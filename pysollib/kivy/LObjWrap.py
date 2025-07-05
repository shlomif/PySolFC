#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-
# =============================================================================
# Copyright (C) 2017-2023 LB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Flake8: noqa
#
# =============================================================================

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty
from kivy.properties import StringProperty

# =============================================================================
# Joins kivy properties to object members of referenced class.
# Usage:
# - use derived classes LBoolWrap etc. according to type.
# - write:  obj.value = <new value>
# - read:   <actual value> = obj.value
# - If you need additional functionality on change add a callback function
#   as 'command'. It will be called  whenever the value changes.

class LObjWrap(EventDispatcher):
    def __init__(self,obj,ref=None,command=None):
        self.obj = obj
        self.ref = ref
        if self.ref is not None:
            self.value = getattr(self.obj,self.ref)
            # logging.info("LObjWrap: setup for %s" % (self.ref))
            self.bind(value=self.on_value)
        if command is not None:
            self.bind(value=command)

    def on_value(self,inst,val):
        # logging.info("LObjWrap: %s = %s" % (self.ref,val))
        if self.ref is not None:
            setattr(self.obj,self.ref,val)

class LBoolWrap(LObjWrap):
    value = BooleanProperty(False)

class LNumWrap(LObjWrap):
    value = NumericProperty(0)

class LStringWrap(LObjWrap):
    value = StringProperty('')

class LListWrap(LObjWrap):
    value = ListProperty([])

# =============================================================================
