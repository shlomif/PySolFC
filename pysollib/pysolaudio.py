## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports
import os, sys
import traceback

try:
    import thread
    from threading import Thread
except ImportError:
    thread = None

try:
    import pysolsoundserver
except ImportError:
    pysolsoundserver = None


# /***********************************************************************
# // basic audio client
# ************************************************************************/

class AbstractAudioClient:
    def __init__(self):
        self.server = None
        self.audiodev = None
        self.connected = 0
        self.app = None
        self.sample_priority = -1
        self.sample_loop = 0
        self.music_priority = -1
        self.music_loop = 0

    def __del__(self):
        self.destroy()

    # start server - set self.server on success (may also set self.audiodev)
    def startServer(self):
        pass

    # connect to server - set self.audiodev on success
    def connectServer(self, app):
        assert app
        self.app = app
        if self.server is not None:
            try:
                if self._connectServer():
                    self.connected = 1
            except:
                if traceback: traceback.print_exc()
                self.destroy()

    # disconnect and stop server
    def destroy(self):
        if self.audiodev is not None:
            try:
                self._destroy()
            except:
                pass
        self.server = None
        self.audiodev = None
        self.connected = 0
        self.app = None

    #
    # high-level interface
    #

    def stopAll(self):
        self.stopSamples()
        self.stopMusic()

    def playSample(self, name, priority=0, loop=0, volume=-1):
        ##print 'AbstractAudioClient.playSample', name
        if self.audiodev is None or not self.app or not self.app.opt.sound:
            return 0
        if priority <= self.sample_priority and self.sample_loop:
            return 0
        obj = self.app.sample_manager.getByName(name)
        if not obj or not obj.absname:
            return 0
        try:
            if self._playSample(obj.absname, priority, loop, volume):
                self.sample_priority = priority
                self.sample_loop = loop
                return 1
        except:
            if traceback: traceback.print_exc()
        return 0

    def stopSamples(self):
        if self.audiodev is None:
            return
        try:
            self._stopSamples()
        except:
            if traceback: traceback.print_exc()
        self.sample_priority = -1
        self.sample_loop = 0

    def stopSamplesLoop(self):
        if self.audiodev is None:
            return
        try:
            self._stopSamplesLoop()
        except:
            if traceback: traceback.print_exc()
        self.sample_priority = -1
        self.sample_loop = 0

    def playMusic(self, basename, priority=0, loop=0, volume=-1):
        if self.audiodev is None or not self.app or not self.app.opt.sound:
            return 0
        if priority <= self.music_priority and self.music_loop:
            return 0
        obj = self.app.music_manager.getByBasename(basename)
        if not obj or not obj.absname:
            return 0
        try:
            if self._playMusic(obj.absname, priority, loop, volume):
                self.music_priority = priority
                self.music_loop = loop
                return 1
        except:
            if traceback: traceback.print_exc()
        return 0

    def stopMusic(self):
        if self.audiodev is None:
            return
        try:
            self._stopMusic()
        except:
            if traceback: traceback.print_exc()
        self.music_priority = -1
        self.music_loop = 0

    #
    # subclass - core implementation
    #

    def _connectServer(self):
        return 0

    def _destroy(self):
        pass

    def _playSample(self, filename, priority, loop, volume):
        return 0

    def _stopSamples(self):
        pass

    def _stopSamplesLoop(self):
        self._stopSamples()

    def _playMusic(self, name, priority, loop, volume):
        return 0

    def _stopMusic(self):
        pass

    #
    # subclass - extensions
    #

    def getMusicInfo(self):
        return -1

    def playContinuousMusic(self, music_list):
        pass

    def playNextMusic(self):
        pass

    def updateSettings(self):
        pass


# /***********************************************************************
# // pysolsoundserver module
# ************************************************************************/

class PysolSoundServerModuleClient(AbstractAudioClient):
    def startServer(self):
        # use the module
        try:
            self.audiodev = pysolsoundserver
            self.audiodev.init()
            self.server = 1         # success - see also tk/menubar.py
        except:
            if traceback: traceback.print_exc()
            self.server = None
            self.audiodev = None

    def cmd(self, cmd):
        return self.audiodev.cmd(cmd)

    # connect to server
    def _connectServer(self):
        r = self.cmd("protocol 6")
        if r != 0:
            return 0
        if 0 and self.app.debug:
            self.cmd("debug 1")
        return 1

    # disconnect and stop server
    def _destroy(self):
        self.audiodev.exit()

    #
    #
    #

    def _playSample(self, filename, priority, loop, volume):
        self.cmd("playwav '%s' %d %d %d %d" % (filename, -1, priority, loop, volume))
        return 1

    def _stopSamples(self):
        self.cmd("stopwav")

    def _stopSamplesLoop(self):
        self.cmd("stopwavloop")

    def _playMusic(self, filename, priority, loop, volume):
        self.cmd("playmus '%s' %d %d %d %d" % (filename, -1, priority, loop, volume))
        return 1

    def _stopMusic(self):
        self.cmd("stopmus")

    def getMusicInfo(self):
        if self.audiodev:
            return self.audiodev.getMusicInfo()
        return -1

    def playContinuousMusic(self, music_list):
        if self.audiodev is None or not self.app:
            return
        try:
            loop = 999999
            for music in music_list:
                if music.absname:
                    self.cmd("queuemus '%s' %d %d %d %d" % (music.absname, music.index, 0, loop, music.volume))
            self.cmd("startqueue")
        except:
            if traceback: traceback.print_exc()

    def playNextMusic(self):
        self.cmd("nextmus")

    def updateSettings(self):
        if self.audiodev is None or not self.app:
            return
        s, m = 0, 0
        if self.app.opt.sound:
            s = self.app.opt.sound_sample_volume
            m = self.app.opt.sound_music_volume
        try:
            self.cmd("setwavvol %d" % s)
            self.cmd("setmusvol %d" % m)
        except:
            if traceback: traceback.print_exc()


# /***********************************************************************
# // Win32 winsound audio
# ************************************************************************/

class Win32AudioClient(AbstractAudioClient):
    def startServer(self):
        # use the built-in winsound module
        try:
            import winsound
            self.audiodev = winsound
            del winsound
            self.server = 0         # success - see also tk/menubar.py
        except:
            self.server = None
            self.audiodev = None

    def _playSample(self, filename, priority, loop, volume):
        a = self.audiodev
        flags = a.SND_FILENAME | a.SND_NODEFAULT | a.SND_NOWAIT | a.SND_ASYNC
        if loop:
            flags = flags | a.SND_LOOP
        if priority <= self.sample_priority:
            flags = flags | a.SND_NOSTOP
        ###print filename, flags, priority
        try:
            a.PlaySound(filename, flags)
            return 1
        except: pass
        return 0

    def _stopSamples(self):
        a = self.audiodev
        flags = a.SND_NODEFAULT | a.SND_PURGE
        a.PlaySound(None, flags)


# /***********************************************************************
# // OSS audio
# ************************************************************************/

#import wave, ossaudiodev

class OSSAudioServer:

    def __init__(self, pipe):
        import ossaudiodev
        self.pipe = pipe
        #self.audiodev = ossaudiodev.open('w')

    def mainLoop(self):
        while True:
            s = os.read(self.pipe, 256)
            ss = s.split('\0', 2)
            if not ss[0]:
                os._exit(0)
            if ss[0] == 'break':
                self._play_loop = False
                continue
            filename, loop = ss[0], int(ss[1])
            if loop:
                self._play_loop = True
                th = Thread(target=self.playLoop, args=(filename,))
                th.start()
            else:
                self.play(filename)

    def _getParameters(self, filename):
        import ossaudiodev, wave
        w = wave.open(filename)
        fmt = ossaudiodev.AFMT_U8
        nch = w.getnchannels()
        rate = w.getframerate()
        frames = w.readframes(w.getnframes())
        return (frames, fmt, nch, rate)

    def playLoop(self, filename, priority=None):
        ##print '_playLoop:', filename
        import ossaudiodev, wave
        try:
            #audiodev = self.audiodev
            audiodev = ossaudiodev.open('w')
            #audiodev.nonblock()
            frames, fmt, nch, rate = self._getParameters(filename)
            audiodev.setparameters(fmt, nch, rate)
            while self._play_loop:
                audiodev.write(frames)
            audiodev.reset()
            #audiodev.close()
            #self.audiodev = ossaudiodev.open('w')
            return 1
        except:
            if traceback: traceback.print_exc()
            return 0

    def play(self, filename, priority=None):
        ##print '_play:', filename
        import ossaudiodev, wave
        try:
            #audiodev = self.audiodev
            audiodev = ossaudiodev.open('w')
            #audiodev.nonblock()
            frames, fmt, nch, rate = self._getParameters(filename)
            audiodev.setparameters(fmt, nch, rate)
            audiodev.write(frames)
            #audiodev.close()
            #self.audiodev = ossaudiodev.open('w')
            return 1
        except:
            if traceback: traceback.print_exc()
            return 0


class OSSAudioClient(AbstractAudioClient):

    def __init__(self):
        AbstractAudioClient.__init__(self)

    def startServer(self):
        try:
            import ossaudiodev, wave
            self.server = 0         # success - see also tk/menubar.py
            self.audiodev = ossaudiodev
            pin, pout = os.pipe()
            self.pout = pout
            server = OSSAudioServer(pin)
            pid = os.fork()
            if pid == 0:
                server.mainLoop()
        except:
            if traceback: traceback.print_exc()
            self.server = None
            self.audiodev = None


    def _playSample(self, filename, priority, loop, volume):
        ##print '_playSample:', filename, loop
        os.write(self.pout, '%s\0%s\0' % (filename, loop))
        return 1

    def _stopSamples(self):
        os.write(self.pout, 'break\0\0')

    def _destroy(self):
        os.write(self.pout, '\0\0')

