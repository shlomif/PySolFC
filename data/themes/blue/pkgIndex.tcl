# Package index for tile demo pixmap themes.

if {[file isdirectory [file join $dir blue]]} {
    if {[package vsatisfies [package require tile] 0.8.0]} {
        package ifneeded ttk::theme::blue 0.7 \
            [list source [file join $dir blue8.5.tcl]]
    } else {
        package ifneeded tile::theme::blue 0.7 \
            [list source [file join $dir blue8.4.tcl]]
    }
}
