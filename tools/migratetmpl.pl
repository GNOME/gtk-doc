#!/usr/bin/perl -w

#############################################################################
# Script      : migratetmpl.pl
# Description : Read template files and reformate them as source code
#               comments.
#               Run from doc dir.
# Example     : cd glib/docs/reference/glib
#               migratetmpl.pl --module=glib --source-dir=../../../glib
#               cd glib/docs/reference/gmodule
#               migratetmpl.pl --module=glib --source-dir=../../../glib
#               ...
# Todo        : - remove docs from tmpl files if there are comments in the src
#               - allow running for only 1 tmpl file (= one section)
#############################################################################

use strict;
use Getopt::Long;
use Parse::ExuberantCTags;

# Options

# name of documentation module
my $MODULE;
my $TMPL_DIR;
my $EXTRA_SRC_DIR;
my $SRC_DIR;
my $PRINT_HELP;

my %optctl = ('module' => \$MODULE,
	      'tmpl-dir' => \$TMPL_DIR,
	      'extra-source-dir' => \$EXTRA_SRC_DIR,
	      'source-dir' => \$SRC_DIR,
	      'help' => \$PRINT_HELP);
GetOptions(\%optctl, "module=s", "tmpl-dir:s", "source-dir:s", "help");

if (!$MODULE) {
    $PRINT_HELP = 1;
}

if ($PRINT_HELP) {
    print <<EOF;
migratetmpl.pl

--module=MODULE_NAME       Name of the doc module being parsed
--tmpl-dir=DIRNAME         Directory in which template files may be found
--extra-source-dir=DIRNAME Directory where to put the generated sources
--source-dir=DIRNAME       Directory of existing sources
--help                     Print this help
EOF
    exit 0;
}


my $ROOT_DIR = ".";
if (! -e "$ROOT_DIR/$MODULE-sections.txt") {
    die "No $ROOT_DIR/$MODULE-sections.txt file found, please run this from doc-dir";
}

# All the files are read from subdirectories beneath here.
$TMPL_DIR = $TMPL_DIR ? $TMPL_DIR : "$ROOT_DIR/tmpl";
$EXTRA_SRC_DIR = $EXTRA_SRC_DIR ? $EXTRA_SRC_DIR : "$ROOT_DIR/src";

# These global hashes store the existing documentation.
my %SymbolDocs;
my %SymbolTypes;
my %SymbolParams;
# These global hashes store declaration info keyed on a symbol name.
my %Deprecated;
my %Since;
my %StabilityLevel;

# build and read tags
my $tags;
if (-e $SRC_DIR) {
    `cd $SRC_DIR; make ctags`;
    $tags = Parse::ExuberantCTags->new("$SRC_DIR/tags");
}

# Create the src output directory if it doens't exist.
if (! -e $EXTRA_SRC_DIR) {
    mkdir ("$EXTRA_SRC_DIR", 0777)
	|| die "Can't create directory: $EXTRA_SRC_DIR";
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
               &OutputSourceFile ("$EXTRA_SRC_DIR/$filename",$filename);
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
        $long_desc = &ConvertMarkup ($long_desc);
        $long_desc = &ConvertComments ($long_desc);
        delete $SymbolDocs{"$TMPL_DIR/$file:Long_Description"};
    }
    if (defined ($SymbolDocs{"$TMPL_DIR/$file:See_Also"})) {
        $see_also = $SymbolDocs{"$TMPL_DIR/$file:See_Also"};
        $see_also = &ConvertMarkup ($see_also);
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
    my $docblob;
    my $merged;
    foreach $symbol (keys (%SymbolDocs)) {
        $docblob=&GetSymbolDoc ($symbol);
        next if (!defined $docblob);

        $merged=0;
        # if we have tags, check if we find the symbol location
        if (defined $tags) {
            my $tag = $tags->findTag($symbol, ignore_case => 0, partial => 0);
            if (defined $tag) {
                my $srcline;
                my $srcfile=$tag->{file};

                if (defined $tag->{addressLineNumber}) {
                    $srcline=$tag->{addressLineNumber}
                }
                if (-e "$SRC_DIR/$srcfile") {
                    my @lines;
                    my $line;

                    my $source = "$SRC_DIR/$srcfile";

                    open (SRC, "$source");
                    @lines = <SRC>;
                    close (SRC);

                    if (!defined $srcline) {
                        my $re  = $tag->{addressPattern};
                        $re =~ m#^/(.*)/$#;
                        $re = $1;
                        $re =~ s/([*()])/\\$1/g;
                        #$re = qr/$re/xo;

                        for (0..$#lines) {
                            if ($lines[$_] =~ $re) {
                                $srcline=$_+1;
                                last;
                            }
                        }
                        if (!defined $srcline) {
                            print "no line found for : $symbol in $srcfile using regexp: ", $re, "\n";
                        }
                    }

                    if (defined $srcline) {
                        my $offset = $srcline-1;
                        
                        if ($SymbolTypes{$symbol} eq "FUNCTION") {
                            # go one up to skip return type
                            # FIXME: check if the $symbol starts at the begin of the line
                            # if ($lines[$srcline] =~ m/^$symbol/)
                            $offset -= 1;
                        }
                        
                        splice @lines,$offset,$#lines-$offset,($docblob,@lines[$offset..($#lines+-1)]);

                        # patch file and overwrite
                        open (SRC, ">$source");
                        print SRC @lines;
                        close (SRC);
                        $merged=1;
                        # rebuild and reread ctags
                        `cd $SRC_DIR; make ctags`;
                        $tags = Parse::ExuberantCTags->new("$SRC_DIR/tags");
                    }

                }
                else {
                    print "no source found for : $symbol\n";
                }
            }
            else {
                print "no tag found for : $symbol\n";
            }
        }
        if ($merged == 0) {
          print (OUTPUT $docblob."\n\n");
        }
        undef $docblob;
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
    my $is_empty =1;

    if (defined ($SymbolParams{$symbol})) {
        $params = $SymbolParams{$symbol}
    }
    if (defined ($StabilityLevel{$symbol})) {
        $stability = $StabilityLevel{$symbol};
    }
    if (defined ($Deprecated{$symbol})) {
        $deprecated = $Deprecated{$symbol};
        $deprecated = &FormatMultiline ($deprecated);
    }
    if (defined ($Since{$symbol})) {
        ($since, undef) = split (/\n/,$Since{$symbol});
    }
    $long_desc = $SymbolDocs{$symbol};
    $long_desc = &ConvertMarkup ($long_desc);
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
            $param_desc = &FormatMultiline ($param_desc);

            if ($param_desc ne "\n") {
                $is_empty = 0;
            }

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
        $is_empty = 0;
    }
    my $spacer=" * \n";
    if (defined($stability) && ($stability ne "")) {
        $str = $str.$spacer." * Stability: $stability\n";
        $spacer="";
        $is_empty = 0;
    }
    if (defined($deprecated) && ($deprecated ne "")) {
        $str = $str.$spacer." * Deprecated: $deprecated";
        $spacer="";
        $is_empty = 0;
    }
    if (defined($since) && ($since ne "")) {
        $str = $str.$spacer." * Since: $since\n";
        $spacer="";
        $is_empty = 0;
    }
    if (defined($returns) && ($returns ne "")) {
        $str = $str.$spacer." * Returns: $returns\n";
        $is_empty = 0;
    }
    $str = $str. <<EOF;
 */
EOF
    if($is_empty == 1) {
        #print "empty docs for $symbol\n";
        return;
    }
    return $str;
}

#############################################################################
# Function    : ConvertMarkup
# Description : Convert para tags to newlines and character entities back 
# Arguments   : $istr -  string to convert
#############################################################################
sub ConvertMarkup {
    my ($istr) = @_;
    my ($line,$ostr);
    
    $ostr="";
    for $line (split (/\n/, $istr)) {
        if ($line =~ m/\s*<para>\s*$/) {
            next;
        } elsif ($line =~ m/\s*<\/para>\s*$/) {
            $ostr.="\n";
        } else {
            # convert character entities back.
            $line =~ s/&amp;/&/g;
            $line =~ s/&num;/#/g;
            $line =~ s/&lt;/</g;
            $line =~ s/&gt;/>/g;
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
        $line =~ s#/\*#/<!---->\*#;
        $line =~ s#\*/#\*<!---->/#;
        $ostr.="$line\n";
    }
    
    return $ostr;
}

#############################################################################
# Function    : FormatMultiline
# Description : Format multiline text and remove blank lines
# Arguments   : $istr -  string to convert
#############################################################################
sub FormatMultiline {
    my ($istr) = @_;
    my ($line,$ostr);
    
    $ostr="";
    for $line (split (/\n/, $istr)) {
        if ($line ne "") {
            $line =~ m/\s*(.*)\s*/g;
            if ($ostr eq "") {
                $ostr.="$1\n";
            } else {
                $ostr.=" *  $1\n";
            }
        }
    }
    if ($ostr eq "") {
        $ostr="\n";
    }

    return $ostr;
}


