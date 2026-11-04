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


class Explosive:
    @classmethod
    def init(cls, scene):
        cls.scene = scene
        cls.explosives = []

    @classmethod
    def create(cls, index):
        cls.explosives.append(Boom(cls, index))

    @classmethod
    def remove(cls, item):
        cls.explosives.remove(item)

    @classmethod
    def update(cls, dt):
        for i, explosive in enumerate(cls.explosives):
            explosive.update(dt)

    @classmethod
    def draw(cls):
        for i, explosive in enumerate(cls.explosives):
            explosive.draw()


class Boom:
    def __init__(self, manager, index):
        self.manager = manager
        self.index = index
        self._initialize_runtime()

    @property
    def cell(self):
        grid = self.manager.scene.grids.get(self._camera_loc)
        return grid.get(*self.index)

    @property
    def image(self):
        return self._frames[self._frame]

    def update(self, dt):
        self._animation_timer += dt

        frame_count = len(self._frames)
        frame_duration = 1 / (frame_count * self._animation_speed)
        if self._animation_timer >= frame_duration:
            self._animation_timer -= frame_duration
            self._frame += 1

            if self._frame > frame_count:
                self._frame = 1

        if self._frame == frame_count:
            self.manager.remove(self)
            self.sfx.play()
            self.cell.state = 4
            self.manager.scene.grids.get(self._camera_loc).create(need_offset=False)
            self.manager.scene.draw_fog(force=True)

    def draw(self):
        self.manager.scene.renderer.draw_image(self.image)

    def _initialize_runtime(self):
        self._frame = 1
        self._animation_timer = 0.0
        self._animation_speed = 0.9
        self._camera_loc = self.manager.scene.camera_loc

        self._frames = {frame: self.__load_image(frame) for frame in range(1, 9)}

        self.sfx = engine.SoundEffect(engine.Assets.get("sfx", "boom"), volume=0.8)

    def __load_image(self, frame):
        image = engine.Assets.get("images", f"explosive{frame}")

        cell = self.cell
        offset = (
            self.manager.scene.grid_offset[0]
            + self.manager.scene.grid_size[0] * self.manager.scene.camera_index[0],
            self.manager.scene.grid_offset[1]
            + self.manager.scene.grid_size[1] * self.manager.scene.camera_index[1],
        )
        pos = (
            cell.rect.x + offset[0] + cell.rect.width / 2,
            cell.rect.y + offset[1] + cell.rect.height / 2,
        )

        size = (cell.rect.width * 0.8, cell.rect.height * 0.8)

        return engine.Image(image, pos, custom_size=size, align="center")


class Player:
    Explosive = Explosive

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._initialize_runtime()
        Explosive.init(self.scene)

    @property
    def cell(self):
        grid = self.scene.grids.get(self.direction)
        return grid.get(*self.index)

    @property
    def camera(self):
        return self.direction

    @property
    def camera_index(self):
        return {
            "center": [0, 0],
            "up": [0, -1],
            "down": [0, 1],
            "left": [-1, 0],
            "right": [1, 0],
            "up-left": [-1, -1],
            "up-right": [1, -1],
            "down-left": [-1, 1],
            "down-right": [1, 1],
        }.get(self.direction)

    @property
    def moving(self):
        return self._moving

    @property
    def skipping(self):
        return self._skipping

    @property
    def path(self):
        return self._queue.copy()

    @property
    def image(self):
        return self._frames[self._looking][self._state][self._frame]

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.__load_frames()
        self.__update_frames()

    def update(self, dt):
        dt = min(0.032, max(0.001, dt))  # Clamp for big drops
        self._animation_timer += dt
        frame_count = len(self._frames[self._looking][self._state])
        if self._state == "death" and self._frame == frame_count:
            self.scene.manager.restart()
            return

        if self._state == "move" and self._frame == frame_count and self._queue:
            self._skipping = False
            self._queue and self.move(*self._queue)
            self.scene.draw_fog(force=True)
            return

        if self._state == "move" and self._frame == frame_count:
            self._state = "idle"
            self._animation_speed = 0.9
            self._moving = False
            self.scene.draw_fog(force=True)
            return

        frame_duration = 1 / (frame_count * self._animation_speed)
        if self._animation_timer >= frame_duration:
            self._animation_timer -= frame_duration
            self._frame += 1

            if self._frame > frame_count:
                self._frame = 1

        self.steps <= 0 and self._state != "death" and self.die()
        Explosive.update(dt)

    def draw(self):
        self.scene.renderer.draw_image(self.image)
        Explosive.draw()

    def die(self):
        self._state = "death"
        self._frame = 1
        self._animation_timer = 0.0
        self._animation_speed = 0.7
        self._sfx["death"].play()

    def explosive(self, index):
        for explosive in Explosive.explosives:
            if explosive._camera_loc != self.scene.camera_loc:
                continue
            if explosive.index == index:
                return
        Explosive.create(index)
        self.explosives -= 1

    def move(self, *data):
        if self._state == "move" and not self._queue:
            return

        if self._state == "death":
            return

        self._moving = True

        diff = self.index[0] - data[0][1]
        if self.index[0] - data[0][1]:
            camera = (
                self.scene.camera_moves[data[0][0]][0] * -1
                if data[0][0] != self.camera
                else self.index[0] - data[0][1]
            )
            self._looking = (
                "left" if camera > 0 else "right" if camera < 0 else self._looking
            )

        data = list(data)
        if not data:
            self._queue = []
            return

        loc, x, y = data.pop(0)

        self.index[0] = x
        self.index[1] = y

        self.direction = loc
        self.scene.move_to_player()

        self.scene.camera and self._overview(len(data) > 10)

        self._queue = data

        self._state = "move"
        self._frame = 1
        self._animation_timer = 0.0
        self._animation_speed = 1.5

        self.__update_frames()

        self._sfx["move"].play()
        self.steps -= 1

    def stop(self):
        self._queue = []
        self._skipping = False
        self._overview(False)
        self.scene.move_to_player()

    def skip(self):
        if self.skipping:
            return
        if len(self._queue) <= 2:
            return
        left = len(self._queue)
        skip_move = int(left / 2) + 1
        if self.steps - left < skip_move:
            return
        self._frame = 2
        self._queue = self._queue[skip_move : left + 1] if self._queue else []
        self._skipping = True
        self.steps -= left
        self._sfx["skip"].play()

    def is_visible(self, cords, camera_loc):
        if not self.fog:
            return True

        if self.camera != camera_loc and self.scene.camera_loc == camera_loc:
            x, y = cords
            for dx, dy in self.scene.camera_moves.values():
                for distance in range(1, 3):
                    next_pos = (
                        x + dx * distance,
                        y + dy * distance,
                    )
                    next_cell = self.scene.grids["center"].get(*next_pos)

                    if (
                        next_cell is not None
                        and next_cell.state == 5
                        and self.scale == 1
                    ):
                        return True
            return False

        if self.camera != camera_loc:
            return False

        return self._in_fog_radius(cords)

    def _overview(self, enabled):
        if enabled:
            for dir in ("up", "up", "left", "left", "down-right"):
                self.scene.move_camera(dir)

        target_scale = self.scene.grid.rows / 10 if enabled else 1
        if self.scale == target_scale:
            return

        self.scene.camera.zoom_at(-1 if enabled else 1)
        self.scale = target_scale

    def _in_fog_radius(self, cords):
        return (
            abs(cords[0] - self.index[0]) <= self.fog
            and abs(cords[1] - self.index[1]) <= self.fog
        )

    def _initialize_runtime(self):
        self._state = "idle"
        self._looking = "right"
        self._frame = 1
        self._scale = 1
        self._animation_timer = 0.0
        self._animation_speed = 0.9
        self._skipping = False
        self._moving = False
        self._queue = []
        self._frames = {}
        self._sfx = {}

        self.__load_frames()
        self.__load_sfx()

    def __load_frames(self):
        load_image = lambda dir, state, frame: engine.Image(
            engine.Assets.get("images", f"{dir}_player_{state}{frame}"),
            (
                self.cell.rect.x
                + self.scene.grid_offset[0]
                + (self.cell.rect.width / 2),
                self.cell.rect.y
                + self.scene.grid_offset[1]
                + (self.cell.rect.height / 2),
            ),
            custom_size=(
                self.cell.rect.width * self._scale,
                self.cell.rect.height * self._scale,
            ),
            align="center",
        )
        for dir in {"left", "right"}:
            self._frames[dir] = {
                "idle": {
                    frame: load_image(dir, "idle", frame) for frame in range(1, 9)
                },
                "move": {
                    frame: load_image(dir, "move", frame) for frame in range(1, 9)
                },
                "death": {
                    frame: load_image(dir, "death", frame) for frame in range(1, 13)
                },
            }

    def __update_frames(self):
        cell = self.cell

        rect_pos = (
            cell.rect.x + self.scene.grid_offset[0] + cell.rect.width / 2,
            cell.rect.y + self.scene.grid_offset[1] + cell.rect.height / 2,
        )

        size = (cell.rect.width * self._scale, cell.rect.height * self._scale)
        offset = (
            self.scene.grid_size[0] * self.camera_index[0],
            self.scene.grid_size[1] * self.camera_index[1],
        )

        pos = (
            rect_pos[0] - size[0] / 2 + offset[0],
            rect_pos[1] - size[1] / 2 + offset[1],
        )

        for dir in self._frames.values():
            for state in dir.values():
                for name, image in state.items():
                    image.move_at(pos)

    def __load_sfx(self):
        self._sfx = {
            state: engine.SoundEffect(
                engine.Assets.get("sfx", f"player_{state}"), volume=0.6
            )
            for state in ["move", "death", "skip"]
        }
