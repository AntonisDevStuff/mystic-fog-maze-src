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

from .display import Display
from .wrapper import vector

from math import log2

import pygame


class Camera:
    def __init__(self):
        self._pos = vector(0, 0)
        self._offset = vector(0, 0)
        self._zoom_scale = 1
        self._zoom_factor = 0
        self._zoom_direction = 0
        self.__max_zoom_factor = 3
        self.zoom(1)

    @property
    def surface(self):
        return Display.surface

    @property
    def position(self):
        return self._pos.copy()

    @property
    def rect(self):
        rect = pygame.Rect(self._pos + self._offset, Display._res)
        rect.width = int(rect.width / self.zoom_scale)
        rect.height = int(rect.height / self.zoom_scale)
        return rect

    @property
    def zoom_scale(self):
        return self._zoom_scale

    @property
    def zoom_factor(self):
        return self._zoom_factor

    @property
    def zoom_direction(self):
        return self._zoom_direction

    @property
    def zoom_level(self):
        if self.zoom_direction == 0 and self.zoom_factor == 0:
            return 1
        elif self.zoom_factor == 0:
            return 1
        elif self.zoom_factor >= 1:
            return self.zoom_factor + 1
        else:
            return self.zoom_factor - 1

    def set_max_zoom(self, factor):
        self.__max_zoom_factor = factor

    def get_max_zoom(self):
        return self.__max_zoom_factor

    def is_visible(self, obj):
        return self.rect.colliderect(obj.rect)

    def move(self, offset):
        self._pos.x += offset[0]
        self._pos.y += offset[1]

    def move_at(self, new_pos):
        self._pos.x = new_pos[0] + Display._res[0] / 2
        self._pos.y = new_pos[1] + Display._res[1] / 2

    def zoom(self, factor):
        if factor == 0:
            return
        factor = (factor + 1) if factor < 0 else (factor - 1)
        scale = 2 ** (self.zoom_factor + factor)
        self.zoom_at(scale)

    def zoom_at(self, scale):
        if not scale:
            return
        min_scale = 2**-self.__max_zoom_factor
        max_scale = 2**self.__max_zoom_factor
        scale = max(min_scale, min(max_scale, scale))
        factor = log2(scale)
        direction = factor - self._zoom_factor

        sign = 1 if scale < 0 else -1
        self._offset.x = 1 / scale * Display._res[0] / 2 * sign + Display._res[0] / 2
        self._offset.y = 1 / scale * Display._res[1] / 2 * sign + Display._res[1] / 2

        self._zoom_scale = scale
        self._zoom_factor = factor
        self._zoom_direction = direction

    def draw_shape(self, shape, fill=0):
        if not self.is_visible(shape):
            return

        shape._pos -= self._pos + self._offset
        shape._pos *= self._zoom_scale
        shape.draw(self.surface, fill, self._zoom_scale)
        shape._pos /= self._zoom_scale
        shape._pos += self._offset + self._pos

    def draw_text(self, txt):
        if not self.is_visible(txt):
            return

        txt._pos -= self._pos + self._offset
        txt._pos *= self._zoom_scale
        txt.draw(self.surface, self._zoom_scale)
        txt._pos /= self._zoom_scale
        txt._pos += self._offset + self._pos

    def draw_image(self, image):
        if not self.is_visible(image):
            return
        image._pos -= self._pos + self._offset
        image._pos *= self._zoom_scale
        image.draw(self.surface, self._zoom_scale)
        image._pos /= self._zoom_scale
        image._pos += self._offset + self._pos

    def draw_surface(self, surface):
        if not self.is_visible(surface):
            return
        surface._pos -= self._pos + self._offset
        surface._pos *= self._zoom_scale
        surface.draw(self.surface, self._zoom_scale)
        surface._pos /= self._zoom_scale
        surface._pos += self._offset + self._pos
