# Copyright (C) Schelte Bron.  Freely redistributable.
# http://wiki.tcl.tk/15897

proc ttk::messageBox {args} {
	variable ::ttk::Priv
	set dataName __ttk_messagebox
	set parent .
	foreach {opt val} $args {
		switch -- $opt {
			-parent {
				set parent $val
			}
			default {
				lappend opts $opt $val
			}
		}
	}
	lappend opts -command {set ::ttk::Priv(button)}
	if {$parent eq "."} {
		set win .$dataName
	} else {
		set win $parent.$dataName
	}
	eval [linsert $opts 0 ttk::dialog $win]
	::tk::PlaceWindow $win widget $parent
	::tk::SetFocusGrab $win $win
	vwait ::ttk::Priv(button)
	::tk::RestoreFocusGrab $win $win
	return $Priv(button)
}

interp alias {} ttk_messageBox {} ::ttk::messageBox

namespace eval ::ttk::dialog {}
namespace eval ::ttk::dialog::file {
	variable sort name hidden 1 sepfolders 1 foldersfirst 1
	variable details 0 reverse 0 filetype none
	variable dirlist "" filelist ""
}
namespace eval ::ttk::dialog::image {}

# Images for the configuration menu

image create photo ::ttk::dialog::image::blank16 -height 16 -width 16

image create photo ::ttk::dialog::image::tick16 -data {
R0lGODlhEAAQAMIAAExOTFRSVPz+/AQCBP///////////////yH5BAEKAAQALAAAAAAQABAA
AAM4CAHcvkEAQqu18uqat+4eFoTEwE3eYFLCWK2lelqyChMtbd84+sqX3IXH8pFwrmNPyRI4
n9CoIAEAOw==}

image create photo ::ttk::dialog::image::radio16 -data {
R0lGODlhEAAQAMIAAJyZi////83OxQAAAP///////////////yH5BAEKAAEALAAAAAAQABAA
AAMtGLrc/jCAOaNsAGYn3A5DuHTMFp4KuZjnkGJK6waq8qEvzGlNzQlAn2VILC4SADs=}

# Images for ttk::getOpenFile, ttk::getSaveFile, ttk::getAppendFile

image create photo ::ttk::dialog::image::next -data {
R0lGODlhFgAWAMYAADt1BDpzBFiJKb7ZpGaVOTx2A8HcqbfVm3ShSjt0BDp1BDx3Bb/apYe7
V7DSkIOtWzt0A8Dbpr/apL7ao7zZoXu0RXy0R6bMgo23Zz12CbzZoH+2Sn61SX21R3qzRHiy
QnaxPnOvOnCuNpjFb5e/cUV8ELnXnHiyQXaxP3WwPXCtNm2sMmqqLWaoKIm8WJ3FeEuBGLXV
l2+tNGGlIWanJ2urLWutLmqtK2irJ2SpIl+lHJ/GeFaKIjt1A6jNhU+aB06aBk+cBlKhCFWl
CViqDF6uEmCvFWGtFl2qE3e2Op3HdVWLIjt2BKPLflSjCFipClyvDF6zDWC2Dl+0DYTER5zK
cEqDFjt3A1eoClywDGG3DmW9EGfBEWnCE5XTWZjJZ0R9D6TLfqbPf6nUgazYgq/cg2nDEXPM
GqPfaY7DWj53CTlzBD13Ba7bg3HGH6fecn+0SqbWdmufOjhwBKTPelqNKTNmAk6DHi9dAzdu
A////////////////////////yH5BAEKAH8ALAAAAAAWABYAAAfGgH+Cg4SFhoeIiYgAio0B
Ao2JAQMEBZGGAQYHCAmNCgGgoAsMDQ4PEIoBEasREhMUFRYXGBmSGhsbHB0eHyAhIiMkJYgB
JifHKCkhKissLS4vMIcBMTItMzM0NTY3ODk6Jzs9mD4/QEBBQkNERUZHSElKTJhN50FOT1BR
UlJTVFVXptUDIgRLFi1buHTx8gUMsSZNwogZQ6aMmTNo0qhJtCYUKDZt3LyB0+mSoABk4siZ
Y3JQADp17LR0eQfPzEF5burcKSgQADs=}

image create photo ::ttk::dialog::image::nextbw -data {
R0lGODlhFgAWAOcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0N
DQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8f
HyAgICEhISIiIiMjIyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDEx
MTIyMjMzMzQ0NDU1NTY2Njc3Nzg4ODk5OTo6Ojs7Ozw8PD09PT4+Pj8/P0BAQEFBQUJCQkND
Q0REREVFRUZGRkdHR0hISElJSUpKSktLS0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVV
VVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9fX2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdn
Z2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNzc3R0dHV1dXZ2dnd3d3h4eHl5
eXp6ent7e3x8fH19fX5+fn9/f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeHh4iIiImJiYqKiouL
i4yMjI2NjY6Ojo+Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampubm5ycnJ2d
nZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq+v
r7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8DAwMHB
wcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9DQ0NHR0dLS0tPT
09TU1NXV1dbW1tfX19jY2NnZ2dra2tvb29zc3N3d3d7e3t/f3+Dg4OHh4eLi4uPj4+Tk5OXl
5ebm5ufn5+jo6Onp6erq6uvr6+zs7O3t7e7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf3
9/j4+Pn5+fr6+vv7+/z8/P39/f7+/v///yH5BAEKAP8ALAAAAAAWABYAAAjUAP8JHEiwoMGD
CBMivKKwYZU3DRNWWcaHYcSCVZwVS2SloZUqIEFiYQYK2KWOEpupbLZsmTJLl3CFwiJRWaZM
mDBVoiQJkiNXqr4grHKMklFJkSA1WpTIUChYZQ5WIdbIkCBBhRItUoSoECBKsSwSrJJrjhw5
dPDsAUTIUCFBlcIarGLrLB09fwgdSpQI0ShZNOfWlYPHDyFFjyRRkvVKqFRbkHP1CkaMUidg
p7JIDAkyyzBNwTChvPivSrBehKaQHlgFl5wlq1mfKRJ7YJTauHMLDAgAOw==}

image create photo ::ttk::dialog::image::previous -data {
R0lGODlhFgAWAOcAADp0BFSIJTx1Bzp0A2KSNLrWnz93Czt1BHGeRbXUmL/apTx0BH6qVa/R
joS5UrzZoEF7CzpzBD13CIu2Y6TLf3iyQniyQbnXnbzZob7ao7/apMDbpj92CkR7D5S8bJbD
a22sMW+tNHKvOXaxPnqzRH21R361SX+2SrvYn0mAFprDdIe6VWOmI2aoKGqqLW2sMnCtNnOv
OnWwPXaxP7jWmj52CTt1A1SIIJvEdHWxPlqhF16jHGGlIWSnJWmrK2uvLGqwKGevI2uvKXKy
NrTVlT11CDt3A1SKIJrEcVOdDVWeEFSeD1ekD1enC1mrCluuC1ywDFqqC6rThEmCFZXAbE6a
BlKgB1enCV+0DWK4DmS7D2O7D1+zDajUfkJ5DYy5YYa7U1elDFqsC2jBEWvGEmrFEmfBEWO6
D6rXfzx1CDx2B4GwU5TGY2GxFGC2Dq7dgLLhhLXmhrTlha/dg63Zgjx2CDpyA3WmRZ3Ob2m5
HK3bgEF9CTtzBDduA2aYNqHQdazYgTNlAleLJaPOeS1ZA0yBGzx0Bv//////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
/////////////////////////////////yH5BAEKAP8ALAAAAAAWABYAAAjgAP8JHEiwoMGD
CBMq/AdgYcIAAhwaHECggAGJBA8gSKDgIsZ/Cxg0cPAAQoSTJw8klDCBQgULFzBk0LChJgeE
HTx8ABFCxIgKJEqYOIHipsEUKlawaOHiBYwYMmZYsECjhkEbOHLo2MGjh48fQIIEETKESBGD
RpDASKJkCZMmTp5AgfIkipSzBgFQIVHFypUnWLJo2ZKFSxe8Br18ARNGDBYtY8iUMXMGTZqE
atawaePmDZw4cuDMoVNHoZ07ePLo2YPyJJ+Fffz8AVT6o8BAggbVtv2PUCFDvAn2CU7cdkAA
Ow==}

image create photo ::ttk::dialog::image::previousbw -data {
R0lGODlhFgAWAOcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0N
DQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8f
HyAgICEhISIiIiMjIyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDEx
MTIyMjMzMzQ0NDU1NTY2Njc3Nzg4ODk5OTo6Ojs7Ozw8PD09PT4+Pj8/P0BAQEFBQUJCQkND
Q0REREVFRUZGRkdHR0hISElJSUpKSktLS0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVV
VVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9fX2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdn
Z2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNzc3R0dHV1dXZ2dnd3d3h4eHl5
eXp6ent7e3x8fH19fX5+fn9/f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeHh4iIiImJiYqKiouL
i4yMjI2NjY6Ojo+Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampubm5ycnJ2d
nZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq+v
r7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8DAwMHB
wcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9DQ0NHR0dLS0tPT
09TU1NXV1dbW1tfX19jY2NnZ2dra2tvb29zc3N3d3d7e3t/f3+Dg4OHh4eLi4uPj4+Tk5OXl
5ebm5ufn5+jo6Onp6erq6uvr6+zs7O3t7e7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf3
9/j4+Pn5+fr6+vv7+/z8/P39/f7+/v///yH5BAEKAP8ALAAAAAAWABYAAAjXAP8JHEiwoMGD
CBMq/GdlYcI2VxwatJLnmBaJBK8YIsbsIkaGk351UtalikmTERFm+WSLEqVjypYta0YzC0Iv
p1YtavRIEqVKmDBlSmbT4BhXnwYZSrQTUiSflIwVzehKEp8/ggglYsRIkaJFkYhhMYjFVSM7
ePDw6QNoECFCgwD5GjsxVSU5d/oMQrSz0aJDvega5BLqE59AiBpJsmRJUqNfKQ9iucTqUCJi
yJgtQ1ZMmOCDVBjRejTMy8mTC6P4uRXsM8YlcG65xiikTOSPA6Pg3s1bYEAAOw==}

image create photo ::ttk::dialog::image::up -data {
R0lGODlhFgAWAOcAADx2Azx2BFWLIlWNIjx1A0uBGJzFdZrFckuDF0V8EJzDdnKvOm+tNZbB
bUR7Dz52CZa/cIW5UlqhGFaeEXmzQ467ZD14CIy2ZZTCaWOmI16jHFmgFlSdDoO4UIKyVTt1
Azp2BIKsWaLKfWysMWaoKGGlIVyiGlSeD0+bCI2+X3anSDt2BHShSa3RjXexQG+tNGusLWir
J2GoHFOhCVGgB1ahDpXDamiaOWSUN7XVmIS4UXm1QXe1O3O0NG6zLFyqEVeoClenCVamCV6o
F5zIcluOKViKKLvXoL/bpb7bo73coH27QXm8OmWzGVywDFyvDKrVganTgKjRgKDLeU+FHzt1
BDpzBD14BcDeooLBRXK7KmC2DmG4DmK4DmG3DqzZgj55BcLhpYfHSma6FGW9EGe/EGfAEWa/
EK/cg8TjpnzDOGnDEWvHEmzIE2vGErDfhMbkqXTBKW/MFHHQFW3KE7HghGy9Hma+EGrEEm3J
E27LFGzHE7HfhMXjqa/aha7bg7Deg6/dg///////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
/////////////////////////////////yH5BAEKAP8ALAAAAAAWABYAAAjWAP8JHEiwoMGD
CBMqXMiw4UEAARwWLGDgAAGJAhMoWMCggQOJDyBEkDCBQgULDQFcwJBBwwYOHTx8WAgihIgR
JEqYOIEihYoVCQGwaOHiBYwYMmbQqGHjxsWDOHLo2MGjh48fQIIIGUKkyEEjR5AkUbKESRMn
Tp5AiSJlCpWCVazIvYIli5YtXLp4+QJGrhUQCK2EETOGTBkzZ9BYYWgljRoya9i0cfNm8UIr
cOKccSNnDp06lhVitnMHTx49e/iETmilj58/gPjU4RNodWC/uOVi3L07IAA7}

image create photo ::ttk::dialog::image::upbw -data {
R0lGODlhFgAWAOcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0N
DQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8f
HyAgICEhISIiIiMjIyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDEx
MTIyMjMzMzQ0NDU1NTY2Njc3Nzg4ODk5OTo6Ojs7Ozw8PD09PT4+Pj8/P0BAQEFBQUJCQkND
Q0REREVFRUZGRkdHR0hISElJSUpKSktLS0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVV
VVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9fX2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdn
Z2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNzc3R0dHV1dXZ2dnd3d3h4eHl5
eXp6ent7e3x8fH19fX5+fn9/f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeHh4iIiImJiYqKiouL
i4yMjI2NjY6Ojo+Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampubm5ycnJ2d
nZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq+v
r7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8DAwMHB
wcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9DQ0NHR0dLS0tPT
09TU1NXV1dbW1tfX19jY2NnZ2dra2tvb29zc3N3d3d7e3t/f3+Dg4OHh4eLi4uPj4+Tk5OXl
5ebm5ufn5+jo6Onp6erq6uvr6+zs7O3t7e7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf3
9/j4+Pn5+fr6+vv7+/z8/P39/f7+/v///yH5BAEKAP8ALAAAAAAWABYAAAjPAP8JHEiwoMGD
CBMqXMiw4cErWBwWLPPK1RWJAr+4etRIlReJWVR54oOn0qgsDa+AUjXoz547nDJdVHjFUq1F
hgT5wUOHVKOZDxP5mtRIEaJBeO7oWQUIaME9xDpZoiTpUSA/ffgEijXnIBxkzMJqyqSIkFlf
vXbVSlPwSpW3WZyBqpRo0SJFwbS8reKUYJVophw9iiQpErEqDKtI8/SI0iVMlowhXliFWqZI
ljZ5ynRsssLKkyBVyqTpUufE04YNM3asdTHPCffK3ouxdu2AADs=}

image create photo ::ttk::dialog::image::gohome -data {
R0lGODlhFgAWAMYAAKQAAPR1deU5OeInJ+xGRvFMTPBRUfJVVeAmJvNbW/JeXntMSohaWN4m
JvNkZJldW4SFgpubmsCKitwmJvRsbPRmZp11c4+Qjbi5uMLCwbq6ucShodwlJfNjY6ONi5+g
nr+/vt7e3d3d3dfX18m1tZwICKefnaOjotra2urq6unp6efn59zQ0IQiIaGgnqKjodjY2Obm
5uTk5OPj4+Le3tvc21VXU3d4enZ5fXV1dXV2dvPz8+7u7n6Ae3+BfICCfeXl5XZ5fHmZw3eY
wnV4fPLy8u3t7YSGgYWHguLi4nV4e1+Gt0p2rnJ1evHx8ezs7IaIg4qIZYmIcODg4HF4gTRl
pG52gfDw8Ovr64eJhIiJfvn5+bGztri8wbq7vLm9waSkpO/v74iKhd7e3qKioqOjo2VnY5eZ
lJiZlpmalpmal/j4+P//////////////////////////////////////////////////////
/////////////////////////yH5BAEKAH8ALAAAAAAWABYAAAf+gH+Cg4QAAISIiYUBAYeK
j38AjIyOkIsCjAONloOSBAWZmpWPkgYHjZIIopCSCQqNCwySDauJkg4OjQ8QERKSE7WdARQV
jRYXGBkaG5IcwZEBHY0eHyAhISIjJCUBHJvCjSYnKCnlKiorLNzfgpItLi8wMSv0MTIyMzTc
o5E1Nv//0N3AkQOHjh38/tjgYaOHjx8/YgAJIiTHECJFbCSyYcTGkY9IZCRRsiQHkyZONCKy
8cQGFChRpCSZQqVKjipWrqgkZAOLjSxZtPiYsoVLFy9fwITZOchGChtioooZs4VMmatlRDAV
ZOOKmTNo0qjZwaOs2TVbFQJcyxYgp7cEcDkFAgA7}

image create photo ::ttk::dialog::image::gohomebw -data {
R0lGODlhFgAWAOcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0N
DQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8f
HyAgICEhISIiIiMjIyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDEx
MTIyMjMzMzQ0NDU1NTY2Njc3Nzg4ODk5OTo6Ojs7Ozw8PD09PT4+Pj8/P0BAQEFBQUJCQkND
Q0REREVFRUZGRkdHR0hISElJSUpKSktLS0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVV
VVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9fX2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdn
Z2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNzc3R0dHV1dXZ2dnd3d3h4eHl5
eXp6ent7e3x8fH19fX5+fn9/f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeHh4iIiImJiYqKiouL
i4yMjI2NjY6Ojo+Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampubm5ycnJ2d
nZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq+v
r7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8DAwMHB
wcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9DQ0NHR0dLS0tPT
09TU1NXV1dbW1tfX19jY2NnZ2dra2tvb29zc3N3d3d7e3t/f3+Dg4OHh4eLi4uPj4+Tk5OXl
5ebm5ufn5+jo6Onp6erq6uvr6+zs7O3t7e7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf3
9/j4+Pn5+fr6+vv7+/z8/P39/f7+/v///yH5BAEKAP8ALAAAAAAWABYAAAj+AP8JHEgwRgyC
CBMW3LTpoMKH/2IwZOgQ4kI2DL80tDhQ4p0+GTVWfCgREKGGEruIhCgRkaKGWc6kXJlQoiNH
Dd0Q0qRJIheaHTdRgtQQ0CNcwXKtkrgFaMRNOGNM+uSrm9Vru2hs2rIxaMNQorSpG5su3blp
WrsKlPgDlChs5s7JNUeO3LhvWkdG3Falb1+zd/DUETxP778q7qr4+QMIkLlyeCjVkXRHXpWE
VdpVIcS5EDlxd/7UcUMn3mWEVdhVMWSIUCFx4Ox0qdOFDrzTBKusq3Ko9x9w+WTt0sWL1Dvc
A6uoq4KoOSJv+USNmj6qG3KBVeCVuYQpU6Z57sIPi8d3/bDf8+j9clzPnmNAADs=}

image create photo ::ttk::dialog::image::reload -data {
R0lGODlhFgAWAOcAADtqqDtrqDdnpTVmpThopjpqpzdopjpqqHeaxaC726zG4q7I46jC3p25
2X6hyk16sDZnpTdnpjRlpFqDt7fN5bDI4qC82q3G4bfN5rrP5rvR57vQ57vR6K/H4W+VwThp
pnOYxUZ0rkVyrJ+52Ux4sDlppjdmpU56sYWmzbbN5bXM5abC4LHK5KO/3X+iy8PW6kNxrDtq
p1N+sz5tq0BvqzZnpDpppzprqH+kzLHJ45a325G02bTM5cja7EBuqjtrpzVlpE56tGKNw0x4
r6fA3a/J43Sfz83d7j1sqD9uq2yWyjpqqT5tqbTJ4pS22nKfz9Xi8DdopabA3cna7M3d7dTi
8Nzn8zZnpjRlpTlppzhopzZmpTVlpdrl8eDp8+Dp9OHq9Nnk8FV+szVmpOLr9aC+3qG+3dvm
8n+gx0FwrOPs9Zu63L3S6Nzm8lB8smWOxEd2sDxsqDRmpOTs9crb7K7I4sHV6oKjyzdopz5u
qz1sqUd0ruXt9sDS5tjj8dHf7qrG4sDU6bjN5YSkzGqQv1B7sj1rqEBuqVeBtZOy1sXV6Dlo
pjtppoelysjY6bDJ5LPK5KrE4Zq42j9vqURxqjxpo2qOvJSx07LJ4rbN5qK+3XKXwy9ZjzNl
pDFbkTZlojZno0FuqDdnpDZmpDRfl///////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
/////////////////////////////////yH5BAEKAP8ALAAAAAAWABYAAAj+AP8JHEiwoMGD
CBMWBBBAwAACBQwYHGCwwAEECRQsYNDAwQMIAyNIKFhgAoUKFi5gyKBhA4cOHj5EABGioIgR
JCKUMAHhBIoUKlawaOHiBQyCMWTEmEGjxkAbN3Dk0LGDRw8fBH8ACSLEhsEPQ4gUMXIECUEb
SZT8W3KQSRMnT6B4HShAYRQpU6hUsXJFIUEsEm5k0WLgChaCA7YoXszF78ABXbx8ARNGjMIx
BIGQKWPmDBqJBW8ITAMAsZo1bNq4yWLQwBs4EuIQlDOHTh07Vu7gASlwQB49MPYUlMOnj58/
gAIJGkSokKFDiFwkIlAQgqJFjBo5osBDxSMWkBYmRJI0yeAYSgMrWbqEiU2mHJo2leBksJNB
T59AhRI1ipTj/wD6FRAAOw==}

image create photo ::ttk::dialog::image::folder_new -data {
R0lGODlhFgAWAPZxAFVXU1ZYVFdZVVhZUlhaVl1fW19hXWdpZW1va7O5baexc8a6V8nJbdvVeNrY
feDcfOLdfDRlozRlpDtqoERljkdqlFh8lE54rlp5oFh7pV+BkWSApHOOr3ySrW2KsHWOsnycvmqa
zmuczmyczm2cznGfz3Kf0HOg0Hei0Xej0Xij0Xqk0n6n03+o1I6OjYuQlpucm7u4m564vaampaur
p6WoqqioqKqrqqW8tKixvLS0tLe3t7i4uLm5ubq6uby8vL6+vsG8lLvImr3MucjOi9PWjuXgiO/p
jPbqgfXsi/Xtl+/npu/poe/nqu7nr+/rte/stvPuvoakxZGyzICo04Gp1Ias1Yes1oyv0omu1omv
142y2ZWz0pS115683aO/3qjAza3B1KnC3KfC4K/H48HBwcTExMnJydDQ0NLS0uvnw+vnxOrnzfTx
3fLw4PX08vb19QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5
BAUAAHEALAAAAAAWABYAAAf/gHGCg4SFhoeIiTcIjIwHBz6JhAholZZoB2eSgggzLp+gLgUEAgEA
AzFNS2uDlDc2sLGwNzM0QQtJSkhOggczGxLBwsIRFglGbm9PDWxxB2gSZGPT1NNiQw9Mb3BRDGrO
MxJeWeTl5TJEEFBtRwrNBmni5vNYMkIORkUaggbh4/PzpsjAAWaCIAHQ/gEsp0XLFS4XBAHwt9Dc
FXJSMkiENuZilotXrlgZaSXkFRAcJIb7UqUllZZVqLRgIZNFFg4dBA1Is2EMixVAVahYIVQFihQq
tmDIIbHGhy0nop4wYaKEVRIlSLTIUuGGxDBdRowQISKE2bNnU3igMEMQjAgRIYbJnftCxyA0Z8r8
8OGDRw++PHbw8PEDiJkzaDYpXpwoEAA7}

image create photo ::ttk::dialog::image::configure -data {
R0lGODlhFgAWAMYAAH9/f+rp6Pn5+NjY1/j39vPy8YKXsjRlpOzq6P///050pHx8fLu7u+3r
6szMzK+vr2WErOjn5Orq6q2trePj4vr6+Xl4dNzc3JmZmejn5vLx7+3r6evp5/r6+oeHh8/N
yvj49/n59/n49/7+/p6enrW1tfb29Z+fnvj4+Ofm5LvByEVxqfT09J2wyt/f31l9q6enpiBK
h1R8rqSttvv7+3WQrqS60JCmvqexvcHBwePi4dPf6qKuvJ22zmN7lYScttfi7Y2YpZ240mB3
kZmtw9/n8IGTqVhthFtxiYaGhqG0yO7z9mB2j+Tj4V9fXpGmvvD095eltgAAALDG2+3y9oGK
lWyFocDR4v//////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
/////////////////////////yH5BAEKAH8ALAAAAAAWABYAAAfygH+CggAAg4eIiX8AAQID
hoqRhAQFj5EGB5EACAKQiAcJCpl/C4WCDA2diaAODxCEERIAExQIFRarFw+jfxgZGhsIHMOq
gwcdB7yCHh8gAiECwyKQByPKhySFACUCwiYnByjXkgACKSorLOOSiy0HLi8w7Icx9QcsMjM0
npIxNTY3YhzAkUPHCH6J/O3g0cNHDAAjhh2MFOMHkCA+hAyJsWiEsImIYhApYuSIkBpIOHaU
mISekiVGmJxMeQhiEycgYzyBEkUmSpWCpAgdKvRPjClUqswEGpToUKNWhFx5QjORUymDYlix
4lAS0ZD15hUVFAgAOw==}

image create photo ::ttk::dialog::image::folder -data {
R0lGODlhEAAQAKUAAG1va2dpZc7OzsbGxWNlYcDAv5aXlVVXU8nJyaampqenp6ioqGF6mjRl
pEZtnMbY677S6K7H44yx2F9hXYmu1qbC4Dlnoq3H44uw14qv14iu1oWr1YCo03qk0nOgz26d
zpi53Fh2m5u73XCeznCdz26czm2czmybzmubzWqazmmZzWiZzZS226mrqYmv12uazWqazWiY
zWaYzGWYzWWXzGSWzGOVzJq63lNxlkVdeT5giT9ghv///////////////yH5BAEKAD8ALAAA
AAAQABAAAAaGwB9gOAwEfsgkEiBoOgcEZRJQMFivhoNWu0QkvmCwYnFABgqMhnrNVjsCiMYD
Qq/bH41zIyLp+/8RDRNxfH+GgQcFe4aHDQeEjICOioWRFBWOCBYXGBIYGRobHB0eHyCTISIj
JB8lJicoKSorLI4tLigvMCoxMjM0NTY3ODk6bcdqO1LLy0EAOw==}

image create photo ::ttk::dialog::image::file -data {
R0lGODlhEAAQAIQAAJmZmYGBgf///+zs7Orq6uvr6+3t7fDw8MTExMXFxcbGxsfHx+7u7u3t
5e3t5u/v78jIyPHx8fLy8pWVlf//////////////////////////////////////////////
/yH5BAEKAB8ALAAAAAAQABAAAAVuIBCMZDl+aCCsbLsGqTAQRGEPg3EI8KcSiERCQVQsdr3f
DWcwMJCxwrBIPPKiBaahMXhefYIClcFweJOynJPxaEPBg+JiAam/VTmyO8L/qgxGdHV8En4C
TWwPBwcREoVoLpE9EyaVARMomZqbmiEAOw==}

# Images for ttk::chooseDirectory

image create photo ::ttk::dialog::image::dirclose -data {
R0lGODlhCQAJAKUAAFRWUlVXU1pcWP///1lbV2BiXt/i3Obo5O3u6/P08vj4911fW2NlYeHk
3+bp5Ovt6u/x7vDx72ZoZAAAAGNmYWpsZ93g2t7h2+Di3WdpZG1vatjb1dfb1Njb1Nfb09XZ
0WpsaHBybW1wa3N1cP//////////////////////////////////////////////////////
/////////////////////////////////////////////////////////yH5BAEKAD8ALAAA
AAAJAAkAAAY4QEBgSBwKBsjkgFAYGA6IhGKwYAwajgckMihIBpNweECpDCwXDOYyyGgGG07H
8xmAQsqkaMTv94MAOw==}

image create photo ::ttk::dialog::image::diropen -data {
R0lGODlhCQAJAKUAAFRWUlVXU1pcWP///1lbV2BiXt/i3Obo5AAAAPP08vj4911fW2NlYeHk
3+bp5O/x7vDx72ZoZGNmYWpsZ93g2t7h2+Di3WdpZG1vatjb1dfb1Nfb09XZ0WpsaHBybW1w
a3N1cP//////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////yH5BAEKAD8ALAAA
AAAJAAkAAAY4QEBgSBwKBsjkgFAYGA6IhGKwYAwaDsQDMihEBohweCCZDCgVhKUyuGAGGQ1i
wxl0PMrkB8Tv94MAOw==}

### ttk::getOpenFile, ttk::getSaveFile, ttk::getAppendFile

proc ttk::getOpenFile {args} {
	return [::ttk::dialog::file::tkFDialog open $args]
}

proc ttk::getSaveFile {args} {
	return [::ttk::dialog::file::tkFDialog save $args]
}

proc ttk::getAppendFile {args} {
	return [::ttk::dialog::file::tkFDialog append $args]
}

proc ::ttk::dialog::file::Create {win class} {
	toplevel $win -class $class
	wm withdraw $win

	set dataName [winfo name $win]
	upvar ::ttk::dialog::file::$dataName data

	# Additional frame to make sure the toplevel has the correct
	# background color for the theme
	#
	set w [ttk::frame $win.f]
	pack $w -fill both -expand 1

	# f1: the toolbar
	#
	set f1 [ttk::frame $w.f1 -class Toolbar]
	set data(bgLabel) [ttk::label $f1.bg -style Toolbutton]
	set data(upBtn) [ttk::button $f1.up -style Toolbutton]
	$data(upBtn) configure -image {::ttk::dialog::image::up 
		disabled ::ttk::dialog::image::upbw} \
		-command [list ::ttk::dialog::file::UpDirCmd $win]
	set data(prevBtn) [ttk::button $f1.prev -style Toolbutton]
	$data(prevBtn) configure -image {::ttk::dialog::image::previous
		disabled ::ttk::dialog::image::previousbw} \
		-command [list ::ttk::dialog::file::PrevDirCmd $win]
	set data(nextBtn) [ttk::button $f1.next -style Toolbutton]
	$data(nextBtn) configure -image {::ttk::dialog::image::next
		disabled ::ttk::dialog::image::nextbw} \
		-command [list ::ttk::dialog::file::NextDirCmd $win]
	set data(homeBtn) [ttk::button $f1.home -style Toolbutton]
	$data(homeBtn) configure -image {::ttk::dialog::image::gohome \
		disabled ::ttk::dialog::image::gohomebw} \
		-command [list ::ttk::dialog::file::HomeDirCmd $win]
	set data(reloadBtn) [ttk::button $f1.reload -style Toolbutton]
	$data(reloadBtn) configure -image ::ttk::dialog::image::reload \
		-command [list ::ttk::dialog::file::Update $win]
	set data(newBtn) [ttk::button $f1.new -style Toolbutton]
	$data(newBtn) configure -image ::ttk::dialog::image::folder_new \
		-command [list ::ttk::dialog::file::NewDirCmd $win]
	set data(cfgBtn) [ttk::menubutton $f1.cfg -style Toolbutton]
	set data(cfgMenu) [menu $data(cfgBtn).menu -tearoff 0]
	$data(cfgBtn) configure -image ::ttk::dialog::image::configure \
		-menu $data(cfgMenu)
	set data(dirMenuBtn) [ttk::combobox $f1.menu]
	$data(dirMenuBtn) configure \
		-textvariable ::ttk::dialog::file::${dataName}(selectPath)

	set data(sortMenu) [menu $data(cfgMenu).sort -tearoff 0]

	$data(cfgMenu) add cascade -label " Sorting" -menu $data(sortMenu)
	$data(cfgMenu) add separator
	$data(cfgMenu) add radiobutton -label "Short View" \
		-variable ::ttk::dialog::file::details -value 0 \
		-command [list ::ttk::dialog::file::setopt $win \
			-details ::ttk::dialog::file::details]
	$data(cfgMenu) add radiobutton -label "Detailed View" \
		-variable ::ttk::dialog::file::details -value 1 \
		-command [list ::ttk::dialog::file::setopt $win \
			-details ::ttk::dialog::file::details]
	$data(cfgMenu) add separator
	$data(cfgMenu) add checkbutton -label "Show Hidden Files" \
		-variable ::ttk::dialog::file::hidden \
		-command [list ::ttk::dialog::file::setopt $win \
			-hidden ::ttk::dialog::file::hidden]
	$data(cfgMenu) add checkbutton -label "Separate Folders" \
		-variable ::ttk::dialog::file::sepfolders \
		-command [list ::ttk::dialog::file::setopt $win \
			-sepfolders ::ttk::dialog::file::sepfolders]
	$data(sortMenu) add radiobutton -label "By Name" \
		-variable ::ttk::dialog::file::sort -value name \
		-command [list ::ttk::dialog::file::setopt $win \
			-sort ::ttk::dialog::file::sort]
	$data(sortMenu) add radiobutton -label "By Date" \
		-variable ::ttk::dialog::file::sort -value date \
		-command [list ::ttk::dialog::file::setopt $win \
			-sort ::ttk::dialog::file::sort]
	$data(sortMenu) add radiobutton -label "By Size" \
		-variable ::ttk::dialog::file::sort -value size \
		-command [list ::ttk::dialog::file::setopt $win \
			-sort ::ttk::dialog::file::sort]
	$data(sortMenu) add separator
	$data(sortMenu) add checkbutton -label "Reverse" \
		-variable ::ttk::dialog::file::reverse \
		-command [list ::ttk::dialog::file::setopt $win \
			-reverse ::ttk::dialog::file::reverse]
	$data(sortMenu) add checkbutton -label "Folders First" \
		-variable ::ttk::dialog::file::foldersfirst \
		-command [list ::ttk::dialog::file::setopt $win \
			-foldersfirst ::ttk::dialog::file::foldersfirst]

	$data(prevBtn) state disabled
	$data(nextBtn) state disabled
	if {![info exists ::env(HOME)]} {
		$data(homeBtn) state disabled
	}

	place $data(bgLabel) -relheight 1 -relwidth 1

	pack $data(upBtn) -side left -fill y
	pack $data(prevBtn) -side left -fill y
	pack $data(nextBtn) -side left -fill y
	pack $data(homeBtn) -side left -fill y
	pack $data(reloadBtn) -side left -fill y
	pack $data(newBtn) -side left -fill y
	pack $data(cfgBtn) -side left -fill y
	pack $data(dirMenuBtn) -side left -fill x -expand 1 -padx 8

	# f2: the frame with the OK button, cancel button, "file name" field,
	#     and file types field.
	#
	set f2 [ttk::frame $w.f2]
	ttk::label $f2.lab1 -text "Location:" -anchor w
	set data(location) [ttk::combobox $f2.loc]
	$data(location) configure \
		-textvariable ::ttk::dialog::file::${dataName}(selectFile)
	set data(typeMenuLab) [ttk::label $f2.lab2 -text "Filter:" -anchor w]
	set data(typeMenuBtn) [ttk::combobox $f2.filter]
	set data(okBtn) [ttk::button $f2.ok -text OK -default active \
		-width 8 -style Slim.TButton \
		-command [list ::ttk::dialog::file::Done $win]]
	set data(cancelBtn) [ttk::button $f2.cancel -text Cancel \
		-width 8 -style Slim.TButton \
		-command [list ::ttk::dialog::file::Cancel $win]]

	grid $f2.lab1 $f2.loc $data(okBtn) -padx 4 -pady 5 -sticky ew
	grid $f2.lab2 $f2.filter $data(cancelBtn) -padx 4 -pady 5 -sticky ew
	grid columnconfigure $f2 1 -weight 1

	# f3: The file and directory lists
	#
	set f3 [ttk::panedwindow $w.f3 -orient horizontal]
	set font TkDefaultFont
	destroy $f3.dummy
	$f3 add [ttk::frame $f3.dir] -weight 0
	ttk::label $f3.dir.bg -relief sunken
	set data(dirArea) [text $f3.dir.t -bg white -width 20 -height 16 \
		-font $font -bd 0 -highlightthickness 0 -cursor "" \
		-wrap none -spacing1 1 -spacing3 1 -exportselection 0 \
		-state disabled -yscrollcommand [list $f3.dir.y set] \
		-xscrollcommand [list $f3.dir.x set]]
	ttk::scrollbar $f3.dir.y -command [list $f3.dir.t yview]
	ttk::scrollbar $f3.dir.x -command [list $f3.dir.t xview] \
		-orient horizontal
	grid $f3.dir.t $f3.dir.y -sticky ns
	grid $f3.dir.x -sticky we
	grid $f3.dir.bg -row 0 -column 0 -rowspan 2 -columnspan 2 -sticky news
	grid $f3.dir.t -sticky news -padx {2 0} -pady {2 0}
	grid columnconfigure $f3.dir 0 -weight 1
	grid rowconfigure $f3.dir 0 -weight 1

	$f3 add [ttk::frame $f3.file] -weight 1

	# The short view version
	#
	set data(short) [ttk::frame $f3.file.short]
	ttk::label $data(short).bg -relief sunken
	set data(fileArea) [text $data(short).t -width 50 -height 16 \
		-bg white -font $font -bd 0 -highlightthickness 0 \
		-cursor "" -wrap none -spacing1 1 -spacing3 1 \
		-exportselection 0 -state disabled]
	set data(xScroll) [ttk::scrollbar $data(short).x -orient horizontal]
	$data(xScroll) config -command [list $data(fileArea) xview]
	$data(fileArea) config -xscrollcommand [list $data(xScroll) set]
	grid $data(short).t -sticky news -padx 2 -pady {2 0}
	grid $data(short).x -sticky ew
	grid $data(short).bg -row 0 -column 0 \
		-rowspan 2 -columnspan 2 -sticky news
	grid columnconfigure $data(short) 0 -weight 1
	grid rowconfigure $data(short) 0 -weight 1

	# The detailed view version
	#
	set data(long) [ttk::frame $f3.file.long]
	ttk::label $data(long).bg -relief sunken
	ttk::frame $data(long).f
	set data(fileHdr) [frame $data(long).f.f]
	ttk::label $data(fileHdr).l0 -text Name -style Toolbutton -anchor w
	ttk::label $data(fileHdr).l1 -text Size -style Toolbutton -anchor w
	ttk::label $data(fileHdr).l2 -text Date -style Toolbutton -anchor w
	ttk::label $data(fileHdr).l3 -text Permissions -style Toolbutton -anchor w
	ttk::label $data(fileHdr).l4 -text Owner -style Toolbutton -anchor w
	ttk::label $data(fileHdr).l5 -text Group -style Toolbutton -anchor w
	ttk::separator $data(fileHdr).s1 -orient vertical
	ttk::separator $data(fileHdr).s2 -orient vertical
	ttk::separator $data(fileHdr).s3 -orient vertical
	ttk::separator $data(fileHdr).s4 -orient vertical
	ttk::separator $data(fileHdr).s5 -orient vertical
	set height [winfo reqheight $data(fileHdr).l1]
	$data(long).f configure -height [expr {$height + 1}]
	$data(fileHdr) configure -height $height
	place $data(fileHdr) -x 1 -relwidth 1
	place $data(fileHdr).l0 -x -1 -relwidth 1 -relheight 1
	place $data(fileHdr).s1 -rely .1 -relheight .8 -anchor n
	place $data(fileHdr).s2 -rely .1 -relheight .8 -anchor n
	place $data(fileHdr).s3 -rely .1 -relheight .8 -anchor n
	place $data(fileHdr).s4 -rely .1 -relheight .8 -anchor n
	place $data(fileHdr).s5 -rely .1 -relheight .8 -anchor n
	set data(fileList) [text $data(long).t -width 42 -height 12 \
		-bg white -font $font -bd 0 -highlightthickness 0 \
		-cursor "" -wrap none -spacing1 1 -spacing3 1 \
		-exportselection 0 -state disabled \
		-yscrollcommand [list $data(long).y set] \
		-xscrollcommand [list ::ttk::dialog::file::scrollhdr $win]]
	ttk::scrollbar $data(long).y -command [list $data(long).t yview]
	ttk::scrollbar $data(long).x -orient horizontal \
		-command [list $data(long).t xview]
	grid $data(long).f $data(long).y -sticky ew -padx {2 0} -pady {2 0}
	grid $data(long).t ^ -sticky news -padx {2 0}
	grid $data(long).x -sticky ew
	grid $data(long).y -sticky ns -padx 0 -pady 0
	grid $data(long).bg -row 0 -column 0 \
		-rowspan 3 -columnspan 2 -sticky news
	grid columnconfigure $data(long) 0 -weight 1
	grid rowconfigure $data(long) 1 -weight 1

	grid $data(long) $data(short) -row 0 -column 0 -sticky news
	grid columnconfigure $f3.file 0 -weight 1
	grid rowconfigure $f3.file 0 -weight 1

	# Get rid of the default Text bindings
	bindtags $data(dirArea) [list $data(dirArea) FileDialogDir $win all]
	bindtags $data(fileArea) [list $data(fileArea) FileDialogFile $win all]
	bindtags $data(fileList) [list $data(fileList) FileDialogList $win all]

	$data(fileArea) tag bind file <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileArea) tag bind characterSpecial <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileArea) tag bind blockSpecial <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileArea) tag bind fifo <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileArea) tag bind link <1> \
		{set ::ttk::dialog::file::filetype link}
	$data(fileArea) tag bind directory <1> \
		{set ::ttk::dialog::file::filetype directory}
	$data(fileList) tag bind file <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileList) tag bind characterSpecial <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileList) tag bind blockSpecial <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileList) tag bind fifo <1> \
		{set ::ttk::dialog::file::filetype file}
	$data(fileList) tag bind link <1> \
		{set ::ttk::dialog::file::filetype link}
	$data(fileList) tag bind directory <1> \
		{set ::ttk::dialog::file::filetype directory}

	set data(paneWin) $f3

	pack $f1 -side top -fill x
	pack $f2 -side bottom -fill x -padx 8 -pady {0 5}
	pack $f3 -side bottom -fill both -expand 1 -padx 8 -pady {6 0}

	set data(columns) 0
	set data(history) ""
	set data(histpos) -1

	update idletasks
	pack propagate $w 0

	wm protocol $win WM_DELETE_WINDOW [list $data(cancelBtn) invoke]
	bind $win <KeyPress-Escape> \
		[list event generate $data(cancelBtn) <<Invoke>>]

	bind $data(fileArea) <Configure> \
		[list ::ttk::dialog::file::configure $win]
	bind $data(dirMenuBtn) <Return> [list ::ttk::dialog::file::chdir $win]
	bind $data(dirMenuBtn) <<ComboboxSelected>> \
		[list ::ttk::dialog::file::chdir $win]
	bind $data(location) <Return> [list ::ttk::dialog::file::Done $win]
	bind $data(typeMenuBtn) <Return> \
		[list ::ttk::dialog::file::SetFilter $win]
	bind $data(typeMenuBtn) <<ComboboxSelected>> \
		[list ::ttk::dialog::file::SelectFilter $win]
}

proc ::ttk::dialog::file::ChangeDir {w dir} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	set data(history) [lrange $data(history) 0 $data(histpos)]
	set cwd [lindex $data(history) $data(histpos)]
	set data(selectPath) [file normalize [file join $cwd $dir]]
	lappend data(history) $data(selectPath)
	if {[incr data(histpos)]} {
		$data(prevBtn) state !disabled
		#set data(selectFile) ""
	}
	$data(nextBtn) state disabled

	UpdateWhenIdle $w
}

proc ::ttk::dialog::file::UpdateWhenIdle {w} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	if {[info exists data(updateId)]} {
		return
	} elseif {[winfo ismapped $w]} {
		set after idle
	} else {
		set after 1
	}
	set data(updateId) [after $after [list ::ttk::dialog::file::Update $w]]
}

proc ::ttk::dialog::file::Update {w} {
	# This proc may be called within an idle handler. Make sure that the
	# window has not been destroyed before this proc is called
	if {![winfo exists $w]} {
		return
	}

	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data
	unset -nocomplain data(updateId)

	if {$data(-details)} {
		grid $data(long)
		grid remove $data(short)
	} else {
		grid $data(short)
		grid remove $data(long)
	}
	if {$data(-sepfolders)} {
		if {![llength [winfo manager $data(paneWin).dir]]} {
			$data(paneWin) insert 0 $data(paneWin).dir
		}
	} else {
		if {[llength [winfo manager $data(paneWin).dir]]} {
			$data(paneWin) forget 0
		}
	}

	$w configure -cursor watch
	update

	set dir ::ttk::dialog::image::folder
	set file ::ttk::dialog::image::file

	set cwd [lindex $data(history) $data(histpos)]

	if {$data(-hidden)} {
		set pattern "* .*"
	} else {
		set pattern "*"
	}

	# Make the directory list
	set dlist ""
	foreach f [eval glob -nocomplain -tails \
		-directory $cwd -type d $pattern] {
		if {[string equal $f .]} continue
		if {[string equal $f ..]} continue
		lappend dlist [list $f dir]
	}

	# Make the file list	
	set flist ""
	set filter $data(filter)
	if {[string equal $filter *]} {
		set filter $pattern
	}
	foreach f [eval [linsert $filter 0 glob -nocomplain -tails \
		-directory $cwd -type {f l c b p}]] {
		# Links can still be directories. Skip those.
		if {[file isdirectory [file join $cwd $f]]} continue
		lappend flist [list $f file]
	}

	# Combine the two lists, if necessary
	if {$data(-sepfolders)} {
		set dlist [sort $w $dlist]
		set flist [sort $w $flist]
	} elseif {$data(-foldersfirst)} {
		set flist [concat [sort $w $dlist] [sort $w $flist]]
		set dlist ""
	} else {
		set flist [sort $w [concat $flist $dlist]]
		set dlist ""
	}
	
	set t $data(dirArea) 
	$t configure -state normal
	$t delete 1.0 end
	foreach f $dlist {
		$t image create end -image $dir
		$t insert end " [lindex $f 0]\n"
	}
	$t delete end-1c end
	$t configure -state disabled

	if {$data(-details)} {
		set t $data(fileList)
		$t configure -state normal
		$t delete 1.0 end
		set size ""
		set date ""
		set mode ""
		set uid ""
		set gid ""
		set maxsize 50
		set font [$t cget -font]
		foreach f $flist {
			lassign $f name type size date mode uid gid
			if {![info exists users($uid)] || \
				![info exists groups($gid)]} {
				set fname [file join $cwd $name]
				# May fail for dead links
				if {![catch {array set attr \
					[file attributes $fname]}]} {
					if {[info exists attr(-owner)]} {
						set users($uid) $attr(-owner)
					} else {
						set users($uid) ""
					}
					if {[info exists attr(-group)]} {
						set groups($gid) $attr(-group)
					} else {
						set groups($gid) ""
					}
				}	
			}
			catch {set uid $users($uid)}
			catch {set gid $groups($gid)}
			set image [expr {$type eq "directory" ? $dir : $file}]
			set img [$t image create end -image $image]
			$t tag add name $img
			$t tag add $type $img
			$t insert end " $name" [list name $type]
			$t insert end "\t$size\t" $type
			$t insert end "[datefmt $date]\t" $type
			$t insert end "[modefmt $type $mode]\t" $type
			$t insert end "$uid\t$gid\t\n" $type
			set size [font measure $font " $name"]
			if {$size > $maxsize} {
				set maxsize $size
			}
		}
		$t delete end-1c end
		$t configure -state disabled
		set today [datefmt [clock seconds]]
		set maxp [winfo reqwidth $data(fileHdr).l3]
		set maxu [winfo reqwidth $data(fileHdr).l4]
		foreach n [array names users] {
			set size [font measure $font $users($n)]
			if {$size > $maxu} {set maxu $size}
		}
		set maxg [winfo reqwidth $data(fileHdr).l5]
		foreach n [array names groups] {
			set size [font measure $font $groups($n)]
			if {$size > $maxg} {set maxg $size}
		}
		set tabs [list [set x [incr maxsize 22]]]
		lappend tabs [incr x [font measure $font 1000000000]] \
			[incr x [font measure $font " $today "]] \
			[incr x [incr maxp 8]] \
			[incr x [incr maxu 8]] [incr x [incr maxg 8]]
		$t configure -tabs $tabs
		set i 1
		foreach n $tabs {
			place $data(fileHdr).l$i -x $n
			place $data(fileHdr).s$i -x $n
			if {[incr i] > 5} break
		}
	} else {
		set t $data(fileArea)
		$t configure -state normal
		$t delete 1.0 end
		set lines [expr {[winfo height $t] / 18}]
		set row 1
		set col 0
		set maxsize 50
		set list ""
		set font [$t cget -font]
		foreach f $flist {
			set idx "$row.end"
			lassign $f name type
			set image [expr {$type eq "directory" ? $dir : $file}]
			set img [$t image create $idx -image $image]
			$t tag add $type $img
			$t tag add name $img
			$t insert $idx " $name" [list name $type] "\t" $type
			lappend list $name $type
			set size [font measure $font " $name"]
			if {$size > $maxsize} {
				set maxsize $size
			}
			if {[incr row] > $lines} {
				incr col
				set row 1
			} elseif {$col == 0} {
				$t insert $idx "\n"
			}
		}
		# Make sure maxsize is a multiple of an average size character
		set dx [font measure $font 0]
		set maxsize [expr {($maxsize + 20 + $dx) / $dx * $dx}]
		$t configure -state disabled
		$t configure -tabs $maxsize
		set data(columns) [expr {$row > 1 ? $col + 1 : $col}]
		set data(rows) $lines
		set data(colwidth) $maxsize
		set data(list) $list
	}

	if {[string equal $cwd "/"]} {
		$data(upBtn) state disabled
	} else {
		$data(upBtn) state !disabled
	}
	$w configure -cursor ""
}

proc ::ttk::dialog::file::sort {w list} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	set cwd [lindex $data(history) $data(histpos)]
	set order [expr {$data(-reverse) ? "-decreasing" : "-increasing"}]
	set newlist ""
	foreach f $list {
		set file [lindex $f 0]
		# Use lstat in case the destination doesn't exists
		file lstat [file join $cwd $file] stat
		if {[string equal $stat(type) link]} {
			# This may fail if the link points to nothing
			if {![catch {file stat [file join $cwd $file] dest}]} {
				array set stat [array get dest]
				if {[string equal $stat(type) file]} {
					set stat(type) link
				}
			}
		}
		lappend newlist [list $file $stat(type) $stat(size) \
			$stat(mtime) $stat(mode) $stat(uid) $stat(gid)]
	}
	switch -- $data(-sort) {
		size {
			set mode -integer
			set idx 2
		}
		date {
			set mode -integer
			set idx 3
		}
		default {
			set mode -dictionary
			set idx 0
		}
	}
	lsort $order $mode -index $idx $newlist
}

proc ::ttk::dialog::file::datefmt {str} {
	clock format $str -format {%d-%m-%Y %H:%M}
}

proc ::ttk::dialog::file::modefmt {type mode} {
	switch $type {
		file {set rc -}
		default {set rc [string index $type 0]}
	}
	binary scan [binary format I $mode] B* bits
	foreach b [split [string range $bits end-8 end] ""] \
		c {r w x r w x r w x} {
		if {$b} {append rc $c} else {append rc -}
	}
	set rc
}

proc ::ttk::dialog::file::scrollhdr {w first last} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	lassign [$data(fileList) dlineinfo @0,0] x y width height base
	place $data(fileHdr) -x $x -width $width
	$data(long).x set $first $last
}

proc ::ttk::dialog::file::configure {w} {
	UpdateWhenIdle $w
}

proc ::ttk::dialog::file::setopt {w option var} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data
	upvar #0 $var value
	
	set data($option) $value
	UpdateWhenIdle $w	
}

proc ::ttk::dialog::file::UpDirCmd {w} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	ChangeDir $w [file dirname [lindex $data(history) $data(histpos)]]
}

proc ::ttk::dialog::file::PrevDirCmd {w} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	set data(selectFile) ""
	incr data(histpos) -1
	set data(selectPath) [lindex $data(history) $data(histpos)]
	$data(nextBtn) state !disabled
	if {!$data(histpos)} {
		$data(prevBtn) state disabled
	}
	Update $w
}

proc ::ttk::dialog::file::NextDirCmd {w} {
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	set data(selectFile) ""
	incr data(histpos)
	set data(selectPath) [lindex $data(history) $data(histpos)]
	$data(prevBtn) state !disabled
	if {$data(histpos) >= [llength $data(history)] - 1} {
		$data(nextBtn) state disabled
	}
	Update $w
}

proc ::ttk::dialog::file::HomeDirCmd {w} {
	ChangeDir $w ~
}

proc ::ttk::dialog::file::NewDirCmd {win} {
	set dataName [winfo name $win]
	upvar ::ttk::dialog::file::$dataName data

	set dir [lindex $data(history) $data(histpos)]

	toplevel $win.new
	wm title $win.new "New Folder"
	set w [ttk::frame $win.new.f]
	pack $w -expand 1 -fill both

	ttk::label $w.prompt -anchor w -justify left \
		-text "Create new folder in:\n$dir"
	ttk::entry $w.box -width 36 -validate all \
		-validatecommand [list ::ttk::dialog::file::NewDirVCmd $w %P]
	ttk::separator $w.sep
	set f [ttk::frame $w.buttons]
	ttk::button $f.clear -text Clear -takefocus 0 \
		-command [list $w.box delete 0 end]
	ttk::button $f.ok -text OK -default active \
		-command [list ::ttk::dialog::file::NewDirExit $win 1]
	ttk::button $f.cancel -text Cancel \
		-command [list ::ttk::dialog::file::NewDirExit $win]
	grid $f.clear $f.ok $f.cancel -padx 4 -pady {0 10} -sticky we
	grid columnconfigure $f {0 1 2} -uniform 1
	pack $w.prompt $w.box $w.sep $f \
		-side top -padx 12 -pady 3 -anchor w -fill x
	pack $w.prompt -pady {12 0}
	pack $f -anchor e -fill none -padx 8
	wm transient $win.new $win
	wm resizable $win.new 0 0
	wm protocol $win.new WM_DELETE_WINDOW [list $f.cancel invoke]

	bind $w.box <Return> [list $f.ok invoke]

	::tk::PlaceWindow $win.new widget $win
	::tk::SetFocusGrab $win.new $w.box
}

proc ::ttk::dialog::file::NewDirVCmd {w str} {
	if {[string length $str]} {
		$w.buttons.ok state !disabled
		$w.buttons.clear state !disabled
	} else {
		$w.buttons.ok state disabled
		$w.buttons.clear state disabled
	}
	return 1
}

proc ::ttk::dialog::file::NewDirExit {w {save 0}} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	if {$save} {
		set dir [lindex $data(history) $data(histpos)]
		set newdir [file join $dir [$w.new.f.box get]]
		if {[catch {file mkdir $newdir} err]} {
			ttk::messageBox -type ok -parent $w.new -icon error \
				-message "$err" -title Error
			return
		} else {
			ChangeDir $w $newdir
		}
	}
	destroy $w.new
	::tk::RestoreFocusGrab $w.new $w.new.f.box
}

proc ::ttk::dialog::file::Cancel {w} {
	variable selectFilePath ""
}

proc ::ttk::dialog::file::Done {w} {
	variable selectFilePath
	variable filelist
	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	if {![string length $data(selectFile)] || \
		[string equal $data(selectFile) .]} {
		return -code break
	}

	set cwd [lindex $data(history) $data(histpos)]
	set path [file join $cwd $data(selectFile)]

	if {[file isdirectory $path]} {
		ChangeDir $w $path
		return -code break
	}

	if {![string length [file extension $path]]} {
		append path $data(-defaultextension)
	}

	if {[file exists $path]} {
		if {[string equal $data(type) save]} {
			set reply [ttk::messageBox -icon warning -type yesno \
				-parent $w -title Warning -message "File\
				\"$path\" already exists.\nDo\
				you want to overwrite it?"]
			if {[string equal $reply "no"]} {return}
		}
	} else {
		if {[string equal $data(type) open]} {
			ttk::messageBox -icon warning -type ok -parent $w \
                            -title Error \
                            -message "File \"$path\" does not exist."
			return
		}
	}

	set idx [lsearch -exact $filelist $path]
	set filelist [linsert [lreplace $filelist $idx $idx] 0 $path]

	set selectFilePath $path
	return -code break
}

proc ::ttk::dialog::file::chdir {w} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	set dir $data(selectPath)
	if {[file isdirectory $dir]} {
		ChangeDir $w $dir
	} else {
		ttk::messageBox -type ok -parent $w \
			-message "Cannot change to the directory\
				\"$data(selectPath)\".\nPermission denied." \
			-icon warning -title Error
	}
	return -code break
}

proc ::ttk::dialog::file::SelectFilter {w} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	set data(filter) [lindex $data(-filetypes) \
		[$data(typeMenuBtn) current] 1]
	::ttk::dialog::file::UpdateWhenIdle $w
}

proc ::ttk::dialog::file::SetFilter {w} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	set data(filter) [$data(typeMenuBtn) get]
	::ttk::dialog::file::UpdateWhenIdle $w
	return -code break
}

proc ::ttk::dialog::file::DirButton1 {w x y} {
	scan [$w index @$x,$y] %d.%d line char
	$w tag remove sel 1.0 end
	$w tag add sel $line.2 $line.end
}

proc ::ttk::dialog::file::DirRelease1 {w x y} {
	set top [winfo toplevel $w]
	$top configure -cursor ""
}

proc ::ttk::dialog::file::DirDouble1 {w x y} {
	set dir [$w get sel.first sel.last]
	ChangeDir [winfo toplevel $w] $dir
}

proc ::ttk::dialog::file::DirMotion1 {w x y} {
	[winfo toplevel $w] configure -cursor "X_cursor #C00 #000"
}

proc ::ttk::dialog::file::FileButton1 {w x y} {
	set dataName [winfo name [winfo toplevel $w]]
	upvar ::ttk::dialog::file::$dataName data
	variable filetype

	if {[string equal $filetype none]} return

	set range [$w tag prevrange name @$x,$y+1c "@$x,$y linestart"]
	if {[llength $range]} {
		lassign $range index1 index2
		$w tag remove sel 1.0 end
		$w tag add sel $index1+2c $index2
		if {$filetype eq "file" || $filetype eq "link"} {
			set data(selectFile) [$w get sel.first sel.last]
		}
	}
}

proc ::ttk::dialog::file::FileRelease1 {w x y} {
	set dataName [winfo name [winfo toplevel $w]]
	upvar ::ttk::dialog::file::$dataName data
	variable filetype

	set top [winfo toplevel $w]
	if {[llength [$top cget -cursor]]} {
		# The mouse has been moved, don't perform the action
		$top configure -cursor ""
	} elseif {![string equal $filetype directory]} {
		# A file was selected
	} elseif {[llength [$w tag ranges sel]]} {
		set dir [$w get sel.first sel.last]
		ChangeDir [winfo toplevel $w] $dir
	}
	[winfo toplevel $w] configure -cursor ""
	set filetype none
}

proc ::ttk::dialog::file::FileMotion1 {w x y} {
	[winfo toplevel $w] configure -cursor "X_cursor #C00 #000"
}

proc ::ttk::dialog::file::tkFDialog {type arglist} {
	global env
	variable selectFilePath
	variable filelist
	set dataName __ttk_filedialog
	upvar ::ttk::dialog::file::$dataName data

	::ttk::dialog::file::Config $dataName $type $arglist

	if {[string equal $data(-parent) .]} {
		set w .$dataName
	} else {
		set w $data(-parent).$dataName
	}

	if {![winfo exists $w]} {
		::ttk::dialog::file::Create $w TkFDialog
	} elseif {![string equal [winfo class $w] TkFDialog]} {
		destroy $w
		::ttk::dialog::file::Create $w TkFDialog
	} else {
		$data(fileArea) configure -state normal
		$data(fileArea) delete 1.0 end
		$data(fileArea) configure -state disabled
		$data(dirArea) configure -state normal
		$data(dirArea) delete 1.0 end
		$data(dirArea) configure -state disabled
		$data(prevBtn) state disabled
		$data(nextBtn) state disabled
		$data(upBtn) state disabled
		set data(history) ""
		set data(histpos) -1
	}

	wm transient $w $data(-parent)

	if {[llength $data(-filetypes)]} {
		set titles ""
		foreach type $data(-filetypes) {
			lassign $type title filter
			lappend titles $title
		}
		$data(typeMenuBtn) configure -values $titles
		$data(typeMenuLab) state !disabled
		$data(typeMenuBtn) state !disabled
		$data(typeMenuBtn) current 0
		::ttk::dialog::file::SelectFilter $w
	} else {
		set data(filter) "*"
		$data(typeMenuBtn) configure -takefocus 0
		$data(typeMenuBtn) state disabled
		$data(typeMenuLab) state disabled
	}

	set dirlist "/"
	if {[info exists env(HOME)] && ![string equal $env(HOME) /]} {
		lappend dirlist $env(HOME)
	}
	if {[lsearch -exact $dirlist $data(selectPath)] < 0} {
		lappend dirlist $data(selectPath)
	}
	foreach n $filelist {
		set dir [file dirname $n]
		if {[lsearch -exact $dirlist $dir] < 0} {
			lappend dirlist $dir
		}
	}
	$data(dirMenuBtn) configure -values $dirlist
	$data(location) configure -values $filelist

	::ttk::dialog::file::ChangeDir $w $data(selectPath)

	::tk::PlaceWindow $w widget $data(-parent)
	wm title $w $data(-title)

	::tk::SetFocusGrab $w $data(location)

	tkwait variable ::ttk::dialog::file::selectFilePath

	::tk::RestoreFocusGrab $w $data(location) withdraw

	return $selectFilePath
}

proc ::ttk::dialog::file::Config {dataName type argList} {
	upvar ::ttk::dialog::file::$dataName data

	set data(type) $type

	# 1: the configuration specs
	#
	set specs {
		{-defaultextension "" "" ""}
		{-filetypes "" "" ""}
		{-initialdir "" "" ""}
		{-initialfile "" "" ""}
		{-parent "" "" "."}
		{-title "" "" ""}
		{-sepfolders "" "" 1}
		{-foldersfirst "" "" 1}
		{-sort "" "" "name"}
		{-reverse "" "" 0}
		{-details "" "" 0}
		{-hidden "" "" 0}
	}

	# 2: default values depending on the type of the dialog
	#
	if {![info exists data(selectPath)]} {
		# first time the dialog has been popped up
		set data(selectPath) [pwd]
		set data(selectFile) ""
	}

	# 3: parse the arguments
	#
	tclParseConfigSpec ::ttk::dialog::file::$dataName $specs "" $argList

	if {$data(-title) == ""} {
		if {[string equal $type "save"]} {
			set data(-title) "Save As"
		} else {
			set data(-title) "Open"
		}
	}

	# 4: set the default directory and selection according to the -initial
	#    settings
	#

	# Ensure that initialdir is an absolute path name.
	if {[string length $data(-initialdir)]} {
		set dir [file normalize [file join [pwd] $data(-initialdir)]]
		if {[string equal [file type $dir] "link"]} {
			set dir [file normalize [file join $dir [file link $dir]]]
		}
		if {[file isdirectory $dir]} {
			set data(selectPath) $dir
		} else {
			set data(selectPath) [pwd]
		}
	}
	set data(selectFile) $data(-initialfile)

	# 5. Parse the -filetypes option
	#
	set data(-filetypes) [::tk::FDGetFileTypes $data(-filetypes)]

	if {![winfo exists $data(-parent)]} {
		error "bad window path name \"$data(-parent)\""
	}

	variable sepfolders $data(-sepfolders)
	variable foldersfirst $data(-foldersfirst)
	variable sort $data(-sort)
	variable reverse $data(-reverse)
	variable details $data(-details)
	variable hidden $data(-hidden)
}

### ttk::chooseDirectory

proc ::ttk::dialog::file::treeCreate {w} {
	destroy $w
	toplevel $w -class TkChooseDir
	wm iconname $w Dialog

	set dataName [winfo name $w]
	upvar ::ttk::dialog::file::$dataName data

	if {[winfo viewable [winfo toplevel $data(-parent)]] } {
		wm transient $w $data(-parent)
	}

	set f1 [ttk::frame $w.f1]
	set data(dirMenuBtn) [ttk::combobox $f1.dir \
		-textvariable ::ttk::dialog::file::${dataName}(selectPath)]
	pack $f1.dir -fill x -expand 1 -padx 8 -pady 5

	set f2 [ttk::frame $w.f2]
	ttk::frame $f2.f
	ttk::label $f2.f.bg -relief sunken
	set font TkDefaultFont
	destroy $f2.f.dummy
	ttk::label $f2.f.title -text Folder -anchor w -style Toolbutton
	set data(text) [text $f2.f.text -width 48 -height 16 -font $font \
		-tabs 20 -wrap none -highlightthickness 0 -bd 0 -cursor "" \
		-spacing1 1 -spacing3 1 -exportselection 0 \
		-yscrollcommand [list $f2.f.scroll set]]
	$data(text) mark set subdir end
	$data(text) mark gravity subdir left
	ttk::scrollbar $f2.f.scroll -command [list $data(text) yview]
	grid $f2.f.title $f2.f.scroll -sticky ns
	grid $f2.f.text ^ -sticky news -padx {2 0} -pady {0 2}
	grid $f2.f.title -padx {2 0} -pady {2 1} -sticky ew
	grid $f2.f.bg -column 0 -row 0 -columnspan 2 -rowspan 2 -sticky news
	grid columnconfigure $f2.f 0 -weight 1
	grid rowconfigure $f2.f 1 -weight 1
	pack $f2.f -fill both -expand 1 -padx 8 -pady 4

	set f3 [ttk::frame $w.f3]
	ttk::button $f3.ok -text OK -default active \
		-command [list ::ttk::dialog::file::TreeDone $w]
	ttk::button $f3.cancel -text Cancel \
		-command [list ::ttk::dialog::file::Cancel $w]
	grid x $f3.ok $f3.cancel -sticky ew -padx {4 8} -pady 8
	grid columnconfigure $f3 {1 2} -uniform buttons -minsize 80
	grid columnconfigure $f3 0 -weight 1

	pack $f1 -side top -fill x
	pack $f3 -side bottom -fill x
	pack $f2 -side top -fill both -expand 1

	$data(text) image create end -padx 1 \
		-image ::ttk::dialog::image::folder 
	$data(text) insert end " /" name
	$data(text) configure -state disabled

	# Get rid of the default Text bindings
	bindtags $data(text) [list $data(text) DirDialog $w all]

	bind $data(dirMenuBtn) <Return> \
		[list ::ttk::dialog::file::TreeReturn $w]

	wm protocol $w WM_DELETE_WINDOW [list $f3.cancel invoke]
}

proc ::ttk::dialog::file::treeUpdate {w dir} {
	upvar ::ttk::dialog::file::[winfo name $w](text) txt

	set dir [file normalize [file join [pwd] $dir]]
	set list [lassign [file split $dir] parent]
	lappend list .
	$txt configure -state normal
	$txt delete 1.end end
	$txt mark set subdir end

	foreach d $list {
		treeOpen $w $parent subdir $d
		set parent [file join $parent $d]
	}
	$txt yview subdir-5l
	TreeSelect $w subdir
}

proc ::ttk::dialog::file::treeOpen {w path {index insert} {subdir .}} {
	upvar ::ttk::dialog::file::[winfo name $w](text) txt

	set level [llength [file split $path]]
	set tabs [string repeat "\t" [expr {$level - 1}]]
	set img [lindex [$txt dump -image \
		"$index linestart" "$index lineend"] 1]
	if {[string length $img] && \
		[string equal [$txt image cget $img -name] diropen]} {
		$txt image configure $img -image ::ttk::dialog::image::dirclose
	} else {
		set img ""
	}

	# Do we already have this data available, but perhaps elided?
	if {[llength [$txt tag ranges $path]]} {
		# Also show all subdirectories that were expanded before
		set list [lsearch -all -inline [$txt tag names] $path/*]
		foreach n [lappend list $path] {
			$txt tag configure $n -elide 0
		}
		return
	}

	# This may take a little longer so give some indication to the user
	$w configure -cursor watch
	update

	$txt configure -state normal
	$txt mark set insert $index
	set list [glob -nocomplain -tails -dir $path -type d * .*]
	foreach d [lsort -dictionary $list] {
		# Skip . and ..
		if {[string equal $d .] || [string equal $d ..]} continue
		# Specify no tags so the tags at the current position are used
		$txt insert insert "\n"
		# Insert the line with the appropriate tags
		$txt insert insert $tabs [list $path]
		file stat [file join $path $d] stat
		if {$stat(nlink) != 2} {
			set img [$txt image create insert -name diropen \
				-image ::ttk::dialog::image::diropen -padx 3]
			$txt tag add $path $img
		}
		$txt insert insert "\t" [list $path]
		set img [$txt image create insert -padx 1 \
			-image ::ttk::dialog::image::folder]
		$txt tag add $path $img
		$txt insert insert " $d" [list name $path]
		# Remove tags from the lineend
		foreach n [$txt tag names insert] {
			$txt tag remove $n insert
		}
		# Add the correct tag to the lineend
		$txt tag add $path insert
		# Put a mark if this is the specified subdirectory
		if {[string equal $d $subdir]} {
			$txt mark set subdir insert
		}
	}
	# Directory is considered empty if it only contains . and ..
	if {[llength $list] <= 2 && [string length $img]} {
		$txt delete $img
	}
	$txt configure -state disabled
	$w configure -cursor ""
}

proc ::ttk::dialog::file::treeClose {w path} {
	upvar ::ttk::dialog::file::[winfo name $w](text) txt

	set img root
	set pathindex [lindex [$txt tag ranges $path] 0]
	lassign [$txt dump -image "$pathindex-1l" $pathindex] - img pos
	if {[string match diropen* $img]} {
		$txt image configure $img -image ::ttk::dialog::image::diropen
	}

	set list [lsearch -all -inline [$txt tag names] $path/*]
	lappend list $path
	$txt configure -state normal
	foreach n $list {
		# Eliding sounds promising, but doesn't work correctly
		# $txt tag configure $n -elide 1
		eval [list $txt delete] [$txt tag ranges $n]
		$txt tag delete $n
	}
	$txt configure -state disabled
}

proc ::ttk::dialog::file::TreeDone {w} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	if {[file exists $data(selectPath)]} {
		if {![file isdirectory $data(selectPath)]} {
			return
		}
	} elseif {[string is true $data(-mustexists)]} {
		return
	}
	variable selectFilePath $data(selectPath)
}

proc ::ttk::dialog::file::cdTree {w dir {subdir .}} {
	upvar ::ttk::dialog::file::[winfo name $w](text) txt

	set parent [file dirname $dir]

	set ranges [$txt tag ranges $parent]
	if {[llength $ranges]} {
		set pat [format {^\t* %s$} [file tail $dir]]
		foreach {index1 index2} $ranges {
			set idx [$txt search -regexp $pat $index1 $index2]
			if {[string length $idx]} {
				$txt mark set subdir "$idx lineend"
				break
			}
		}
	} else {
		cdTree $w $parent [file tail $dir]
	}
	::ttk::dialog::file::treeOpen $w $dir subdir $subdir
}

proc ::ttk::dialog::file::TreeSelect {w index} {
	upvar ::ttk::dialog::file::[winfo name [winfo toplevel $w]] data

	set idx [$data(text) index "$index lineend"]
	set range [$data(text) tag prevrange name $idx "$idx linestart"]
	if {[llength $range]} {
		lassign $range index1 index2
		$data(text) tag remove sel 1.0 end
		$data(text) tag add sel $index1-1c $index2+1c
		set path [lsearch -inline [$data(text) tag names $index1] /*]
		set dir [$data(text) get $index1+1c $index2]
		set data(selectPath) [file join $path $dir]
	}
}

proc ::ttk::dialog::file::TreeRelease1 {w} {
	set w [winfo toplevel $w]
	upvar ::ttk::dialog::file::[winfo name $w](text) txt

	if {[string length [$w cget -cursor]]} {
		$w configure -cursor ""
		return
	}

	set dir [string range [$txt get sel.first sel.last] 1 end-1]
	set path [lsearch -inline [$txt tag names sel.first] /*]
	if {![catch {$txt image cget sel.first-2c -image} name]} {
		set index [$txt index sel.last-1c]
		$txt mark set selmark sel.first
		switch -glob $name {
			*::diropen {
				treeOpen $w [file join $path $dir] $index
			}
			*::dirclose {
				treeClose $w [file join $path $dir]
			}
		}
		$txt tag remove sel 1.0 end
		$txt tag add sel selmark "selmark lineend+1c"
	}
}

proc ::ttk::dialog::file::TreeMotion1 {w} {
	[winfo toplevel $w] configure -cursor "X_cursor #C00 #000"
}

proc ::ttk::dialog::file::TreeReturn {w} {
	upvar ::ttk::dialog::file::[winfo name $w] data

	if {[file isdirectory $data(selectPath)]} {
		::ttk::dialog::file::cdTree $w $data(selectPath)
		$data(text) yview subdir-5l
		TreeSelect $w subdir
	}

	return -code break
}

proc ttk::chooseDirectory {args} {
	set dataName __ttk_dirdialog
	upvar ::ttk::dialog::file::$dataName data

	set specs {
		{-initialdir "" "" .}
		{-mustexists "" "" 0}
		{-parent "" "" .}
		{-title "" "" ""}
    	}
	tclParseConfigSpec ::ttk::dialog::file::$dataName $specs "" $args

	if {$data(-title) == ""} {
		set data(-title) "[::tk::mc "Choose Directory"]"
	}

	if {![winfo exists $data(-parent)]} {
		error "bad window path name \"$data(-parent)\""
	}

	if {[string equal $data(-parent) .]} {
		set w .$dataName
	} else {
		set w $data(-parent).$dataName
	}

	if {![winfo exists $w]} {
		::ttk::dialog::file::treeCreate $w
	}

	::tk::PlaceWindow $w widget $data(-parent)
	wm title $w $data(-title)
	::tk::SetFocusGrab $w $data(text)

	::ttk::dialog::file::treeUpdate $w $data(-initialdir)

	tkwait variable ::ttk::dialog::file::selectFilePath

	::tk::RestoreFocusGrab $w $data(text) withdraw

	return $::ttk::dialog::file::selectFilePath
}

# Alternative procedure names
interp alias {} ttk_getOpenFile {} ::ttk::dialog::file::tkFDialog open
interp alias {} ttk_getSaveFile {} ::ttk::dialog::file::tkFDialog save
interp alias {} ttk_getAppendFile {} ::ttk::dialog::file::tkFDialog append


# Need to have a lassign procedure
if {![llength [info procs lassign]]} {
	proc lassign {list args} {
		uplevel 1 [list foreach $args $list break]
		lrange $list [llength $args] end
	}
}

# option add *TkFDialog*selectBackground #0a5f89
# option add *TkFDialog*selectForeground #ffffff
option add *TkFDialog*Toolbar*takeFocus 0
option add *TkFDialog*Text.background white
# option add *TkFDialog*Menu.activeBackground #0a5f89
# option add *TkFDialog*Menu.activeForeground #ffffff
# option add *TkFDialog*Menu.activeBorderWidth 1
# option add *TkFDialog*Menu.borderWidth 1
# option add *TkFDialog*Menu.relief solid
# option add *TkFDialog*Menu.Image ::ttk::dialog::image::blank16
# option add *TkFDialog*Menu*selectImage ::ttk::dialog::image::tick16

# Bindings
bind FileDialogDir <ButtonPress-1> {::ttk::dialog::file::DirButton1 %W %x %y}
bind FileDialogDir <ButtonRelease-1> {::ttk::dialog::file::DirRelease1 %W %x %y}
bind FileDialogDir <Double-1> {::ttk::dialog::file::DirDouble1 %W %x %y}
bind FileDialogDir <B1-Motion> {::ttk::dialog::file::DirMotion1 %W %x %y}
bind FileDialogDir <4> {%W yview scroll -5 units}
bind FileDialogDir <5> {%W yview scroll 5 units}
bind FileDialogFile <ButtonPress-1> {::ttk::dialog::file::FileButton1 %W %x %y}
bind FileDialogFile <ButtonRelease-1> {::ttk::dialog::file::FileRelease1 %W %x %y}
bind FileDialogFile <B1-Motion> {::ttk::dialog::file::FileMotion1 %W %x %y}
bind FileDialogFile <Double-1> {::ttk::dialog::file::Done [winfo toplevel %W]}
bind FileDialogFile <4> {%W xview scroll -10 units}
bind FileDialogFile <5> {%W xview scroll 10 units}
bind FileDialogList <ButtonPress-1> {::ttk::dialog::file::FileButton1 %W %x %y}
bind FileDialogList <ButtonRelease-1> {::ttk::dialog::file::FileRelease1 %W %x %y}
bind FileDialogList <B1-Motion> {::ttk::dialog::file::FileMotion1 %W %x %y}
bind FileDialogList <Double-1> {::ttk::dialog::file::Done [winfo toplevel %W]}
bind FileDialogList <4> {%W yview scroll -5 units}
bind FileDialogList <5> {%W yview scroll 5 units}

bind DirDialog <4> {%W yview scroll -5 units}
bind DirDialog <5> {%W yview scroll 5 units}
bind DirDialog <ButtonPress-1> {::ttk::dialog::file::TreeSelect %W @%x,%y}
bind DirDialog <ButtonRelease-1> {::ttk::dialog::file::TreeRelease1 %W}
bind DirDialog <B1-Motion> {::ttk::dialog::file::TreeMotion1 %W}
