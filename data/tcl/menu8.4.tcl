# this file from tkabber project
# http://www.jabberstudio.org/projects/tkabber/

namespace eval :: {

proc myMenuButtonDown {args} {
    global myMenuFlag myMenuMotion
    eval ::tk::MenuButtonDown $args
    set myMenuFlag 1
}
proc myMenuInvoke {args} {
    global myMenuFlag myMenuMotion
    if {$myMenuFlag || $myMenuMotion} {
	eval ::tk::MenuInvoke $args
    }
    set myMenuFlag 0
    set myMenuMotion 0
}
proc myMenuMotion {args} {
    global myMenuFlag myMenuMotion
    eval ::tk::MenuMotion $args
    set myMenuMotion 1
}
proc myMenuLeave {args} {
    global myMenuFlag myMenuMotion
    eval ::tk::MenuLeave $args
    set myMenuMotion 0
}
bind Menu <Leave> {myMenuLeave %W %X %Y %s}
bind Menu <ButtonPress> {myMenuButtonDown %W}
bind Menu <ButtonRelease> {myMenuInvoke %W 1}
bind Menu <Motion> {myMenuMotion %W %x %y %s}
set myMenuFlag 0
set myMenuMotion 0

# ::tk::MenuNextEntry --
# Activate the next higher or lower entry in the posted menu,
# wrapping around at the ends.  Disabled entries are skipped.
#               
# Arguments:
# menu -                        Menu window that received the keystroke.
# count -                       1 means go to the next lower entry,
#                               -1 means go to the next higher entry.

proc ::tk::MenuNextEntry {menu count} {
    global ::tk::Priv

    if {[$menu index last] eq "none"} {
        return
    }
    set length [expr {[$menu index last]+1}]
    set quitAfter $length
    set active [$menu index active]
    if {$active eq "none"} {
        set i 0
    } else {
        set i [expr {$active + $count}]
    }
    while {1} {
        if {$quitAfter <= 0} {
            # We've tried every entry in the menu.  Either there are
            # none, or they're all disabled.  Just give up.

            return
        }
        while {$i < 0} {
            incr i $length
        }
        while {$i >= $length} {
            incr i -$length
        }
        if {[catch {$menu entrycget $i -state} state] == 0} {
            if {$state ne "disabled"} {
                break
            }
        }
        if {$i == $active} {
            return
        }
        incr i $count
        incr quitAfter -1
    }
    $menu activate $i
    ::tk::GenerateMenuSelect $menu
    if {[$menu type $i] eq "cascade"} {
        set cascade [$menu entrycget $i -menu]
        if {[$menu cget -type] eq "menubar" && $cascade ne ""} {
            # Here we auto-post a cascade.  This is necessary when
            # we traverse left/right in the menubar, but undesirable when
            # we traverse up/down in a menu.
            $menu postcascade $i
            ::tk::MenuFirstEntry $cascade
        }
    }
}

# ::tk::MenuNextMenu --
# This procedure is invoked to handle "left" and "right" traversal
# motions in menus.  It traverses to the next menu in a menu bar,
# or into or out of a cascaded menu.
#   
# Arguments:
# menu -                The menu that received the keyboard
#                       event.
# direction -           Direction in which to move: "left" or "right"

proc ::tk::MenuNextMenu {menu direction} {
    global ::tk::Priv

    # First handle traversals into and out of cascaded menus.

    if {$direction eq "right"} {
        set count 1
        set parent [winfo parent $menu]
        set class [winfo class $parent]
        if {[$menu type active] eq "cascade"} {
            $menu postcascade active
            set m2 [$menu entrycget active -menu]
            if {$m2 ne ""} {
                ::tk::MenuFirstEntry $m2
            }
            return
        } else {
            set parent [winfo parent $menu]
            while {$parent ne "."} {
                if {[winfo class $parent] eq "Menu" && \
                        [$parent cget -type] eq "menubar"} {
                    tk_menuSetFocus $parent
                    ::tk::MenuNextEntry $parent 1
                    return
                }
                set parent [winfo parent $parent]
            }
        }
    } else {
        set count -1
        set m2 [winfo parent $menu]
        if {[winfo class $m2] eq "Menu"} {
            if {[$m2 cget -type] ne "menubar"} {
                $menu activate none
                ::tk::GenerateMenuSelect $menu
                tk_menuSetFocus $m2

                # This code unposts any posted submenu in the parent.
		$m2 postcascade none

                #set tmp [$m2 index active]
                #$m2 activate none
                #$m2 activate $tmp
                return
            }
        }
    }

    # Can't traverse into or out of a cascaded menu.  Go to the next
    # or previous menubutton, if that makes sense.

    set m2 [winfo parent $menu]
    if {[winfo class $m2] eq "Menu"} {
        if {[$m2 cget -type] eq "menubar"} {
            tk_menuSetFocus $m2
            ::tk::MenuNextEntry $m2 -1
            return
        }
    }

    set w $::tk::Priv(postedMb)
    if {$w eq ""} {
        return
    }
    set buttons [winfo children [winfo parent $w]]
    set length [llength $buttons]
    set i [expr {[lsearch -exact $buttons $w] + $count}]
    while {1} {
        while {$i < 0} {
            incr i $length
        }
        while {$i >= $length} {
            incr i -$length
        }
        set mb [lindex $buttons $i]
        if {[winfo class $mb] eq "Menubutton" \
                && [$mb cget -state] ne "disabled" \
                && [$mb cget -menu] ne "" \
                && [[$mb cget -menu] index last] ne "none"} {
            break
        }
        if {$mb eq $w} {
            return
        }
        incr i $count
    }
    ::tk::MbPost $mb
    ::tk::MenuFirstEntry [$mb cget -menu]
}

# ::tk::MenuFirstEntry --
# Given a menu, this procedure finds the first entry that isn't
# disabled or a tear-off or separator, and activates that entry.
# However, if there is already an active entry in the menu (e.g.,
# because of a previous call to ::tk::PostOverPoint) then the active
# entry isn't changed.  This procedure also sets the input focus
# to the menu.
#
# Arguments:
# menu -                Name of the menu window (possibly empty).

proc ::tk::MenuFirstEntry menu {
    if {$menu eq ""} {
        return
    }
    tk_menuSetFocus $menu
    if {[$menu index active] ne "none"} {
        return
    }
    set last [$menu index last]
    if {$last eq "none"} {
        return
    }
    for {set i 0} {$i <= $last} {incr i} {
        if {([catch {set state [$menu entrycget $i -state]}] == 0) \
                && $state ne "disabled"} {
            #~$menu activate $i
            #~::tk::GenerateMenuSelect $menu
            # Only post the cascade if the current menu is a menubar;
            # otherwise, if the first entry of the cascade is a cascade,
            # we can get an annoying cascading effect resulting in a bunch of
            # menus getting posted (bug 676)
            if {[$menu type $i] eq "cascade" && \
                [$menu cget -type] eq "menubar"} {
                set cascade [$menu entrycget $i -menu]
                if {$cascade ne ""} {
                    $menu postcascade $i
                    ::tk::MenuFirstEntry $cascade
                }
            }
            return
        }
    }
}

# ::tk::MenuMotion --
# This procedure is called to handle mouse motion events for menus.
# It does two things.  First, it resets the active element in the
# menu, if the mouse is over the menu.  Second, if a mouse button
# is down, it posts and unposts cascade entries to match the mouse
# position.
#
# Arguments:
# menu -                The menu window.
# x -                   The x position of the mouse.
# y -                   The y position of the mouse.
# state -               Modifier state (tells whether buttons are down).

proc ::tk::MenuMotion {menu x y state} {
    global ::tk::Priv 
    if {$menu eq $::tk::Priv(window)} {
        if {[$menu cget -type] eq "menubar"} {
            if {[info exists ::tk::Priv(focus)] && $menu ne $::tk::Priv(focus)} {
                $menu activate @$x,$y
                ::tk::GenerateMenuSelect $menu
            }   
        } else {
            $menu activate @$x,$y
            ::tk::GenerateMenuSelect $menu
        }
    }
    #debugmsg plugins "MENU: $menu $::tk::Priv(activeMenu) $::tk::Priv(activeItem) $::tk::Priv(focus)"
    if {([$menu cget -type] ne "menubar") || \
	    ([info exist ::tk::Priv(focus)] && ($::tk::Priv(focus) ne "") && ($::tk::Priv(activeItem) != "none"))} {
	myMenuPostCascade $menu
    }
}

# ::tk::MenuButtonDown --
# Handles button presses in menus.  There are a couple of tricky things
# here:
# 1. Change the posted cascade entry (if any) to match the mouse position.
# 2. If there is a posted menubutton, must grab to the menubutton;  this
#    overrrides the implicit grab on button press, so that the menu
#    button can track mouse motions over other menubuttons and change
#    the posted menu.
# 3. If there's no posted menubutton (e.g. because we're a torn-off menu
#    or one of its descendants) must grab to the top-level menu so that
#    we can track mouse motions across the entire menu hierarchy.
#
# Arguments:
# menu -		The menu window.

proc ::tk::MenuButtonDown menu {
    variable ::tk::Priv
    global tcl_platform

    if {![winfo viewable $menu]} {
        return
    }
    $menu postcascade active
    if {$Priv(postedMb) ne "" && [winfo viewable $Priv(postedMb)]} {
	grab -global $Priv(postedMb)
    } else {
	while {[$menu cget -type] eq "normal" \
		&& [winfo class [winfo parent $menu]] eq "Menu" \
		&& [winfo ismapped [winfo parent $menu]]} {
	    set menu [winfo parent $menu]
	}

	if {$Priv(menuBar) eq {}} {
	    set Priv(menuBar) $menu
	    set Priv(cursor) [$menu cget -cursor]
	    $menu configure -cursor arrow
        } else {
            $menu activate none
            #MenuUnpost $menu
        }

	# Don't update grab information if the grab window isn't changing.
	# Otherwise, we'll get an error when we unpost the menus and
	# restore the grab, since the old grab window will not be viewable
	# anymore.

	if {$menu ne [grab current $menu]} {
	    SaveGrabInfo $menu
	}

	# Must re-grab even if the grab window hasn't changed, in order
	# to release the implicit grab from the button press.

	if {[tk windowingsystem] eq "x11"} {
	    grab -global $menu
	}
    }
}                                       

set myPriv(id) ""
set myPriv(delay) 170
set myPriv(activeMenu) ""
set myPriv(activeItem) ""

proc myMenuPostCascade {menu} {
    global myPriv

    if {$myPriv(id) ne ""} {
	if {($myPriv(activeMenu) == $menu) && ($myPriv(activeItem) == [$menu index active])} {
	    return
	} else {
	    after cancel $myPriv(id)
	}
    }
    if {[$menu cget -type] eq "menubar"} {
	$menu postcascade active
    } else {
	set myPriv(activeMenu) $menu
	set myPriv(activeItem) [$menu index active]
	set myPriv(id) [after $myPriv(delay) "$menu postcascade active"]
    }
}

}
