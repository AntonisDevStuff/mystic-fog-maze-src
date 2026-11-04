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

from abc import ABC, abstractmethod
from math import ceil

import pygame


class Shape(ABC):
    def __init__(self, pos, color):
        self._pos = vector(*pos)
        self._color = color

    @property
    def position(self):
        return self._pos.copy()

    @property
    def color(self):
        return self._color

    @property
    @abstractmethod
    def rect(self):
        pass

    @abstractmethod
    def draw(self, surf, fill, scale):
        pass

    def move(self, pos):
        self._pos.x += pos[0]
        self._pos.y += pos[1]

    def move_at(self, pos):
        self._pos.x = pos[0]
        self._pos.y = pos[1]


class Rect(Shape):
    def __init__(self, pos, size, color):
        super().__init__(pos, color)
        self._size = tuple(size)

    @property
    def size(self):
        return self._size

    @property
    def rect(self):
        if all(
            isinstance(i, int)
            for i in (self._pos[0], self._pos[1], self._size[0], self._size[1])
        ):
            return pygame.Rect(self._pos, self._size)
        return pygame.FRect(self._pos, self._size)

    def draw(self, surf, fill, scale):
        rect = self.rect
        color = self.color
        fill *= scale
        rect.width *= scale
        rect.height *= scale
        fill = ceil(fill)
        pygame.draw.rect(surf, color, rect, width=fill if fill > 0 else 0)


class Circle(Shape):
    def __init__(
        self,
        pos,
        radius,
        color,
    ):
        super().__init__(pos, color)
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @property
    def rect(self):
        pos = (
            self._pos[0] - self.radius,
            self._pos[1] - self.radius,
        )
        size = (self.radius * 2, self.radius * 2)
        return pygame.Rect(pos, size)

    def draw(self, surf, fill, scale):
        pos = self._pos
        fill *= scale
        radius = self.radius * scale
        fill = ceil(fill)
        pygame.draw.circle(surf, self.color, pos, radius, width=fill if fill > 0 else 0)
