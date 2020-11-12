#!/usr/bin/perl

use strict;
use warnings;

use Test::More;

eval "use Test::TrailingSpace";
if ($@)
{
    plan skip_all => "Test::TrailingSpace required for trailing space test.";
}
else
{
    plan tests => 1;
}

my $finder = Test::TrailingSpace->new(
    {
        abs_path_prune_re => qr# kcardgame[/\\](?:b|build-kpat)(?:\z|/|\\) #msx,
        root              => '.',
        filename_regex    =>
qr/(?:(?:\.(?:bash|sh|t|pm|pl|PL|yml|json|arc|vim|html|py|tcl|xhtml))|README(?:[\.\w]*)|Changes|LICENSE|MANIFEST(?:\.in)?|AUTHORS|COPYING)\z/,
    },
);

# TEST
$finder->no_trailing_space("No trailing space was found.");
