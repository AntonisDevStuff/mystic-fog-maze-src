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

from .functions import vector

import pygame


class Surface:
    def __init__(self, size, pos=(0, 0)):
        self._surface = pygame.Surface(size)
        self._pos = vector(*pos)
        self._size = tuple(size)
        self._cached_surface = self._surface.copy()
        self._scale = 1.0
        self._scale_cache = None

    @property
    def position(self):
        return self._pos.copy()

    @property
    def size(self):
        return self._size

    @property
    def rect(self):
        _rect = self._surface.get_rect()
        _rect.x = self._pos[0]
        _rect.y = self._pos[1]
        return _rect

    @property
    def value(self):
        return self._surface

    @property
    def memory(self):
        bytes_per_pixel = self._surface.get_bytesize()
        width, height = self._surface.get_size()
        return width * height * bytes_per_pixel

    def move(self, pos):
        self._pos.x += pos[0]
        self._pos.y += pos[1]

    def move_at(self, pos):
        self._pos.x = pos[0]
        self._pos.y = pos[1]

    def fill(self, color):
        self._surface.fill(color)

    def update(self):
        self._cached_surface = self._surface.copy()
        self._scale_cache = None

    def draw(self, surf, scale=1.0):
        if scale == 1.0:
            surf.blit(self._cached_surface, self._pos)
            return

        if self._scale_cache is None or self._scale != scale:
            self._scale_cache = pygame.transform.smoothscale_by(
                self._cached_surface, scale
            )
            self._scale = scale

        surf.blit(self._scale_cache, self._pos)

    def blit(self, surface, pos):
        self._surface.blit(surface, pos)

    def clear(self, color=(0, 0, 0)):
        self.fill(color)

    def set_alpha(self, value):
        self._surface.set_alpha(value)

    def set_colorkey(self, color):
        self._surface.set_colorkey(color)

    def convert(self):
        self._surface = self._surface.convert()

    def convert_alpha(self):
        self._surface = self._surface.convert_alpha()
