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


class SoundEffect:
    _volume = 1.0

    def __init__(self, effect, volume=1.0):
        self._effect = effect
        self._local_volume = volume

    @property
    def playing(self):
        return bool(self._effect.get_num_channels())

    @property
    def channels(self):
        return self._effect.get_num_channels()

    @property
    def length(self):
        return self._effect.get_length()

    @property
    def raw(self):
        return self._effect.get_raw()

    @property
    def volume(self):
        return self._volume * self._local_volume

    @classmethod
    def change_volume(cls, value):
        cls._volume = value

    def change_local_volume(self, value):
        self._local_volume = value

    def play(self, loops=0, maxtime=0, fade_ms=0):
        self._effect.stop()
        self._effect.set_volume(self.volume)
        self._effect.play(loops, maxtime, fade_ms)

    def stop(self):
        self._effect.stop()
