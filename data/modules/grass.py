# Copyright (C) 2022 DaFluffyPotato
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import random
import math
from copy import deepcopy

import engine


def normalize(val, amt, target):
    if val > target + amt:
        val -= amt
    elif val < target - amt:
        val += amt
    else:
        val = target
    return val


class Grass:
    def __init__(
        self,
        tile_size=15,
        shade_amount=100,
        stiffness=360,
        max_unique=10,
        place_range=[1, 1],
        padding=13,
    ):
        self.tile_size = tile_size
        self.shade_amount = shade_amount
        self.stiffness = stiffness
        self.max_unique = max_unique
        self.vertical_place_range = place_range
        self.padding = padding
        self._initialize_runtime()

    def enable_ground_shadows(
        self,
        shadow_strength=40,
        shadow_radius=2,
        shadow_color=(0, 0, 1),
        shadow_shift=(0, 0),
    ):
        if shadow_color == (0, 0, 0):
            shadow_color = (0, 0, 1)
        self.ground_shadow = [
            shadow_radius,
            shadow_color,
            shadow_strength,
            shadow_shift,
        ]

    def get_format(self, format_id, data, tile_id):
        if format_id not in self.formats:
            self.formats[format_id] = {"count": 1, "data": [(tile_id, data)]}
        elif self.formats[format_id]["count"] >= self.max_unique:
            return deepcopy(random.choice(self.formats[format_id]["data"]))
        else:
            self.formats[format_id]["count"] += 1
            self.formats[format_id]["data"].append((tile_id, data))

    def place_tile(self, location, density):
        grass_options = list(range(0, len(self.ga.blades)))
        if tuple(location) not in self.grass_tiles:
            self.grass_tiles[tuple(location)] = GrassTile(
                self.tile_size,
                (location[0] * self.tile_size, location[1] * self.tile_size),
                density,
                grass_options,
                self.ga,
                self,
            )

    def apply_force(self, location, radius, dropoff):
        location = (int(location[0]), int(location[1]))
        grid_pos = (
            int(location[0] // self.tile_size),
            int(location[1] // self.tile_size),
        )
        tile_range = math.ceil((radius + dropoff) / self.tile_size)
        for y in range(tile_range * 2 + 1):
            y = y - tile_range
            for x in range(tile_range * 2 + 1):
                x = x - tile_range
                pos = (grid_pos[0] + x, grid_pos[1] + y)
                if pos in self.grass_tiles:
                    self.grass_tiles[pos].apply_force(location, radius, dropoff)

    def update(self):
        scene = engine.Scene.manager.scene
        if not hasattr(scene, "dt"):
            return  # change scene catche
        for tile in self.grass_tiles.values():
            tile.update(scene.dt)

    def draw(self, surf, offset=(0, 0)):
        visible_tile_range = (
            int(surf.get_width() // self.tile_size) + 1,
            int(surf.get_height() // self.tile_size) + 1,
        )
        base_pos = (int(offset[0] // self.tile_size), int(offset[1] // self.tile_size))

        render_list = []
        for y in range(visible_tile_range[1]):
            for x in range(visible_tile_range[0]):
                pos = (base_pos[0] + x, base_pos[1] + y)
                if pos in self.grass_tiles:
                    render_list.append(pos)

        if self.ground_shadow[0]:
            shadow_offset = (
                offset[0] - self.ground_shadow[3][0],
                offset[1] - self.ground_shadow[3][1],
            )
            for pos in render_list:
                self.grass_tiles[pos].render_shadow(surf, offset=shadow_offset)

        for pos in render_list:
            tile = self.grass_tiles[pos]
            tile.render(surf, offset=offset)

    def _initialize_runtime(self):
        self.ga = GrassAssets(self)
        self.grass_id = 0
        self.grass_cache = {}
        self.shadow_cache = {}
        self.formats = {}
        self.grass_tiles = {}
        self.ground_shadow = [0, (0, 0, 0), 100, (0, 0)]


class GrassAssets:
    def __init__(self, gm):
        self.gm = gm
        self.blades = engine.Assets.get("custom", "grass")
        self.blades = list(self.blades.values())

    def render_blade(self, surf, blade_id, location, rotation):
        rot_img = engine._pygame.transform.rotate(self.blades[blade_id], rotation)
        shade = engine._pygame.Surface(rot_img.get_size())
        shade_amt = self.gm.shade_amount * (abs(rotation) / 90)
        shade.set_alpha(shade_amt)
        rot_img.blit(shade, (0, 0))
        surf.blit(
            rot_img,
            (
                location[0] - rot_img.get_width() // 2,
                location[1] - rot_img.get_height() // 2,
            ),
        )


class GrassTile:
    def __init__(self, tile_size, location, amt, config, ga, gm):
        self.ga = ga
        self.gm = gm
        self.loc = location
        self.size = tile_size
        self.blades = []
        self.master_rotation = 0
        self.precision = 30
        self.padding = self.gm.padding
        self.inc = 90 / self.precision

        y_range = self.gm.vertical_place_range[1] - self.gm.vertical_place_range[0]
        for i in range(amt):
            new_blade = random.choice(config)
            y_pos = self.gm.vertical_place_range[0]
            if y_range:
                y_pos = random.random() * y_range + self.gm.vertical_place_range[0]
            self.blades.append(
                [
                    (random.random() * self.size, y_pos * self.size),
                    new_blade,
                    random.random() * 30 - 15,
                ]
            )

        self.blades.sort(key=lambda x: x[1])

        self.base_id = self.gm.grass_id
        self.gm.grass_id += 1

        format_id = (amt, tuple(config))
        overwrite = self.gm.get_format(format_id, self.blades, self.base_id)
        if overwrite:
            self.blades = overwrite[1]
            self.base_id = overwrite[0]

        self.custom_blade_data = None
        self.update_render_data()

    def apply_force(self, force_point, force_radius, force_dropoff):
        if not self.custom_blade_data:
            self.custom_blade_data = [None] * len(self.blades)

        for i, blade in enumerate(self.blades):
            dis = math.sqrt(
                (self.loc[0] + blade[0][0] - force_point[0]) ** 2
                + (self.loc[1] + blade[0][1] - force_point[1]) ** 2
            )
            if dis < force_radius:
                force = 2
            else:
                dis = max(0, dis - force_radius)
                force = 1 - min(dis / force_dropoff, 1)
            dir = 1 if force_point[0] > (self.loc[0] + blade[0][0]) else -1
            if (
                not self.custom_blade_data[i]
                or abs(self.custom_blade_data[i][2] - self.blades[i][2])
                <= abs(force) * 90
            ):
                self.custom_blade_data[i] = [
                    blade[0],
                    blade[1],
                    blade[2] + dir * force * 90,
                ]

    def update_render_data(self):
        self.render_data = (self.base_id, self.master_rotation)
        self.true_rotation = self.inc * self.master_rotation

    def set_rotation(self, rotation):
        self.master_rotation = rotation
        self.update_render_data()

    def render_tile(self, render_shadow=False):
        surf = engine._pygame.Surface(
            (self.size + self.padding * 2, self.size + self.padding * 2)
        )
        surf.set_colorkey((0, 0, 0))

        blades = self.custom_blade_data if self.custom_blade_data else self.blades

        if render_shadow:
            shadow_surf = engine._pygame.Surface(surf.get_size())
            shadow_surf.set_colorkey((0, 0, 0))
            for blade in self.blades:
                engine._pygame.draw.circle(
                    shadow_surf,
                    self.gm.ground_shadow[1],
                    (blade[0][0] + self.padding, blade[0][1] + self.padding),
                    self.gm.ground_shadow[0],
                )
            shadow_surf.set_alpha(self.gm.ground_shadow[2])

        for blade in blades:
            self.ga.render_blade(
                surf,
                blade[1],
                (blade[0][0] + self.padding, blade[0][1] + self.padding),
                max(-90, min(90, blade[2] + self.true_rotation)),
            )

        return (surf, shadow_surf) if render_shadow else surf

    def render_shadow(self, surf, offset=(0, 0)):
        if self.gm.ground_shadow[0] and (self.base_id in self.gm.shadow_cache):
            surf.blit(
                self.gm.shadow_cache[self.base_id],
                (
                    self.loc[0] - offset[0] - self.padding,
                    self.loc[1] - offset[1] - self.padding,
                ),
            )

    def render(self, surf, offset=(0, 0)):
        if self.custom_blade_data:
            surf.blit(
                self.render_tile(),
                (
                    self.loc[0] - offset[0] - self.padding,
                    self.loc[1] - offset[1] - self.padding,
                ),
            )
        else:
            if (self.render_data not in self.gm.grass_cache) and (
                self.gm.ground_shadow[0] and (self.base_id not in self.gm.shadow_cache)
            ):
                grass_img, shadow_img = self.render_tile(render_shadow=True)
                self.gm.grass_cache[self.render_data] = grass_img
                self.gm.shadow_cache[self.base_id] = shadow_img
            elif self.render_data not in self.gm.grass_cache:
                self.gm.grass_cache[self.render_data] = self.render_tile()
            surf.blit(
                self.gm.grass_cache[self.render_data],
                (
                    self.loc[0] - offset[0] - self.padding,
                    self.loc[1] - offset[1] - self.padding,
                ),
            )

    def update(self, dt):
        if self.custom_blade_data:
            matching = True
            for i, blade in enumerate(self.custom_blade_data):
                blade[2] = normalize(
                    blade[2], self.gm.stiffness * dt, self.blades[i][2]
                )
                if blade[2] != self.blades[i][2]:
                    matching = False
            if matching:
                self.custom_blade_data = None
