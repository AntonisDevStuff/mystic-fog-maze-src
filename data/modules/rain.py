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

import random
import engine


class Rain:
    def __init__(self, amount, speed):
        self._amount = amount
        self._speed = speed
        self._initialize_runtime()

    @property
    def scene(self):
        return engine.Scene.manager.scene

    def update(self, dt):
        camera = self.scene.camera
        music = self.scene.music
        self.skip = False
        if camera.zoom_factor:
            camera.zoom_factor and music.playing and music.pause()
            self.skip = True
            return
        scene = self.scene
        left, top, right, bottom = self._get_grid_bounds()
        target_amount = random.randint(self._amount // 2, self._amount)

        while len(self._drops) < target_amount:
            width = self._drop[0]
            height = random.randint(self._drop[1] // 2, self._drop[1])
            pos = (
                random.randint(left + 40, right - 50),
                random.randint(top - 200, bottom),
            )
            self._drops.append(engine.Rect(pos, (width, height), "blue"))
        movement = (0, self._speed * dt * 60)

        for drop in self._drops:
            drop.move(movement)

        self._drops = [
            drop
            for drop in self._drops
            if drop.position[1] <= bottom - self._drop[1] - 25
        ]

        not music.playing and music.resume()

    def draw(self):
        if self.skip:
            return
        for drop in self._drops:
            engine.Display.draw_shape(drop)

    def _get_grid_bounds(self):
        scene = self.scene
        grid_width, grid_height = scene.grid_size
        offset_x, offset_y = scene.grid_offset

        left = scene.grid_map["center"][0] + offset_x

        right = scene.grid_map["center"][0] + offset_x + grid_width

        top = scene.grid_map["center"][1] + offset_y

        bottom = scene.grid_map["center"][1] + offset_y + grid_height

        return left, top, right, bottom

    def _initialize_runtime(self):
        self._drop = (4, 12)
        self._drops = []
        self.skip_draw = False
