#!/usr/bin/perl

use strict;
use warnings;

use Test::More tests => 1;
use Test::Differences qw( eq_or_diff );

use String::ShellQuote qw/ shell_quote /;

# my $cmd = shell_quote( 'flake8', '.' );
my $cmd = shell_quote( 'flake8', glob('./pysollib/a*.py') );

# TEST
eq_or_diff( scalar(`$cmd`), '', "flake8 is happy with the code." );

__END__

=head1 COPYRIGHT AND LICENSE

This file is part of Freecell Solver. It is subject to the license terms in
the COPYING.txt file found in the top-level directory of this distribution
and at http://fc-solve.shlomifish.org/docs/distro/COPYING.html . No part of
Freecell Solver, including this file, may be copied, modified, propagated,
or distributed except according to the terms contained in the COPYING file.

Copyright (c) 2016 Shlomi Fish

=cut

