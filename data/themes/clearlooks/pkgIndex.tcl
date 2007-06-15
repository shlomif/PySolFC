# Package index for tile demo pixmap themes.

if {[file isdirectory [file join $dir clearlooks]]} {
    package ifneeded tile::theme::clearlooks 0.1 \
        [list source [file join $dir clearlooks.tcl]]
}

