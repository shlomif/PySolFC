#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# ---------------------------------------------------------------------------##
#
#  Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
#  Copyright (C) 2003 Mt. Hood Playing Card Co.
#  Copyright (C) 2005-2009 Skomoroh
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------##

import gettext
import struct
import warnings
from pathlib import Path

def list_languages():
    # Get a list of languages in (name, code) pairs, from the
    # available language files.  Does not change the language.
    locale_dir = gettext.bindtextdomain("pysol")
    languages = []
    for catalog in Path(locale_dir).glob('*/LC_MESSAGES/pysol.mo'):
        code = catalog.parent.parent.name
        if code == 'en':
            continue
        try:
            with catalog.open('rb') as stream:
                metadata = gettext.GNUTranslations(stream).info()
        except (OSError, EOFError, ValueError, LookupError,
                struct.error) as error:
            warnings.warn('Skipping {}: {}'.format(catalog, error))
            continue
        label = metadata.get('x-pysol-language-name', '').strip()
        if not label:
            label = code
        languages.append((code, label))
    languages.append(('en', 'English'))
    languages.sort(key=lambda item: (item[1].casefold(), item[0]))
    return languages
