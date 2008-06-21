#!/usr/bin/perl -w

#############################################################################
# Script      : migratetmpl.pl
# Description : Read template files and reformate them as source code
#               comments.
#############################################################################

use strict;
use Getopt::Long;

# Options

# name of documentation module
my $MODULE;
my $TMPL_DIR;
my $SRC_DIR;
my $PRINT_HELP;

my %optctl = ('module' => \$MODULE,
	      'tmpl-dir' => \$TMPL_DIR,
	      'source-dir' => \$SRC_DIR,
	      'help' => \$PRINT_HELP);
GetOptions(\%optctl, "module=s", "tmpl-dir:s", "source-dir:s", "help");

if (!$MODULE) {
    $PRINT_HELP = 1;
}

if ($PRINT_HELP) {
    print <<EOF;
migratetmpl.pl

--module=MODULE_NAME Name of the doc module being parsed
--tmpl-dir=DIRNAME   Directory in which template files may be found
--source-dir=DIRNAME Directory where to put the generated sources
--help               Print this help
EOF
    exit 0;
}


my $ROOT_DIR = ".";

# All the files are read from subdirectories beneath here.
$TMPL_DIR = $TMPL_DIR ? $TMPL_DIR : "$ROOT_DIR/tmpl";
$SRC_DIR = $SRC_DIR ? $SRC_DIR : "$ROOT_DIR/src";

# These global hashes store the existing documentation.
my %SymbolDocs;
my %SymbolTypes;
my %SymbolParams;
# These global hashes store declaration info keyed on a symbol name.
my %Deprecated;
my %Since;
my %StabilityLevel;


# Create the src output directory if it doens't exist.
if (! -e $SRC_DIR) {
    mkdir ("$SRC_DIR", 0777)
	|| die "Can't create directory: $SRC_DIR";
}

# now process the files
&Convert ("$ROOT_DIR/$MODULE-sections.txt");


#############################################################################
# Function    : Convert
# Description : Parse the section file and convert each template back to source
#               comments.
# Arguments   : $file - the section file that lists all templates
#############################################################################
sub Convert {
    my ($file) = @_;

    #print "Reading: $file\n";
    open (INPUT, $file)
	|| die "Can't open $file: $!";

    my $filename = "";

    while (<INPUT>) {
	if (m/^#/) {
	    next;
	} elsif (m/^<FILE>(.*)<\/FILE>/) {
            $filename = $1;
            if (&ReadTemplateFile ("$TMPL_DIR/$filename")) {
               &OutputSourceFile ("$SRC_DIR/$filename",$filename);
            }
        }
    }
    close (INPUT);
}


#############################################################################
# Function    : ReadTemplateFile
# Description : This reads in the manually-edited documentation file
#		corresponding to the file currently being created, so we can
#		insert the documentation at the appropriate places.
#		It outputs %SymbolTypes, %SymbolDocs and %SymbolParams, which
#		is a hash of arrays.
#		NOTE: This function is duplicated in gtkdoc-mktmpl (but
#		slightly different).
# Arguments   : $docsfile - the template file to read in.
#############################################################################
sub ReadTemplateFile {
    my ($docsfile) = @_;

    my $template = "$docsfile.sgml";
    if (! -f $template) {
	#print "File doesn't exist: $template\n";
	return 0;
    }
    #print "Reading $template\n";

    # start with empty hashes, we merge the source comment for each file
    # afterwards
    %SymbolDocs = ();
    %SymbolTypes = ();
    %SymbolParams = ();

    my $current_type = "";	# Type of symbol being read.
    my $current_symbol = "";	# Name of symbol being read.
    my $symbol_doc = "";		# Description of symbol being read.
    my @params;			# Parameter names and descriptions of current
				#   function/macro/function typedef.
    my $current_param = -1;	# Index of parameter currently being read.
				#   Note that the param array contains pairs
				#   of param name & description.
    my $in_unused_params = 0;	# True if we are reading in the unused params.
    my $in_deprecated = 0;
    my $in_since = 0;
    my $in_stability = 0;

    open (DOCS, "$template")
	|| die "Can't open $template: $!";
    while (<DOCS>) {
	if (m/^<!-- ##### ([A-Z_]+) (\S+) ##### -->/) {
	    my $type = $1;
	    my $symbol = $2;
	    if ($symbol eq "Title"
		|| $symbol eq "Short_Description"
		|| $symbol eq "Long_Description"
		|| $symbol eq "See_Also"
		|| $symbol eq "Stability_Level"
		|| $symbol eq "Include") {

		$symbol = $docsfile . ":" . $symbol;
	    }

	    #print "Found symbol: $symbol\n";

	    # Store previous symbol, but remove any trailing blank lines.
	    if ($current_symbol ne "") {
		$symbol_doc =~ s/\s+$//;
		$SymbolTypes{$current_symbol} = $current_type;
		$SymbolDocs{$current_symbol} = $symbol_doc;

		# Check that the stability level is valid.
		if ($StabilityLevel{$current_symbol}) {
		    $StabilityLevel{$current_symbol} = &ParseStabilityLevel($StabilityLevel{$current_symbol}, $template, $., "Stability level for $current_symbol");
		}

		if ($current_param >= 0) {
		    $SymbolParams{$current_symbol} = [ @params ];
		} else {
		    # Delete any existing params in case we are overriding a
		    # previously read template.
		    delete $SymbolParams{$current_symbol};
		}
	    }
	    $current_type = $type;
	    $current_symbol = $symbol;
	    $current_param = -1;
	    $in_unused_params = 0;
	    $in_deprecated = 0;
	    $in_since = 0;
	    $in_stability = 0;
	    $symbol_doc = "";
	    @params = ();

	} elsif (m/^<!-- # Unused Parameters # -->/) {
	    #print "DEBUG: Found unused parameters\n";
	    $in_unused_params = 1;
	    next;

	} elsif ($in_unused_params) {
	    #print "DEBUG: Skipping unused param: $_";
	    next;

	} else {
	    # Check if param found. Need to handle "..." and "format...".
	    if (s/^\@([\w\.]+):\040?//) {
		my $param_name = $1;
		# Allow variations of 'Returns'
		if ($param_name =~ m/^[Rr]eturns?$/) {
		    $param_name = "Returns";
		}
		#print "Found param for symbol $current_symbol : '$param_name'= '$_'\n";

		if ($param_name eq "Deprecated") {
		    $in_deprecated = 1;
		    $Deprecated{$current_symbol} = $_;
		} elsif ($param_name eq "Since") {
		    $in_since = 1;
		    $Since{$current_symbol} = $_;
		} elsif ($param_name eq "Stability") {
		    $in_stability = 1;
		    $StabilityLevel{$current_symbol} = $_;
		} else {
		    push (@params, $param_name);
		    push (@params, $_);
		    $current_param += 2;
		}
	    } else {
	        if ($in_deprecated) {
		    $Deprecated{$current_symbol} .= $_;
		} elsif ($in_since) {
		    $Since{$current_symbol} .= $_;
		} elsif ($in_stability) {
		    $StabilityLevel{$current_symbol} .= $_;
		} elsif ($current_param >= 0) {
		    $params[$current_param] .= $_;
		} else {
		    $symbol_doc .= $_;
		}
	    }
	}
    }

    # Remember to finish the current symbol doccs.
    if ($current_symbol ne "") {
	$symbol_doc =~ s/\s+$//;
	$SymbolTypes{$current_symbol} = $current_type;
	$SymbolDocs{$current_symbol} = $symbol_doc;

	# Check that the stability level is valid.
	if ($StabilityLevel{$current_symbol}) {
	    $StabilityLevel{$current_symbol} = &ParseStabilityLevel($StabilityLevel{$current_symbol}, $template, $., "Stability level for $current_symbol");
	}

	if ($current_param >= 0) {
	    $SymbolParams{$current_symbol} = [ @params ];
	} else {
	    # Delete any existing params in case we are overriding a
	    # previously read template.
	    delete $SymbolParams{$current_symbol};
	}
    }

    close (DOCS);
    return 1;
}

#############################################################################
# Function    : OutputSourceFile
# Description : Format the source comments for one file.
# Arguments   : $docsfile -  the basename for the output file
#               $file - base filename
#############################################################################
sub OutputSourceFile {
    my ($docsfile,$file) = @_;

    my $source = "$docsfile.c";

    open (OUTPUT, ">$source")
        || die "Can't create $source";
    
    # output section docs
    my ($title, $short_desc, $long_desc, $see_also, $stability);

    if (defined ($SymbolDocs{"$TMPL_DIR/$file:Title"})) {
        $title = $SymbolDocs{"$TMPL_DIR/$file:Title"};
        delete $SymbolDocs{"$TMPL_DIR/$file:Title"};
    }
    if (defined ($SymbolDocs{"$TMPL_DIR/$file:Short_Description"})) {
        $short_desc = $SymbolDocs{"$TMPL_DIR/$file:Short_Description"};
        delete $SymbolDocs{"$TMPL_DIR/$file:Short_Description"};
    }
    if (defined ($SymbolDocs{"$TMPL_DIR/$file:Long_Description"})) {
        $long_desc = $SymbolDocs{"$TMPL_DIR/$file:Long_Description"};
        $long_desc = &ConvertNewlines ($long_desc);
        $long_desc = &ConvertComments ($long_desc);
        delete $SymbolDocs{"$TMPL_DIR/$file:Long_Description"};
    }
    if (defined ($SymbolDocs{"$TMPL_DIR/$file:See_Also"})) {
        $see_also = $SymbolDocs{"$TMPL_DIR/$file:See_Also"};
        $see_also = &ConvertNewlines ($see_also);
        delete $SymbolDocs{"$TMPL_DIR/$file:See_Also"};
    }
    if (defined ($SymbolDocs{"$TMPL_DIR/$file:Stability_Level"})) {
        $stability = $SymbolDocs{"$TMPL_DIR/$file:Stability_Level"};
        delete $SymbolDocs{"$TMPL_DIR/$file:Stability_Level"};
    }

    print (OUTPUT <<EOF);
/**
 * SECTION:$file
EOF
    if (defined($short_desc) && ($short_desc ne "")) {
        print (OUTPUT " * \@Short_description: $short_desc\n");
    }
    if (defined($title) && ($title ne "")) {
        print (OUTPUT " * \@Title: $title\n");
    }
    if (defined($see_also) && ($see_also ne "")) {
        my $line;
        my $first="\@See_also:";
        for $line (split (/\n/, $see_also)) {
            print (OUTPUT " * $first$line\n");
            $first="";
        }
    }
    if (defined($stability) && ($stability ne "")) {
        print (OUTPUT " * \@Stability: $stability\n");
    }
    if (defined($long_desc) && ($long_desc ne "")) {
        my $line;
        print (OUTPUT " * \n");
        for $line (split (/\n/, $long_desc)) {
            print (OUTPUT " * $line\n");
        }
    }
    print (OUTPUT <<EOF);
 */


EOF

    # output symbol docs
    my $symbol;
    foreach $symbol (keys (%SymbolDocs)) {
        print (OUTPUT &GetSymbolDoc ($symbol));
    }

    close (OUTPUT);
}

#############################################################################
# Function    : GetSymbolDoc
# Description : Format the docs for one symbol
# Arguments   : $symbol -  the symbol
#############################################################################
sub GetSymbolDoc {
    my ($symbol) = @_;
    
    my $str;
    my ($params, $long_desc, $stability, $deprecated, $since, $returns);

    if (defined ($SymbolParams{$symbol})) {
        $params = $SymbolParams{$symbol}
    }
    if (defined ($StabilityLevel{$symbol})) {
        $stability = $StabilityLevel{$symbol};
    }
    if (defined ($Deprecated{$symbol})) {
        $deprecated = $Deprecated{$symbol};
    }
    if (defined ($Since{$symbol})) {
        ($since, undef) = split (/\n/,$Since{$symbol});
    }
    $long_desc = $SymbolDocs{$symbol};
    $long_desc = &ConvertNewlines ($long_desc);
    $long_desc = &ConvertComments ($long_desc);
    
    $str=<<EOF;
/**
 * $symbol:
EOF
    if (defined($params)) {
        my $j;
        for ($j = 0; $j <= $#$params; $j += 2) {
            my $param_name = $$params[$j];
            my $param_desc = $$params[$j+1];
            my $line;
            my $stripped="";
            
            for $line (split (/\n/, $param_desc)) {
                if ($line ne "") {
                    $line =~ m/\s*(.*)\s*/g;
                    if ($stripped eq "") {
                        $stripped=$stripped."$1\n";
                    } else {
                        $stripped=$stripped." *  $1\n";
                    }
                }
            }
            $param_desc=$stripped;
            
            if ($param_name eq "Varargs") {
                $param_name="...";
            }
            
            if ($param_name eq "Returns") {
                $returns = $param_desc;
                chomp($returns);
            } else {
                $str = $str." * \@$param_name: $param_desc";
            }
        }
    }
    if (defined($long_desc) && ($long_desc ne "")) {
        my $line;
        $str = $str." * \n";
        for $line (split (/\n/, $long_desc)) {
            $str = $str." * $line\n";
        }
    }
    my $spacer=" * \n";
    if (defined($stability) && ($stability ne "")) {
        $str = $str.$spacer." * Stability: $stability\n";
        $spacer="";
    }
    if (defined($deprecated) && ($deprecated ne "")) {
        $str = $str.$spacer." * Deprecated: $deprecated\n";
        $spacer="";
    }
    if (defined($since) && ($since ne "")) {
        $str = $str.$spacer." * Since: $since\n";
        $spacer="";
    }
    if (defined($returns) && ($returns ne "")) {
        $str = $str.$spacer." * Returns: $returns\n";
    }
    $str = $str. <<EOF;
 */


EOF
    return $str;
}

#############################################################################
# Function    : ConvertNewlines
# Description : Convert para tags to newlines
# Arguments   : $istr -  string to convert
#############################################################################
sub ConvertNewlines {
    my ($istr) = @_;
    my ($line,$ostr);
    
    $ostr="";
    for $line (split (/\n/, $istr)) {
        if ($line =~ m/<para>\s*$/) {
            next;
        } elsif ($line =~ m/<\/para>\s*$/) {
            $ostr.="\n";
        } else {
            $ostr.="$line\n";
        }
    }
    
    return $ostr;
}

#############################################################################
# Function    : ConvertComments
# Description : Convert signle line c comments to c++ comments
# Arguments   : $istr -  string to convert
#############################################################################
sub ConvertComments {
    my ($istr) = @_;
    my ($line,$ostr);
    
    $ostr="";
    for $line (split (/\n/, $istr)) {
        if ($line =~ m#/\*.*\*/#) {
            $line =~ s#/\*#//#;
            $line =~ s#\s*\*/##;
        }
        $ostr.="$line\n";
    }
    
    return $ostr;
}
