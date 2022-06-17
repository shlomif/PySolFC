#!/usr/bin/perl

use strict;
use warnings;
use autodie;

use Cwd            ();
use File::Spec     ();
use File::Copy     qw/ copy /;
use File::Path     qw/ mkpath /;
use Getopt::Long   qw/ GetOptions /;
use Env::Path      ();
use Path::Tiny     qw/ path /;
use File::Basename qw/ basename dirname /;

my $bindir     = dirname(__FILE__);
my $abs_bindir = File::Spec->rel2abs($bindir);

# Whether to use prove instead of runprove.
my $use_prove = $ENV{FCS_USE_TEST_RUN} ? 0 : 1;
my $num_jobs  = $ENV{TEST_JOBS};

sub _is_parallized
{
    return ( $use_prove && $num_jobs );
}

sub _calc_prove
{
    return [ 'prove',
        ( defined($num_jobs) ? sprintf( "-j%d", $num_jobs ) : () ) ];
}

my $exit_success;

sub run_tests
{
    my $tests = shift;

    my @cmd = ( ( $use_prove ? @{ _calc_prove() } : 'runprove' ), @$tests );
    if ( $ENV{RUN_TESTS_VERBOSE} )
    {
        print "Running [@cmd]\n";
    }

    if ($use_prove)
    {
        # Workaround for Windows spawning-SNAFU.
        my $exit_code = system(@cmd);
        exit( $exit_success ? 0 : $exit_code ? (-1) : 0 );
    }
    else
    {
        require Test::Run::CmdLine::Prove;

        my $p = Test::Run::CmdLine::Prove->create(
            {
                'args'         => [@$tests],
                'env_switches' => $ENV{'PROVE_SWITCHES'},
            }
        );
        exit( !$p->run() );
    }
}

my $tests_glob   = "*.{t.exe,py,t}";
my $exclude_re_s = "__init__";

my @execute;
GetOptions(
    '--exclude-re=s' => \$exclude_re_s,
    '--execute|e=s'  => \@execute,
    '--exit0!'       => \$exit_success,
    '--glob=s'       => \$tests_glob,
    '--prove!'       => \$use_prove,
    '--jobs|j=n'     => \$num_jobs,
) or die "Wrong opts - $!";

sub myglob
{
    return glob( shift . "/$tests_glob" );
}

{
    my $fcs_path = Cwd::getcwd();
    local $ENV{FCS_PATH}     = $fcs_path;
    local $ENV{FCS_SRC_PATH} = $abs_bindir;

    local $ENV{FREECELL_SOLVER_QUIET} = 1;
    Env::Path->PATH->Prepend(
        File::Spec->catdir( Cwd::getcwd(), "board_gen" ),
        File::Spec->catdir( $abs_bindir,   "t", "scripts" ),
    );

    my $IS_WIN = ( $^O eq "MSWin32" );
    Env::Path->CPATH->Prepend( $abs_bindir, );

    Env::Path->LD_LIBRARY_PATH->Prepend($fcs_path);
    if ($IS_WIN)
    {
        # For the shared objects.
        Env::Path->PATH->Append($fcs_path);
    }

    my $foo_lib_dir = File::Spec->catdir( $abs_bindir, "tests", "lib" );
    foreach my $add_lib ( Env::Path->PERL5LIB(), Env::Path->PYTHONPATH() )
    {
        $add_lib->Append($foo_lib_dir);
        $add_lib->Append($abs_bindir);
    }

    my $get_config_fn = sub {
        my $basename = shift;

        return File::Spec->rel2abs(
            File::Spec->catdir( $bindir, "tests", "config", $basename ), );
    };

    local $ENV{HARNESS_ALT_INTRP_FILE} = $get_config_fn->(
        $IS_WIN
        ? "alternate-interpreters--mswin.yml"
        : "alternate-interpreters.yml"
    );

    local $ENV{HARNESS_TRIM_FNS} = 'keep:1';

    local $ENV{HARNESS_PLUGINS} = join(
        ' ', qw(
            BreakOnFailure ColorSummary ColorFileVerdicts AlternateInterpreters
            TrimDisplayedFilenames
        )
    );

    my $is_ninja = ( -e "build.ninja" );
    my $MAKE     = $IS_WIN ? 'gmake' : 'make';
    if ($is_ninja)
    {
        system( "ninja", "pretest" );
    }
    else
    {
        if ( system( $MAKE, "-s", "pretest" ) )
        {
            die "$MAKE failed";
        }
    }

    if ( !$is_ninja )
    {
        if ( system( $MAKE, "-s" ) )
        {
            die "$MAKE failed";
        }
    }

    my @tests =
        sort { ( basename($a) cmp basename($b) ) || ( $a cmp $b ) }
        ( myglob("$abs_bindir/tests/*") );

    if ($IS_WIN)
    {
        @tests = grep { not( /pysolgtk/i or /import_v2/i ) } @tests;
    }

    if ( defined($exclude_re_s) )
    {
        my $re = qr/$exclude_re_s/ms;
        @tests = grep { basename($_) !~ $re } @tests;
    }

    local $ENV{FCS_TEST_TAGS} = $ENV{FCS_TEST_TAGS} // '';
    print STDERR "FCS_PATH = $ENV{FCS_PATH}\n";
    print STDERR "FCS_SRC_PATH = $ENV{FCS_SRC_PATH}\n";
    print STDERR "FCS_TEST_TAGS = <$ENV{FCS_TEST_TAGS}>\n";
    if ( $ENV{FCS_TEST_SHELL} )
    {
        system("bash");
    }
    elsif (@execute)
    {
        system(@execute);
    }
    else
    {
        local @INC = ( Env::Path->PERL5LIB->List, @INC );
        run_tests( \@tests );
    }
}

__END__

=head1 COPYRIGHT AND LICENSE

This file is part of Freecell Solver. It is subject to the license terms in
the COPYING.txt file found in the top-level directory of this distribution
and at http://fc-solve.shlomifish.org/docs/distro/COPYING.html . No part of
Freecell Solver, including this file, may be copied, modified, propagated,
or distributed except according to the terms contained in the COPYING file.

Copyright (c) 2000 Shlomi Fish

=cut
