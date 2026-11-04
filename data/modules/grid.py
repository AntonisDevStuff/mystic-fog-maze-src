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

import engine


class Cell:
    index = {
        -1: "red",
        0: "black",
        1: "white",
        2: "green",
        3: "blue",
        4: "darkgreen",
        5: "yellow",
        6: "purple",
        7: "gray",
    }

    def __init__(self, pos, state):
        self._state = state
        self._pos = engine.vector(*pos)
        self._rect = None

    @property
    def position(self):
        return self._pos.copy()

    @property
    def state(self):
        return self._state

    @property
    def rect(self):
        return self._rect

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def color(self):
        return self.index.get(self._state, "black")

    def draw(self, surface, pos, size):
        self._rect = engine._pygame.Rect(pos, size)
        engine._pygame.draw.rect(surface, self.color, self._rect, 0)


class Line:
    def __init__(self, start, end, color="black", width=1):
        self._start = engine.vector(*start)
        self._end = engine.vector(*end)
        self._color = color
        self._width = width

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    def draw(self, surface):
        engine._pygame.draw.line(
            surface, self._color, self._start, self._end, self._width
        )


class Grid:
    def __init__(self, data, size, lines, pos=None, renderer=engine.Display):
        self._map = data
        self._line_width = lines
        self._renderer = renderer
        pos = (0, 0) if not pos else pos
        self._initialize_runtime(size, pos)

    @property
    def cells(self):
        return self._cells

    @property
    def surface(self):
        return self._surface

    @property
    def cell_size(self):
        return self._cell_size

    @property
    def columns(self):
        return self._cols

    @property
    def rows(self):
        return self._rows

    @property
    def offset(self):
        return self._offset.copy()

    @offset.setter
    def offset(self, value):
        self._offset.x = value[0]
        self._offset.y = value[1]

    @property
    def line_color(self):
        return self._line_color

    @line_color.setter
    def line_color(self, value):
        self._line_color = value
        for line in self._lines:
            line.color = value

    @property
    def line_width(self):
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        self._line_width = value
        for line in self._lines:
            line.width = value

    def get(self, col, row):
        key = (col, row)
        try:
            cell = self._cells[key]
        except KeyError:
            cell = None
        return cell

    def cell(self, position):
        px = position[0] - self._offset[0]
        py = position[1] - self._offset[1]
        if px < 0 or py < 0:
            return None
        x = int(px // self._cell_size[0])
        y = int(py // self._cell_size[1])
        return self.get(x, y)

    def create(self, need_offset=True):
        self._surface.clear()
        surf = self._surface.value

        x, y = self._cell_size

        for (col, row), cell in self._cells.items():
            cell.draw(surf, (col * x, row * y), self._cell_size)

        for line in self._lines:
            line.draw(surf)

        self._surface.update()

        self._cache_surface = self._surface.value.copy()

        need_offset and self._surface.move(self._offset)

    def clear(self):
        self._surface.clear()

    def reset(self):
        surface = self._cache_surface.copy()
        self._surface._surface = surface
        self._surface._cached_surface = surface

    def update(self):
        self._surface.update()

    def draw(self):
        self._renderer.draw_surface(self._surface)

    def _initialize_cells(self):
        self._cells = {
            (col, row): Cell((col, row), state=self._map[row][col])
            for row in range(self._rows)
            for col in range(self._cols)
        }

    def _initialize_lines(self, width, height):
        cell_w = int(self._cell_size[0])
        cell_h = int(self._cell_size[1])

        for col in range(self._cols + 1):
            x = col * cell_w
            self._lines.append(
                Line((x, 0), (x, height), self._line_color, self._line_width)
            )

        for row in range(self._rows + 1):
            y = row * cell_h
            self._lines.append(
                Line((0, y), (width, y), self._line_color, self._line_width)
            )

    def _initialize_runtime(self, size, pos):
        self._cols = len(self._map[0])
        self._rows = len(self._map)
        self._cell_size = engine.vector(size[0] // self._cols, size[1] // self._rows)
        self._offset = engine.vector(0, 0)
        self._cells = {}
        self._lines = []
        self._line_color = "black"

        self._surface = engine.Surface(size, pos=pos)

        self._initialize_cells()
        self._initialize_lines(size[0], size[1])
