#!/usr/bin/env python3
import unittest

from pycotap import LogMode, TAPTestRunner

suite = unittest.TestLoader().discover('.')
TAPTestRunner(LogMode.LogToError).run(suite)
