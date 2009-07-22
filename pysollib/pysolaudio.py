#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##


# imports
import os
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


# ************************************************************************
# * basic audio client
# ************************************************************************

class AbstractAudioClient:

    EXTENSIONS = r"\.((wav)|(it)|(mod)|(mp3)|(pym)|(s3m)|(xm))$"

    CAN_PLAY_SOUND = False
    CAN_PLAY_MUSIC = False

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
        if self.audiodev:
            self._destroy()
        self.server = None
        self.audiodev = None
        self.connected = 0
        self.app = None

    #
    # high-level interface
    #

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


# ************************************************************************
# * pysolsoundserver module
# ************************************************************************

class PysolSoundServerModuleClient(AbstractAudioClient):

    CAN_PLAY_SOUND = True
    CAN_PLAY_MUSIC = True

    def __init__(self):
        AbstractAudioClient.__init__(self)
        import pysolsoundserver

    def startServer(self):
        # use the module
        try:
            self.audiodev = pysolsoundserver
            self.audiodev.init()
            self.server = 1
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
        ##self.cmd("debug 1")
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


# ************************************************************************
# * Win32 winsound audio
# ************************************************************************

class Win32AudioClient(AbstractAudioClient):

    CAN_PLAY_SOUND = True
    CAN_PLAY_MUSIC = False

    def __init__(self):
        AbstractAudioClient.__init__(self)
        import winsound
        self.audiodev = winsound

    def startServer(self):
        pass

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


# ************************************************************************
# * OSS audio
# ************************************************************************

class OSSAudioServer:

    def __init__(self, pipe):
        self.pipe = pipe
        #import ossaudiodev
        #self.audiodev = ossaudiodev.open('w')
        self.sound_priority = -1
        self._busy = False

    def mainLoop(self):
        while True:
            s = os.read(self.pipe, 256)
            ss = s.split('\0')
            if not ss[0]:
                os._exit(0)
            if ss[0] == 'break':
                self._play_loop = False
                continue
            filename, priority, loop = ss[0], int(ss[1]), int(ss[2])
            if loop:
                self._play_loop = True
                th = Thread(target=self.playLoop, args=(filename,))
                th.start()
            else:
                if not self._busy:
                    self.play(filename, priority)

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

    def play(self, filename, priority):
        ##print '_play:', filename
        import ossaudiodev, wave
        try:
            self._busy = True
            #audiodev = self.audiodev
            audiodev = ossaudiodev.open('w')
            #audiodev.nonblock()
            frames, fmt, nch, rate = self._getParameters(filename)
            audiodev.setparameters(fmt, nch, rate)
            audiodev.write(frames)
            #audiodev.close()
            #self.audiodev = ossaudiodev.open('w')
            self.sound_priority = priority
            self._busy = False
            return 1
        except:
            if traceback: traceback.print_exc()
            self._busy = False
            return 0


class OSSAudioClient(AbstractAudioClient):

    CAN_PLAY_SOUND = True
    CAN_PLAY_MUSIC = False

    def __init__(self):
        AbstractAudioClient.__init__(self)
        import ossaudiodev, wave
        self.audiodev = ossaudiodev

    def startServer(self):
        pin, pout = os.pipe()
        self.pout = pout
        server = OSSAudioServer(pin)
        pid = os.fork()
        if pid == 0:
            server.mainLoop()

    def _playSample(self, filename, priority, loop, volume):
        ##print '_playSample:', filename, loop
        os.write(self.pout, '%s\0%s\0%s\0' % (filename, priority, loop))
        return 1

    def _stopSamples(self):
        os.write(self.pout, 'break\0\0\0')

    def _destroy(self):
        os.write(self.pout, '\0\0\0')


# ************************************************************************
# * PyGame
# ************************************************************************

class PyGameAudioClient(AbstractAudioClient):

    EXTENSIONS = r'\.((ogg)|(mp3)|(wav)|(it)|(mod)|(s3m)|(xm)|(mid)|(midi))$'

    CAN_PLAY_SOUND = True
    CAN_PLAY_MUSIC = True

    def __init__(self):
        AbstractAudioClient.__init__(self)
        import pygame.mixer, pygame.time
        if os.name == 'nt':
            # for py2exe
            import pygame.base, pygame.rwobject, pygame.mixer_music
        self.mixer = pygame.mixer
        self.time = pygame.time
        self.music = self.mixer.music
        self.audiodev = self.mixer
        self.sound = None
        self.sound_channel = None
        self.sound_priority = -1

    def startServer(self):
        pass

    def connectServer(self, app):
        AbstractAudioClient.connectServer(self, app)
        ## http://www.pygame.org/docs/ref/mixer.html
        ## NOTE: there is currently a bug on some windows machines which
        ## makes sound play back 'scratchy'. There is not enough cpu in
        ## the sound thread to feed the buffer to the sound api. To get
        ## around this you can increase the buffer size. However this
        ## means that there is more of a delay between the time you ask to
        ## play the sound and when it gets played. Try calling this before
        ## the pygame.init or pygame.mixer.init calls.
        ## pygame.mixer.pre_init(44100,-16,2, 1024 * 3)
        #self.mixer.pre_init(44100, -16, 2, 1024 * 3)
        buff_size = self.app.opt.sound_sample_buffer_size
        self.mixer.pre_init(44100, -16, 2, 1024*buff_size)
        self.mixer.init()

    def _playSample(self, filename, priority, loop, volume):
        ##print '_playSample:', filename, priority, loop, volume
        if self.sound_channel and self.sound_channel.get_busy():
            if self.sound_priority >= priority:
                return 0
            else:
                self.sound.stop()
        vol = self.app.opt.sound_sample_volume/128.0
        try:
            self.sound = self.mixer.Sound(filename)
            self.sound.set_volume(vol)
            self.sound_channel = self.sound.play(loop)
        except:
            if traceback: traceback.print_exc()
            pass
        self.sound_priority = priority
        return 1

    def _stopSamples(self):
        if self.sound:
            self.sound.stop()
        self.sound = None
        self.sound_channel = None

    def _playMusicLoop(self):
        ##print '_playMusicLoop'
        music_list = self.music_list
        if not music_list:
            return
        while True:
            if not self.music:
                break
            for m in music_list:
                if not self.music:
                    break
                vol = self.app.opt.sound_music_volume/128.0
                try:
                    self.music.load(m.absname)
                    self.music.set_volume(vol)
                    self.music.play()
                    while self.music and self.music.get_busy():
                        self._wait(200)
                    self._wait(300)
                except:
                    ##if traceback: traceback.print_exc()
                    self._wait(1000)

    def _destroy(self):
        self.mixer.stop()
        self.mixer.quit()
        self.music = None

    def _wait(self, s):
        # sometime time or time.wait is None (threading)
        if self.time and self.time.wait:
            self.time.wait(s)

    def playContinuousMusic(self, music_list):
        ##print 'playContinuousMusic'
        self.music_list = music_list
        #if self.audiodev is None or not self.app:
        #    return
        if not music_list:
            return
        th = Thread(target=self._playMusicLoop)
        th.start()

    def updateSettings(self):
        if not self.app.opt.sound or self.app.opt.sound_music_volume == 0:
            if self.music:
                self.music.stop()
                self.music = None
        else:
            if not self.music:
                self.music = self.mixer.music
                th = Thread(target=self._playMusicLoop)
                th.start()
            else:
                vol = self.app.opt.sound_music_volume/128.0
                self.music.set_volume(vol)

    def playNextMusic(self):
        if self.music:
            self.music.stop()

