#!/usr/bin/perl -w

#############################################################################
# Function    : CreateValidSGMLID
# Description : Creates a valid SGML 'id' from the given string.
#		NOTE: SGML ids are case-insensitive, so we have a few special
#		      cases to avoid clashes of ids.
# Arguments   : $id - the string to be converted into a valid SGML id.
#############################################################################

sub CreateValidSGMLID {
    my ($id) = $_[0];

    # Append -CAPS to all all-caps identifiers

    # Special case, '_' would end up as '' so we use 'gettext-macro' instead.
    if ($id eq "_") { return "gettext-macro"; }

    if ($id !~ /[a-z]/) { $id .= "-CAPS" };

    $id =~ s/[_ ]/-/g;
    $id =~ s/[,\.]//g;
    $id =~ s/^-*//;
    $id =~ s/::/-/g;

    return $id;
}

$BASEDIR=shift @ARGV;

print <<EOT;
<table cellspacing="0" cellpadding="2">
  <tr><th align="left">Module</th><th style="padding-left: 0.5em; padding-right: 0.5em" colspan="4">Documented</th></tr>
EOT

my $row = 0; 
while (@ARGV) {
    my $percentage;
    my $documented;
    my $undocumented;
    my @undocumented_symbols;
    
    my $module_name = shift @ARGV;
    my $file = shift @ARGV;
    my $indexfile = shift @ARGV;

    open DOCUMENTED, "<$file" or die "Cannot open $file: $!\n";

    while (<DOCUMENTED>) {
	if      (/(\d+)% (function|symbol) docs coverage/) {
	    $percentage = $1;
	} elsif (/(\d+) (function|symbol)s documented/) {
	    $documented = $1;
	} elsif (/(\d+) not documented/) {
	    $undocumented = $1;
	} elsif (/^\s*(\w+)\s*$/) {
	    push @undocumented_symbols, $1;
	}
    }

    close DOCUMENTED;

    my $complete = defined $percentage && defined $documented && defined $undocumented;
    if (!$complete) {
	die "Cannot parse documentation status file $file\n";
    }

    my $total = $documented + $undocumented;

    my $directory;
    ($directory = $indexfile) =~ s@/[^/]*$@@;
    
    $bgcolor = ($row % 2 == 0) ? "#f7ebd3" : "#fffcf4";

    print <<EOT;
  <tr bgcolor="$bgcolor">
    <td><a href="$indexfile">$module_name</a></td>
    <td align="right" style="padding-left: 0.5em">$documented</td>
	<td>/</td><td>$total</td>
    <td style="padding-right: 0.5em">($percentage%)</td>
EOT
    if ($undocumented != 0) {
	print <<EOT;
    <td><a href="$directory/undocumented.html"><small>[missing]<small></a></td>
EOT
    }
    print <<EOT;
  </tr>
EOT
    
    #
    # Print an index of undocumented symbols for this module
    #

    @undocumented_symbols = sort { uc($a) cmp uc($b) } @undocumented_symbols;

    my $base = "$BASEDIR/$directory";

    open INDEX_SGML, "<$base/index.sgml" or die "Cannot open $base/index.sgml: $!\n";

    my %index_symbols;
    
    while (<INDEX_SGML>) {
	if (/<ANCHOR\s+id="([^"]+)"\s+href="([^"]+)">/) {
	    $index_symbols{$1} = $2;
	}
    }

    close INDEX_SGML;

    open UNDOC_OUT, ">$base/undocumented.html" or die "Cannot open $base/undocumented.html: $!\n";
    print UNDOC_OUT <<EOT;
<html>
<head>
<title>Undocumented functions in $module_name</title>
</head>
<body bgcolor="#ffffff">
<table>
  <tr>
EOT
    my $i = 0;
    for $symbol (@undocumented_symbols) {
	my $id = CreateValidSGMLID($symbol);

	my $output;
	if (exists $index_symbols{$id}) {
	    my $href;
	    
	    ($href = $index_symbols{$id}) =~ s@.*/(.*)$@$1@; 
	    
	    $output = qq(<a href="$href">$symbol</a>);
	} else {
	    $output = qq($symbol);
	}
	print UNDOC_OUT "    <td>$output</td>\n";
	if ($i % 3 == 2) {
	    print UNDOC_OUT "  </tr><tr>\n";
	}
    
        $i++;
    }

    print UNDOC_OUT <<EOT;
  </tr>
</table>
</body>
</html>
EOT
    close UNDOC_OUT;
    $row++;
}

print <<EOT;
</table>
EOT
