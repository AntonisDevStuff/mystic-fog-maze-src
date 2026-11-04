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


class Image:
    def __init__(
        self,
        image,
        pos,
        shape_type=1,
        align="left",
        custom_size=None,
    ):
        self._surface = image
        self._pos = vector(*pos)
        self._size = self.rect.size

        if custom_size:
            self._surface = pygame.transform.smoothscale(image, custom_size)

        if custom_size:
            self._size = custom_size

        self._scale = 1.0
        self._scale_surface = None

        shape_type == 2 and self.__apply_circular_mask()

        self.__apply_alignment(align)

    @property
    def position(self):
        return self._pos.copy()

    @property
    def size(self):
        return tuple(self._size)

    @property
    def shape(self):
        return self._shape

    @property
    def value(self):
        return self._surface.copy()

    @property
    def rect(self):
        _rect = self._surface.get_rect()
        _rect.x = self._pos[0]
        _rect.y = self._pos[1]
        return _rect

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

    def draw(self, surf, scale):
        if scale == 1:
            surf.blit(self._surface, self._pos)
            return

        if not self._scale == scale:
            self._scale_surface = pygame.transform.smoothscale_by(self._surface, scale)
            self._scale = scale

        surf.blit(self._scale_surface, self._pos)

    def __apply_circular_mask(self):
        mask = pygame.Surface(self._size, pygame.SRCALPHA)
        radius = self._size[0] // 2
        center = (radius, radius)
        pygame.draw.circle(mask, (255, 255, 255), center, radius)
        self._surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def __apply_alignment(self, align):
        align = align.lower().strip()
        rect = self.rect
        # Horizontal axis
        if "right" in align:
            self._pos.x -= rect.width
        elif "left" in align:
            pass
        elif "center" in align or "mid" in align:
            self._pos.x -= rect.width / 2

        # Vertical axis
        if "bottom" in align:
            self._pos.y -= rect.height
        elif "top" in align:
            pass
        elif "center" in align or "mid" in align:
            self._pos.y -= rect.height / 2
