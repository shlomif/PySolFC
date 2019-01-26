package MyCacheModel;

use Moo;

extends('Code::TidyAll::CacheModel');

my $DUMMY_LAST_MOD = 0;

sub _build_cache_value
{
    my ($self) = @_;

    return $self->_sig(
        [ $self->base_sig, $DUMMY_LAST_MOD, $self->file_contents ] );
}

package main;

use Test::Code::TidyAll qw/ tidyall_ok /;

my $KEY = 'TIDYALL_DATA_DIR';
tidyall_ok(
    cache_model_class => 'MyCacheModel',
    ( exists( $ENV{$KEY} ) ? ( data_dir => $ENV{$KEY} ) : () )
);

1;
