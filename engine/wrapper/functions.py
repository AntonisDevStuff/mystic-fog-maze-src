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

__all__ = ["vector", "rect"]


def vector(x, y, z=None):
    if z is not None:
        return pygame.math.Vector3(x, y, z)
    return pygame.math.Vector2(x, y)


def rect(pos, size):
    if all(isinstance(i, int) for i in (pos[0], pos[1], size[0], size[1])):
        return pygame.Rect(pos, size)
    return pygame.FRect(pos, size)
