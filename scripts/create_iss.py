#!/usr/bin/env python

prog_name = 'PySol Fan Club edition'

import os

dirs_list = []
files_list = []
for root, dirs, files in os.walk('dist'):
    if files:
        files_list.append(root)
    dirs_list.append(root)

execfile(os.path.join('pysollib', 'settings.py'))
prog_version = VERSION

out = open('setup.iss', 'w')

print >> out, '''
[Setup]
AppName=%(prog_name)s
AppVerName=%(prog_name)s v.%(prog_version)s
DefaultDirName={pf}\\%(prog_name)s
DefaultGroupName=%(prog_name)s
UninstallDisplayIcon={app}\\pysol.exe
Compression=lzma
SolidCompression=yes
SourceDir=dist
OutputDir=.
OutputBaseFilename=PySolFC_%(prog_version)s_setup

[Icons]
Name: "{group}\\%(prog_name)s"; Filename: "{app}\\pysol.exe"
Name: "{group}\\Uninstall %(prog_name)s"; Filename: "{uninstallexe}"
Name: "{userdesktop}\\%(prog_name)s"; Filename: "{app}\\pysol.exe"
''' % vars()

print >> out, '[Dirs]'
for d in dirs_list[1:]:
    print >> out, 'Name: "{app}%s"' % d.replace('dist', '')

print >> out
print >> out, '[Files]'
print >> out, 'Source: "*"; DestDir: "{app}"'
for d in files_list[1:]:
    d = d.replace('dist\\', '')
    print >> out, 'Source: "%s\\*"; DestDir: "{app}\\%s"' % (d, d)


