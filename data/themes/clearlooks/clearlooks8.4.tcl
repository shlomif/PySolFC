# clearlooks.tcl

namespace eval tile::theme::clearlooks {

    package provide tile::theme::clearlooks 0.1

    variable I
    array set I [tile::LoadImages \
                     [file join [file dirname [info script]] clearlooks] *.gif]
    
    variable colors

    array set colors {
        -frame          "#efebe7"
        -lighter        "#f5f3f0"
        -dark           "#cfcdc8"
        -darker         "#9e9a9e"
        -darkest        "#d4cfca"
        -selectbg       "#7c99ad"
        -selectfg       "#ffffff"
        -disabledfg     "#b5b3ac"
        -entryfocus     "#6f9dc6"
        -tabbg          "#c9c1bc"
        -tabborder      "#b5aca7"
        -troughcolor    "#d7cbbe"
        -troughborder   "#ae9e8e"
        -checklight     "#f5f3f0"
    }


    style theme create clearlooks -parent clam -settings {

        style configure . \
            -borderwidth        1 \
            -background         $colors(-frame) \
            -foreground         black \
            -bordercolor        $colors(-darkest) \
            -darkcolor          $colors(-dark) \
            -lightcolor         $colors(-lighter) \
            -troughcolor        $colors(-troughcolor) \
            -selectforeground   $colors(-selectfg) \
            -selectbackground   $colors(-selectbg) \
            -font               TkDefaultFont \
            ;

        style map . \
            -background [list disabled $colors(-frame) \
                             active $colors(-lighter)] \
            -foreground [list disabled $colors(-disabledfg)] \
            -selectbackground [list !focus $colors(-darker)] \
            -selectforeground [list !focus white] \
            ;


#        style configure Frame.border -relief groove

        ## Treeview.
        #
        style element create Treeheading.cell image $I(tree-n) \
            -map [list \
                      selected $I(tree-p) \
                      disabled $I(tree-d) \
                      pressed $I(tree-p) \
                      active $I(tree-h) \
                     ] \
            -border 4 -sticky ew

        #style configure Treeview -fieldbackground white
        style configure Row -background "#efefef"
        style map Row -background [list \
                                       {focus selected} "#71869e" \
                                       selected "#969286" \
                                       alternate white]
        style map Item -foreground [list selected white]
        style map Cell -foreground [list selected white]


        ## Buttons.
        #
        #style configure TButton -padding {10 0} -anchor center
        style configure TButton -padding {5 5} -anchor center -width -9
        style layout TButton {
            Button.button -children {
                Button.focus -children {
                    Button.padding -children {
                        Button.label
                    }
                }
            }
        }

        style element create button image $I(button-n) \
            -map [list \
                      pressed $I(button-p) \
                      {selected active} $I(button-pa) \
                      selected $I(button-p) \
                      active $I(button-a) \
                      disabled $I(button-d) \
                     ] \
            -border 4 -sticky ew


        ## Checkbuttons.
        #
        style element create Checkbutton.indicator image $I(check-nu) \
            -width 24 -sticky w -map [list \
                {disabled selected} $I(check-dc) \
                disabled $I(check-du) \
                {pressed selected} $I(check-pc) \
                pressed $I(check-pu) \
                {active selected} $I(check-ac) \
                active $I(check-au) \
                selected $I(check-nc) ]

        style map TCheckbutton -background [list active $colors(-checklight)]
        style configure TCheckbutton -padding 1


        ## Radiobuttons.
        #
        style element create Radiobutton.indicator image $I(radio-nu) \
            -width 24 -sticky w \
            -map [list \
                      {disabled selected} $I(radio-dc) \
                      disabled $I(radio-du) \
                      {pressed selected} $I(radio-pc) \
                      pressed $I(radio-pu) \
                      {active selected} $I(radio-ac) \
                      active $I(radio-au) \
                      selected $I(radio-nc) ]

        style map TRadiobutton -background [list active $colors(-checklight)]
        style configure TRadiobutton -padding 1


        ## Menubuttons.
        #
        #style configure TMenubutton -relief raised -padding {10 2}
# 	style element create Menubutton.border image $I(toolbutton-n) \
# 	    -map [list \
#                       pressed $I(toolbutton-p) \
#                       selected $I(toolbutton-p) \
#                       active $I(toolbutton-a) \
#                       disabled $I(toolbutton-n)] \
# 	    -border {4 7 4 7} -sticky nsew

        style element create Menubutton.border image $I(button-n) \
            -map [list \
                      selected $I(button-p) \
                      disabled $I(button-d) \
                      active $I(button-a) \
                     ] \
            -border 4 -sticky ew


        ## Toolbar buttons.
        #
        style configure Toolbutton -padding -5 -relief flat
        style configure Toolbutton.label -padding 0 -relief flat

        style element create Toolbutton.border image $I(blank) \
            -map [list \
                      pressed $I(toolbutton-p) \
                      {selected active} $I(toolbutton-pa) \
                      selected $I(toolbutton-p) \
                      active $I(toolbutton-a) \
                      disabled $I(blank)] \
            -border 11 -sticky nsew


        ## Entry widgets.
        #
        style configure TEntry -padding 1 -insertwidth 1 \
            -fieldbackground white

        style map TEntry \
            -fieldbackground [list readonly $colors(-frame)] \
            -bordercolor     [list focus $colors(-selectbg)] \
            -lightcolor      [list focus $colors(-entryfocus)] \
            -darkcolor       [list focus $colors(-entryfocus)] \
            ;


        ## Combobox.
        #
        style configure TCombobox -selectbackground

        style element create Combobox.downarrow image $I(comboarrow-n) \
            -map [list \
                          disabled $I(comboarrow-d) \
                          pressed $I(comboarrow-p) \
                          active $I(comboarrow-a) \
                         ] \
            -border 1 -sticky {}

        style element create Combobox.field image $I(combo-n) \
            -map [list \
                      {readonly disabled} $I(combo-rd) \
                      {readonly pressed} $I(combo-rp) \
                      {readonly focus} $I(combo-rf) \
                      readonly $I(combo-rn)
                     ] \
            -border 4 -sticky ew


        ## Notebooks.
        #
#         style element create tab image $I(tab-a) -border {2 2 2 0} \
#             -map [list selected $I(tab-n)]

        style configure TNotebook.Tab -padding {6 2 6 2}
        style map TNotebook.Tab \
            -padding [list selected {6 4 6 2}] \
            -background [list selected $colors(-frame) {} $colors(-tabbg)] \
            -lightcolor [list selected $colors(-lighter) {} $colors(-dark)] \
            -bordercolor [list selected $colors(-darkest) {} $colors(-tabborder)] \
            ;

        ## Labelframes.
        #
        style configure TLabelframe -borderwidth 2 -relief groove


        ## Scrollbars.
        #
        style layout Vertical.TScrollbar {
            Scrollbar.trough -sticky ns -children {
                Scrollbar.uparrow -side top
                Scrollbar.downarrow -side bottom
                Vertical.Scrollbar.thumb -side top -expand true -sticky ns
            }
        }

        style layout Horizontal.TScrollbar {
            Scrollbar.trough -sticky we -children {
                Scrollbar.leftarrow -side left
                Scrollbar.rightarrow -side right
                Horizontal.Scrollbar.thumb -side left -expand true -sticky we
            }
        }

        style element create Horizontal.Scrollbar.thumb image $I(sbthumb-hn) \
            -map [list \
                      disabled $I(sbthumb-hd) \
                      pressed $I(sbthumb-ha) \
                      active $I(sbthumb-ha)] \
            -border 3

        style element create Vertical.Scrollbar.thumb image $I(sbthumb-vn) \
            -map [list \
                      disabled $I(sbthumb-vd) \
                      pressed $I(sbthumb-va) \
                      active $I(sbthumb-va)] \
            -border 3

        foreach dir {up down left right} {
            style element create ${dir}arrow image $I(arrow${dir}-n) \
                -map [list \
                          disabled $I(arrow${dir}-d) \
                          pressed $I(arrow${dir}-p) \
                          active $I(arrow${dir}-a)] \
                -border 1 -sticky {}
        }

        style configure TScrollbar -bordercolor $colors(-troughborder)


        ## Scales.
        #
        style element create Scale.slider image $I(scale-hn) \
            -map [list \
                      disabled $I(scale-hd) \
                      active $I(scale-ha) \
                     ]

        style element create Scale.trough image $I(scaletrough-h) \
            -border 2 -sticky ew -padding 0

        style element create Vertical.Scale.slider image $I(scale-vn) \
            -map [list \
                      disabled $I(scale-vd) \
                      active $I(scale-va) \
                     ]
        style element create Vertical.Scale.trough image $I(scaletrough-v) \
            -border 2 -sticky ns -padding 0

        style configure TScale -bordercolor $colors(-troughborder)


        ## Progressbar.
        #
        style element create Horizontal.Progressbar.pbar image $I(progress-h) \
            -border {2 2 1 1}
        style element create Vertical.Progressbar.pbar image $I(progress-v) \
            -border {2 2 1 1}

        style configure TProgressbar -bordercolor $colors(-troughborder)


        ## Statusbar parts.
        #
        style element create sizegrip image $I(sizegrip)


        ## Paned window parts.
        #
#         style element create hsash image $I(hseparator-n) -border {2 0} \
#             -map [list {active !disabled} $I(hseparator-a)]
#         style element create vsash image $I(vseparator-n) -border {0 2} \
#             -map [list {active !disabled} $I(vseparator-a)]

        style configure Sash -sashthickness 6 -gripcount 16


        ## Separator.
        #
        #style element create separator image $I(sep-h)
        #style element create hseparator image $I(sep-h)
        #style element create vseparator image $I(sep-v)

    }
}

