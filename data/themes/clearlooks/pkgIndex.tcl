# Package index for tile demo pixmap themes.

if {[file isdirectory [file join $dir clearlooks]]} {
    if {[package vsatisfies [package require tile] 0.8.0]} {
        package ifneeded ttk::theme::clearlooks 0.1 \
            [list source [file join $dir clearlooks8.5.tcl]]
    } else {
        package ifneeded tile::theme::clearlooks 0.1 \
            [list source [file join $dir clearlooks8.4.tcl]]
    }
}

