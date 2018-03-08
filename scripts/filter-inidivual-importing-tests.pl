#!/usr/bin/perl

use strict;
use warnings;

use IO::All;
use List::MoreUtils qw(none);

my @m2;
L_LOOP:
foreach my $l ( io("scripts/gen_individual_importing_tests.py")->getlines() )
{
    if ( $l =~ m/^for module_name/ )
    {
        my @ms = $l =~ m{('pysollib\.[^']+')}g;
        @m2 = ( map { $_ =~ s/\A'//r =~ s/\'\z//r =~ tr#.#/#r } @ms );
        last L_LOOP;
    }
}

while ( my $l = <STDIN> )
{
    chomp($l);
    print "$l\n" if none { $l =~ /$_/ } @m2;
}
