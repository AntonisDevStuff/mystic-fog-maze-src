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
from ..assets import Assets

from collections import OrderedDict

import pygame

text_sizes = {
    1,
    2,
    4,
    8,
    10,
    12,
    14,
    16,
    18,
    24,
    32,
    48,
    64,
    72,
    96,
    128,
    144,
    192,
    256,
}


class Text:
    surfaces = OrderedDict()
    _cache_limit = 10000

    def __init__(
        self,
        text,
        pos,
        color,
        font_name=pygame.font.get_default_font().split(".")[0],
        size=24,
        align="left",
    ):
        size = self.__fix_size(size)
        font = self.__get_font(font_name, size)
        self._text = text
        self._pos = vector(*pos)
        self._color = color
        self._font_name = font_name
        self._font = font
        self._size = size
        self._zoom = 1
        self._zoom_surface = None
        (
            self._cache_surface()
            if (font, text, color) not in self.surfaces
            else setattr(self, "_surface", self.surfaces[(font, text, color)])
        )
        self._align_pos(align)

    @classmethod
    def set_cache(cls, new_limit):
        cls._cache_limit = new_limit

    @classmethod
    def get_cache(cls):
        return len(cls.surfaces)

    @classmethod
    def clear_cache(cls):
        cls.surfaces.clear()

    @classmethod
    def font_size_for(cls, text, size, font_name):
        width, height = size[0], size[1]
        font_type = "sys" if font_name.lower() in pygame.font.get_fonts() else "local"
        for font_size in text_sizes:
            font = cls.__get_font(font_name, font_size)
            text_surface = font.render(text, True, (0, 0, 0))
            text_width, text_height = text_surface.get_size()
            if text_width > width or text_height > height:
                return font_size - 1
        return font_size

    @property
    def position(self):
        return self._pos.copy()

    @property
    def value(self):
        return self._text

    @property
    def color(self):
        return self._color

    @property
    def font(self):
        return self._font_name

    @property
    def font_size(self):
        return self._size

    @property
    def size(self):
        return self._surface.get_size()

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
        zoom = scale
        if zoom == 1:
            surf.blit(self._surface, self._pos)
            return
        if not self._zoom == zoom:
            self._zoom_surface = pygame.transform.scale_by(self._surface, zoom)
            self._zoom = zoom
        surf.blit(self._zoom_surface, self._pos)

    def _cache_surface(self):
        self._surface = self._font.render(self._text, False, self._color)
        if len(self.surfaces) >= self._cache_limit:
            self.surfaces and self.surfaces.popitem(last=True)
        self.surfaces[(self._font, self._text, self._color)] = self._surface

    def _align_pos(self, align):
        if align == "left":
            return
        rect = self.rect
        if align == "center":
            self._pos.x -= rect.width / 2
        elif align == "right":
            self._pos.x += rect.width
        else:
            raise ValueError(f"Invalid alignment: {align}")

    @staticmethod
    def __get_font(font_name, size):
        font = Assets.get("data", "fonts", font_name)
        if not font:
            raise ValueError(f"Font '{font_name}' not found.")
        return font.get(size)

    @staticmethod
    def __fix_size(size):
        closest = min(text_sizes, key=lambda s: abs(s - size))
        if closest != size:
            return closest
        return size
