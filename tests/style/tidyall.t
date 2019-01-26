#!/usr/bin/perl

use strict;
use warnings;

if ( $ENV{TEST_SKIP_TIDYALL} )
{
    require Test::More;
    Test::More::plan( 'skip_all' =>
            "Skipping perltidy test because FCS_TEST_SKIP_PERLTIDY was set" );
}

use lib './tests/lib';

require MyTidyAll;
