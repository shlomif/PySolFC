#! /usr/bin/env python3
# -*- coding: iso-8859-1 -*-

import sys
import os
import requests
import logging
import hashlib
import glob
from zipfile import ZipFile, ZipInfo
from clint.textui import progress

cachefiles = [
  ('https://dl.google.com/android/repository/platform-tools-latest-linux.zip',
   '',
   'platform-tools'),
  ('https://dl.google.com/android/repository/tools_r25.2.5-linux.zip',
   '577516819c8b5fae680f049d39014ff1ba4af870b687cab10595783e6f22d33e',
   'tools'),
  ('https://dl.google.com/android/repository/android-19_r04.zip',
   '5efc3a3a682c1d49128daddb6716c433edf16e63349f32959b6207524ac04039',
   'platform'),
  ('https://dl.google.com/android/repository/build-tools_r26-linux.zip',
   '7422682f92fb471d4aad4c053c9982a9a623377f9d5e4de7a73cd44ebf2f3c61',
   'build-tools'),
  ('https://dl.google.com/'
   'android/repository/android-ndk-r12b-linux-x86_64.zip',
   'eafae2d614e5475a3bcfd7c5f201db5b963cc1290ee3e8ae791ff0c66757781e',
   'ndk'),
]

# https://stackoverflow.com/questions/39296101:


class MyZipFile(ZipFile):

    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        ret_val = self._extract_member(member, path, pwd)
        attr = member.external_attr >> 16
        os.chmod(ret_val, attr)
        return ret_val

# Reused from fdroidserver:


def sha256_for_file(path):
    with open(path, 'rb') as f:
        s = hashlib.sha256()
        while True:
            data = f.read(4096)
            if not data:
                break
            s.update(data)
        return s.hexdigest()

# Adapted from fdroidserver:


def update_cache(cachedir, cachefiles):
    for srcurl, shasum, typ in cachefiles:
        filename = os.path.basename(srcurl)
        local_filename = os.path.join(cachedir, filename)

        if os.path.exists(local_filename):
            local_length = os.path.getsize(local_filename)
        else:

            local_length = -1

        if (typ == 'ndk') and (ndkloc is not None):
            continue
        elif (typ != 'tools') and (sdkloc is not None):
            continue

        resume_header = {}
        download = True

        try:
            r = requests.head(srcurl, allow_redirects=True, timeout=60)
            if r.status_code == 200:
                content_length = int(r.headers.get('content-length'))
            else:
                content_length = local_length  # skip the download
        except requests.exceptions.RequestException as e:
            content_length = local_length  # skip the download
            logger.warn('%s', e)

        if local_length == content_length:
            download = False
        elif local_length > content_length:
            logger.info('deleting corrupt file from cache: %s',
                        local_filename)
            os.remove(local_filename)
            logger.info("Downloading %s to cache", filename)
        elif local_length > -1 and local_length < content_length:
            logger.info("Resuming download of %s", local_filename)
            resume_header = {
                'Range': 'bytes=%d-%d' % (local_length, content_length)}
        else:
            logger.info("Downloading %s to cache", filename)

        if download:
            r = requests.get(srcurl, headers=resume_header,
                             stream=True, verify=False, allow_redirects=True)
            content_length = int(r.headers.get('content-length'))
            with open(local_filename, 'ab') as f:
                for chunk in progress.bar(
                        r.iter_content(chunk_size=65536),
                        expected_size=(content_length / 65536) + 1):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        if not shasum == '':
            v = sha256_for_file(local_filename)
            if v == shasum:
                logger.info("Shasum verified for %s", local_filename)
            else:
                logger.critical(
                  "Invalid shasum of '%s' detected for %s", v, local_filename)
                os.remove(local_filename)
                sys.exit(1)

# Build the sdk from zips.


def build_sdk(sdkdir, cachedir, cachfiles):
    for srcurl, shasum, typ in cachefiles:
        filename = os.path.basename(srcurl)
        local_filename = os.path.join(cachedir, filename)

        if typ == 'tools':
            if os.path.exists(local_filename):
                print('Extract: %s' % local_filename)
                zf = MyZipFile(local_filename)
                zf.extractall(sdkdir)
        elif typ == 'platform-tools':
            if (sdkloc is None) and (os.path.exists(local_filename)):
                print('Extract: %s' % local_filename)
                zf = MyZipFile(local_filename)
                zf.extractall(sdkdir)
            else:
                print('Link to: %s' % sdkloc)
                os.symlink(sdkloc + '/platform-tools',
                           sdkdir + '/platform-tools')
        elif typ == 'platform':
            if (sdkloc is None) and (os.path.exists(local_filename)):
                print('Extract: %s' % local_filename)
                zf = MyZipFile(local_filename)
                zf.extractall(sdkdir + '/platforms')
            else:
                print('Link to: %s' % sdkloc)
                os.symlink(sdkloc + '/platforms', sdkdir + '/platforms')
        elif typ == 'build-tools':
            if (sdkloc is None) and (os.path.exists(local_filename)):
                print('Extract: %s' % local_filename)
                zf = MyZipFile(local_filename)
                zf.extractall(sdkdir + '/build-tools')
            else:
                print('Link to: %s' % sdkloc)
                os.symlink(sdkloc + '/build-tools', sdkdir + '/build-tools')
        elif typ == 'ndk':
            if ndkloc is None:
                print('Extract: %s' % local_filename)
                zf = MyZipFile(local_filename)
                zf.extractall(sdkdir)
                lst = glob.glob(sdkdir + '/*-ndk-*')
                print(lst)
                os.rename(lst[0], sdkdir + '/ndk-bundle')
            else:
                print('Link to: %s' % ndkloc)
                os.symlink(ndkloc, sdkdir + '/ndk-bundle')


logger = logging.getLogger('prepare-fdroid-build')
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger.setLevel(logging.INFO)

# command line arguments

sdkloc = None
ndkloc = None
if len(sys.argv) > 1:
    sdkloc = sys.argv[1]
    if (len(sdkloc) > 0) and (sdkloc[-1] == '/'):
        sdkloc = sdkloc[:-1]
    if not os.path.isdir(sdkloc):
        sdkloc = None

if len(sys.argv) > 2:
    ndkloc = sys.argv[2]
    if (len(ndkloc) > 0) and (ndkloc[-1] == '/'):
        ndkloc = ndkloc[:-1]
    if not os.path.isdir(ndkloc):
        ndkloc = None

fdroidmode = None
if len(sys.argv) > 3:
    fdroidmode = sys.argv[3]
    if (len(fdroidmode) > 0):
        fdroidmode = '1'

if sdkloc == "":
    sdkloc = None
if ndkloc == "":
    ndkloc = None

logger.info('sdkloc = %s' % sdkloc)
logger.info('ndkloc = %s' % ndkloc)

# sdkloc and ndkloc already set by the user and fdroidmode:
# nothing to do.

if (sdkloc is not None) and (ndkloc is not None) and (fdroidmode is not None):
    sys.exit(0)

# cache dir (using the same as in fdroidserver/buildserver)
cachedir = os.path.join(os.getenv('HOME'), '.cache', 'fdroidserver')
logger.info('cachedir name is: %s', cachedir)

if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0o755)
    logger.info('created cachedir %s', cachedir)

# sdkdir location
sdkdir = os.path.join(os.getenv('HOME'), '.cache', 'sdk-for-p4a')
logger.info('sdkdir name is: %s', sdkdir)

if not os.path.exists(sdkdir):
    os.makedirs(sdkdir, 0o755)
    logger.debug('created sdkdir %s', sdkdir)

    update_cache(cachedir, cachefiles)
    build_sdk(sdkdir, cachedir, cachefiles)
else:
    logger.info('sdkdir %s already exists', sdkdir)
