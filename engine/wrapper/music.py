# Mystic Fog Maze (Source Code)
# Copyright (C) 2026 AntonisDevStuff

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame


class Music:
    _volume = 1.0
    _active = None

    def __init__(self, path, volume=1.0):
        self._path = path
        self._local_volume = volume

    @property
    def playing(self):
        if self is not Music._active:
            return False
        return pygame.mixer.music.get_busy()

    @property
    def time(self):
        if self is not Music._active:
            return 0
        return pygame.mixer.music.get_pos() / 1000

    @property
    def volume(self):
        return self._volume * self._local_volume

    @property
    def metadata(self):
        return pygame.mixer.music.get_metadata(self._path)

    @classmethod
    def change_volume(cls, value):
        cls._volume = value
        cls._active and pygame.mixer.music.set_volume(cls._active.volume)

    def change_local_volume(self, value):
        self._local_volume = value
        pygame.mixer.music.set_volume(self.volume)

    def play(self, loops=0, start=0.0, fade_ms=0):
        pygame.mixer.music.load(self._path)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(loops, start, fade_ms)
        Music._active = self

    def resume(self):
        pygame.mixer.music.unpause()

    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        Music._active = None
