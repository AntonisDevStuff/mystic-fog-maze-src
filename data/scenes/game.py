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
import time
import math
import collections


class Game(engine.Scene):
    def _on_create(self):
        self.background = "black"
        self.mouse_speed = 0.6
        self.music_volue = 0.7
        self.double_click_threshold = 1 / 5
        self.grid_offset = (140, 111)
        self.grid_size = (986, 602)
        self.grid_map = {
            "center": (0, 0),
            "right": (self.grid_size[0], 0),
            "left": (-self.grid_size[0], 0),
            "up": (0, -self.grid_size[1]),
            "down": (0, self.grid_size[1]),
            "up-left": (-self.grid_size[0], -self.grid_size[1]),
            "up-right": (self.grid_size[0], -self.grid_size[1]),
            "down-left": (-self.grid_size[0], self.grid_size[1]),
            "down-right": (self.grid_size[0], self.grid_size[1]),
        }
        self.grid_connections = {
            "center": {
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right",
                "up-left": "up-left",
                "up-right": "up-right",
                "down-left": "down-left",
                "down-right": "down-right",
            },
            "up": {
                "down": "center",
                "down-left": "left",
                "down-right": "right",
                "left": "up-left",
                "right": "up-right",
            },
            "down": {
                "up": "center",
                "up-left": "left",
                "up-right": "right",
                "left": "down-left",
                "right": "down-right",
            },
            "left": {
                "right": "center",
                "up-right": "up",
                "down-right": "down",
                "up": "up-left",
                "down": "down-left",
            },
            "right": {
                "left": "center",
                "up-left": "up",
                "down-left": "down",
                "up": "up-right",
                "down": "down-right",
            },
            "up-left": {
                "down-right": "center",
                "right": "up",
                "down": "left",
                "down-left": "left",
                "up-right": "up",
            },
            "up-right": {
                "down-left": "center",
                "left": "up",
                "down": "right",
                "down-right": "right",
                "up-left": "up",
            },
            "down-left": {
                "up-right": "center",
                "right": "down",
                "up": "left",
                "up-left": "left",
                "down-right": "down",
            },
            "down-right": {
                "up-left": "center",
                "left": "down",
                "up": "right",
                "up-right": "right",
                "down-left": "down",
            },
        }
        self.camera_moves = {
            "center": (0, 0),
            "right": (1, 0),
            "left": (-1, 0),
            "down": (0, 1),
            "up": (0, -1),
            "up-left": (-1, -1),
            "up-right": (1, -1),
            "down-left": (-1, 1),
            "down-right": (1, 1),
        }
        self.reverse_camera_moves = {v: k for k, v in self.camera_moves.items()}
        self.invalid = engine.SoundEffect(
            engine.Assets.get("sfx", "incorrect"), volume=0.5
        )

    def _initialize_runtime(self):
        self.camera_index = [0, 0]
        self.selection_index = [0, 0]
        self.selection_speed = 0.07
        self.selection_away = 0
        self.selection_auto = 0
        self.selection_timer = 0
        self.end_index = [0, 0]
        self.skip = False
        self.end_loc = "center"
        self.camera_loc = "center"

        self.time_keypressed = {}
        self.hold_keydown = {}
        self.last_keydown = ()
        self.last_joydown = ()

        self.event.create("selection_updated")
        self.event.create("draw_fog")
        self.event.schedule("selection_updated", 350)
        self.event.post("draw_fog")

    def _start(self):
        self._initialize_runtime()
        self.create_gui()
        self.create_frame()
        self.create_console()
        self.create_pause()
        self.create_level()
        self.create_camera()
        self.create_cursor()
        self.create_grid()
        self.create_player()
        self.create_rain()
        self.set_shader()
        self.play_music()

    def _update(self):
        if self.skip:
            return
        self.update_rain()
        self.update_gui()
        self.update_cursor()
        self.update_selection()
        self.update_joystick()
        self.update_player()

    def _draw(self):
        self.draw_fog()
        self.draw_grid()
        self.draw_selection()
        self.draw_path()
        self.draw_player()
        self.draw_rain()
        self.draw_gui()
        self.draw_frame()
        self.draw_level()
        self.draw_cursor()

    def _on_event(self, event):
        self.cursor.process_event(event)
        self.gui.process_events(event)
        self.console.process_event(event)
        self.pause.process_event(event)

    def _on_keydown(self, key):
        self.hold_keydown[key] = 0.0
        if self.console.visible:
            return
        (
            self.move_index(key)
            if not self.selection_auto or self.selection_auto == key
            else None
        )
        self.handle_input(key)

    def _on_keyup(self, key):
        self.selection_auto = None
        self.hold_keydown.pop(key, None)

    def _on_keypressed(self, keys):
        self.time_keypressed.update(
            (key, self.time_keypressed.get(key, 0) + self.dt) for key in keys
        )
        self.handle_selection()

    def _on_joydown(self, joy, button):
        button == 4 and self.console.toggle()
        if self.console.visible:
            return

        self.move_index(button)
        self.handle_input(button)

    def _paused_update(self):
        self.update_gui()
        self.update_cursor()

    def _paused_draw(self):
        self.draw_gui()
        self.draw_cursor()

    def _on_paused_event(self, event):
        self.cursor.process_event(event)
        self.gui.process_events(event)
        self.pause.process_event(event)

    def _on_paused_keydown(self, key):
        key == "escape" and self.pause.toggle()

    def _on_change(self):
        self.music.stop()

    def _on_error(self, error):
        engine._pygame.mouse.set_visible(True)
        engine._pygame.event.set_grab(False)

    @property
    def selection(self):
        return self.grid.get(*self.selection_index)

    @property
    def grid(self):
        return self.grids.get(self.camera_loc)

    @property
    def renderer(self):
        return self.camera if self.camera else engine.Display

    def create_level(self):
        Level = engine.Assets.get("modules", "level")
        self.level = Level(self._level, self.console)

    def create_gui(self):
        self.gui = engine._pygame_gui.UIManager(
            engine.Display.get_resolution(),
            theme_path=engine.Assets.get("custom", "json", "gui"),
        )

    def create_camera(self):
        has_camera = self.level.data["Settings"]["camera"]
        self.camera = engine.Camera() if has_camera else None
        self.camera and self.camera.set_max_zoom(2)

    def create_cursor(self):
        Cursor = engine.Assets.get("modules", "cursor")
        self.cursor = Cursor(self.mouse_speed, visible=False)

    def create_console(self):
        Console = engine.Assets.get("modules", "console")
        self.console = Console(self.gui)

    def create_pause(self):
        Pause = engine.Assets.get("modules", "pause")
        self.pause = Pause(self.gui)

    def create_rain(self):
        has_rain = self.level.data["Settings"]["music"] == "rain"
        Rain = engine.Assets.get("modules", "rain")
        self.rain = Rain(300, 15) if has_rain else None

    def create_player(self):
        Player = engine.Assets.get("modules", "player")
        start = next(
            (
                (direction, pos)
                for direction, grid in self.grids.items()
                for pos, cell in grid.cells.items()
                if cell.state == 3
            ),
            ("center", [1, 1]),
        )
        direction, index = start
        index = list(index)
        steps = self.level.data["Settings"].get("steps")
        explosives = self.level.data["Settings"].get("explosives", int(steps * 2))
        fog = self.level.data["Settings"].get("fog", 0)

        self.player = Player(
            index=index,
            direction=direction,
            explosives=explosives,
            steps=steps,
            fog=fog,
            scene=self,
        )

        self.camera_loc = direction
        self.player.move(
            (self.player.direction, self.player.index[0], self.player.index[1])
        )
        self.move_camera(direction)
        self.player.steps += 1
        self.selection_index = index.copy()

    def create_frame(self):
        frame_path = engine.Assets.get("images", "overlay")
        self.frame = engine.Image(
            engine.Assets.get("images", "overlay"),
            (0, 0),
            custom_size=engine.Display.get_resolution(),
        )

    def create_grid(self):
        Grid = engine.Assets.get("modules", "grid")
        self.grids = {}

        directions = [
            "center",
            "up",
            "down",
            "left",
            "right",
            "up-left",
            "up-right",
            "down-left",
            "down-right",
        ]

        padded = lambda d: (
            [[0] * (len(d[0]) + 2)]
            + [[0] + r + [0] for r in d]
            + [[0] * (len(d[0]) + 2)]
        )

        state = 5
        directions_map = self.grid_connections
        available = {
            direction: bool(self.level.data["Map"].get(direction))
            for direction in directions
        }
        for direction in directions:
            data = self.level.data["Map"].get(direction)
            if not data:
                continue

            connections = {}
            for exit_direction, target in directions_map.get(direction).items():
                if available.get(target, False):
                    connections[exit_direction] = state

            final_data = padded(data)
            rows = len(final_data)
            cols = len(final_data[0])

            if "up" in connections:
                for x in range(1, cols - 1):
                    final_data[0][x] = state
            if "down" in connections:
                for x in range(1, cols - 1):
                    final_data[rows - 1][x] = state
            if "left" in connections:
                for y in range(1, rows - 1):
                    final_data[y][0] = state
            if "right" in connections:
                for y in range(1, rows - 1):
                    final_data[y][cols - 1] = state

            if direction == "center":
                if available["up"] and available["left"]:
                    final_data[0][0] = state
                if available["up"] and available["right"]:
                    final_data[0][cols - 1] = state
                if available["down"] and available["left"]:
                    final_data[rows - 1][0] = state
                if available["down"] and available["right"]:
                    final_data[rows - 1][cols - 1] = state
            elif direction == "up":
                if available["left"]:
                    final_data[rows - 1][0] = state
                if available["right"]:
                    final_data[rows - 1][cols - 1] = state
            elif direction == "down":
                if available["left"]:
                    final_data[0][0] = state
                if available["right"]:
                    final_data[0][cols - 1] = state
            elif direction == "left":
                if available["up"]:
                    final_data[0][cols - 1] = state
                if available["down"]:
                    final_data[rows - 1][cols - 1] = state
            elif direction == "right":
                if available["up"]:
                    final_data[0][0] = state
                if available["down"]:
                    final_data[rows - 1][0] = state
            elif direction == "up-left":
                if available["up"] and available["left"]:
                    final_data[rows - 1][cols - 1] = state
            elif direction == "up-right":
                if available["up"] and available["right"]:
                    final_data[rows - 1][0] = state
            elif direction == "down-left":
                if available["down"] and available["left"]:
                    final_data[0][cols - 1] = state
            elif direction == "down-right":
                if available["down"] and available["right"]:
                    final_data[0][0] = state

            grid = Grid(
                final_data,
                self.grid_size,
                pos=self.grid_map[direction],
                lines=5,
                renderer=self.renderer,
            )
            grid.offset = self.grid_offset
            grid.create()

            self.grids[direction] = grid

        self.end_loc, self.end_index = next(
            (
                (direction, pos)
                for direction, grid in self.grids.items()
                for pos, cell in grid.cells.items()
                if cell.state == -1
            ),
            ("center", (1, 1)),
        )

    def move_camera(self, direction):
        camera_moves = self.camera_moves
        if direction not in camera_moves:
            return

        if not self.camera:
            return

        dx, dy = camera_moves[direction]

        new_x = self.camera_index[0] + dx
        new_y = self.camera_index[1] + dy

        if not (-1 <= new_x <= 1 and -1 <= new_y <= 1):
            return

        self.camera_index[0] = new_x
        self.camera_index[1] = new_y

        self.camera.move((dx * self.grid_size[0], dy * self.grid_size[1]))

        if dx > 0:
            self.selection_index[0] = 1
        elif dx < 0:
            self.selection_index[0] = self.grid.columns - 2

        if dy > 0:
            self.selection_index[1] = 1
        elif dy < 0:
            self.selection_index[1] = self.grid.rows - 2

        location_map = self.reverse_camera_moves

        self.camera_loc = location_map.get(tuple(self.camera_index))
        self.event.post("draw_fog")

    def move_index(self, input):
        if not self.selection:
            return
        if self.selection.color == "black":
            return
        if self.player.moving:
            return
        old_index = self.selection_index.copy()
        moves = self.camera_moves
        if isinstance(input, int):
            input = {
                11: "up",
                12: "down",
                13: "left",
                14: "right",
            }.get(input)

        if input in moves:
            dx, dy = moves[input]
            self.selection_index[0] += dx
            self.selection_index[1] += dy
            if not self.selection:
                self.selection_index = old_index
            if self.selection.color == "black" or (
                self.selection.color == "yellow" and self.player.moving
            ):
                self.selection_index = old_index
            if self.selection.color == "yellow" and not self.player.moving:
                self.move_camera(input)

        self.event.post("selection_updated")

    def move_to_player(self, recursion=0):
        if recursion > 20:
            return

        self.selection_index = self.player.index.copy()

        if self.player.camera == self.camera_loc:
            return

        locations = self.camera_moves

        target_x, target_y = locations[self.player.camera]
        current_x, current_y = locations[self.camera_loc]

        dx = target_x - current_x
        dy = target_y - current_y

        if dx != 0:
            self.move_camera("right" if dx > 0 else "left")

        elif dy != 0:
            self.move_camera("down" if dy > 0 else "up")

        self.move_to_player(recursion + 1)

    def move_to_end(self, recursion=0):
        if recursion > 20:
            return

        self.selection_index = list(self.end_index)

        if self.end_loc == self.camera_loc:
            return

        locations = self.camera_moves

        target_x, target_y = locations[self.end_loc]
        current_x, current_y = locations[self.camera_loc]

        dx = target_x - current_x
        dy = target_y - current_y

        if dx != 0:
            self.move_camera("right" if dx > 0 else "left")

        elif dy != 0:
            self.move_camera("down" if dy > 0 else "up")

        self.move_to_end(recursion + 1)

    def handle_input(self, input):
        (input == "escape" or input == 6) and self.pause.toggle()
        if self.pause.visible:
            return
        (input == "r" or input == 1) and setattr(self.player, "steps", 0)
        (input == "x" or input == 3) and self.player.moving and self.handle_target(None)
        (input == "space" or input == 0) and self.player.moving and self.player.skip()
        (
            input == "space" or input == 0
        ) and not self.player.moving and self.handle_target(self.selection_index.copy())

        # double-click
        if (input == "a" or input == 2) and not self.player.moving:
            keyboard_double = (
                self.last_keydown
                and input == self.last_keydown[0]
                and time.time() - self.last_keydown[1] < self.double_click_threshold
            )
            joystick_double = (
                self.last_joydown
                and input == self.last_joydown[0]
                and time.time() - self.last_joydown[1] < self.double_click_threshold
            )
            (
                self.move_to_end()
                if (keyboard_double or joystick_double)
                else self.move_to_player()
            )
        self.last_keydown = (input, time.time())
        self.last_joydown = (input, time.time())

    def handle_target(self, target):
        if not target:
            self.player.stop()
            return

        if self.player.skipping:
            return

        cell = self.grid.get(*target)

        if (
            cell.state == 2
            and self.player.explosives > 0
            and self.player.is_visible(target, self.camera_loc)
        ):
            self.player.explosive(target)
            return

        if cell.state not in (4, -1, 3):
            self.invalid.play()
            return

        path = self.find_path(
            self.player.camera,
            self.player.index.copy(),
            self.camera_loc,
            target,
            self.grids,
            self.grid_connections,
        )
        if not path or self.player.moving:
            self.invalid.play()
            return

        self.player.move(*path)

        return 1

    def handle_selection(self):
        for key in self.keys_pressed:
            if self.selection_auto:
                break
            self.hold_keydown[key] += self.dt
            if self.hold_keydown[key] < self.double_click_threshold * 2:
                continue
            self.selection_auto = key

        if not self.selection_auto:
            return
        key = self.selection_auto
        if self.time_keypressed[key] >= self.selection_speed:
            self.selection_auto = key
            self.move_index(key)
            self.handle_input(key)
            self.time_keypressed[key] = 0

    def set_shader(self):
        shader_path = engine.Assets.get("custom", "shaders", "crt")
        engine.Display.set_shader(shader_path)

    def play_music(self):
        self.music = engine.Music(
            engine.Assets.get("music", self.level.data["Settings"]["music"]),
            volume=self.music_volue,
        )
        self.music.play(loops=-1)

    def update_gui(self):
        self.gui.update(self.dt)

    def update_player(self):
        self.player.update(self.dt)
        if self.player.cell.state == -1 and self.player.steps > 0:
            next = self.level.end()
            if next == "4-1":
                self.manager.change("credits")
                return
            if not self.auto:
                self.manager.change("menu", _loader=True)
                return
            level = engine.Assets.get("custom", "levels", next, exit=False)
            if not level:
                self.manager.change("generator", auto=self.auto, target=next)
                return
            self.manager.change("game", auto=self.auto, _level=level)
            self.skip = True

    def update_cursor(self):
        self.cursor.visible = any((self.console.visible, self.pause.visible))
        self.cursor.update()

    def update_joystick(self):
        pos = (
            self.joystick_motion.get(0, 0),
            self.joystick_motion.get(1, 0),
        )
        x, y = (0, 0) if math.hypot(pos[0], pos[1]) < 0.1 else pos
        if not x and not y:
            self.selection_timer = 0
            return
        self.selection_timer -= self.dt
        if self.selection_timer <= 0:
            x_direction = (x > 0) - (x < 0)
            y_direction = (y > 0) - (y < 0)
            key = (x_direction, y_direction)
            if min(abs(x), abs(y)) / max(abs(x), abs(y), 1) < 0.5:
                key = (x_direction, 0) if abs(x) > abs(y) else (0, y_direction)
            direction = self.reverse_camera_moves.get(key)
            direction and self.move_index(direction)
            self.selection_timer = self.selection_speed

    def update_rain(self):
        self.rain and self.rain.update(self.dt)

    @engine.utils.event_listener("selection_updated")
    def update_selection(self):
        self.selection_away = len(
            self.find_path(
                self.player.camera,
                self.player.index.copy(),
                self.camera_loc,
                self.selection_index.copy(),
                self.grids,
                self.grid_connections,
            )
        )

    def draw_gui(self):
        self.gui.draw_ui(engine.Display.surface)

    def draw_frame(self):
        engine.Display.draw_image(self.frame)

    def draw_cursor(self):
        self.cursor.draw()

    def draw_player(self):
        self.player.draw()

    def draw_rain(self):
        self.rain and self.rain.draw()

    def draw_grid(self):
        for grid in self.grids:
            self.grids[grid].draw()

    def draw_path(self):
        for step in self.player.path:
            grid = self.grids.get(step[0])
            x, y = grid.get(step[1], step[2]).position
            offset = (
                self.grid_map.get(step[0])[0] + grid.offset[0],
                self.grid_map.get(step[0])[1] + grid.offset[1],
            )

            pos = (
                x * grid.cell_size[0] + offset[0],
                y * grid.cell_size[1] + offset[1],
            )

            size = (grid.cell_size[0], grid.cell_size[1])

            explosives = (
                self.player.explosives if self.player.explosives < float("inf") else 0
            )

            overlay = engine.Rect(pos, size, "greenyellow")
            self.renderer.draw_shape(overlay, 3)

    def draw_selection(self):
        if self.player.moving:
            if self.camera:
                return
            for i, step in enumerate(self.player.path):
                rect = self.grids.get(step[0]).get(step[1], step[2]).rect
                size = rect.size
                offset = (
                    self.grid_offset[0] + self.grid_size[0] * self.camera_index[0],
                    self.grid_offset[1] + self.grid_size[1] * self.camera_index[1],
                )
                pos = (rect.x + offset[0], rect.y + offset[1])
                text_size = max(size[0] / 2 * 0.8, size[1] / 2 * 0.8)
                text_pos = (
                    pos[0] + size[0] // 2,
                    pos[1] + size[1] // 2 - text_size / 2,
                )
                steps = self.player.steps - i - 1
                value = f"{int(steps / 1000)}k" if steps >= 1000 else steps
                moving_text = engine.Text(
                    f"{value}", text_pos, "aquamarine2", size=text_size, align="center"
                )
                self.renderer.draw_text(moving_text)
            return
        rect = self.selection.rect
        cell = self.grids.get(self.camera_loc).get(*self.selection_index)
        offset = (
            self.grid_offset[0] + self.grid_size[0] * self.camera_index[0],
            self.grid_offset[1] + self.grid_size[1] * self.camera_index[1],
        )
        pos = (rect.x + offset[0], rect.y + offset[1])
        size = rect.size
        data = engine.Rect(pos, size, "orange")
        self.renderer.draw_shape(data, 4)

        if not self.player.is_visible(
            self.selection_index.copy(), self.camera_loc
        ) and (cell.state == 1 or cell.state == 2):
            return

        if (self.selection_index[0] == self.player.index[0]) and (
            self.selection_index[1] == self.player.index[1]
        ):
            return

        text_size = max(size[0] / 2, size[1] / 2)
        text_pos = (
            pos[0] + size[0] // 2,
            pos[1] + size[1] // 2 - text_size / 2,
        )

        if self.player.steps < float("inf") and not self.selection.state in {2, 1}:
            if self.selection_away:
                steps = self.player.steps - self.selection_away
                value = (
                    "Fail"
                    if steps <= 0
                    else (
                        "Last"
                        if steps == 1
                        else f"{int(steps / 1000)}k" if steps >= 1000 else steps
                    )
                )
            else:
                value = "X"
            step_text = engine.Text(
                f"{value}", text_pos, "aquamarine2", size=text_size, align="center"
            )
            self.renderer.draw_text(step_text)
            return

        has_explosive = False
        for explosive in self.player.Explosive.explosives:
            if (
                explosive.index[0] == self.selection_index[0]
                and explosive.index[1] == self.selection_index[1]
            ):
                has_explosive = True
                break
        if self.selection.state == 2 and not has_explosive:
            explosives = (
                self.player.explosives
                if self.player.explosives < 1000
                else f"{int(self.player.explosives / 1000)}k"
            )
            value = explosives if self.player.explosives < float("inf") else "∞"
            explosive_text = engine.Text(
                f"{value}", text_pos, "darkred", size=text_size, align="center"
            )
            self.renderer.draw_text(explosive_text)

    @engine.utils.event_listener("draw_fog")
    def draw_fog(self):
        if not self.player.fog:
            return
        for dir, grid in self.grids.items():
            grid = self.grids[dir]
            surface = grid.surface
            grid.reset()
            for pos, cell in grid.cells.items():
                if cell.state not in (1, 2):
                    continue
                if self.player.is_visible(pos, dir):
                    continue
                x, y = pos

                pos = (
                    x * grid.cell_size[0],
                    y * grid.cell_size[1],
                )

                size = (grid.cell_size[0], grid.cell_size[1])

                engine._pygame.draw.rect(
                    surface.value, "gray", engine._pygame.Rect(pos, size), 0
                )
                engine._pygame.draw.rect(
                    surface.value, "black", engine._pygame.Rect(pos, size), 3
                )
            grid.update()

    def draw_level(self):
        text = engine.Text(
            f"Level: {self.level.data['Info']['level']} | {self.level.data['Info']['name']}",
            (engine.Display.get_center()[0], 40),
            "white",
            align="center",
            size=48,
        )
        engine.Display.draw_text(text)

    @staticmethod
    def find_path(start_camera, start, target_camera, target, grids, connections):
        start = (start_camera, *start)
        target = (target_camera, *target)
        queue = collections.deque([(start, [])])
        visited = {start}
        while queue:
            (camera, x, y), path = queue.popleft()
            if (camera, x, y) == target:
                return path

            grid = grids[camera]
            for nx, ny in (
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
            ):
                node = (camera, nx, ny)
                if node in visited:
                    continue

                cell = grid.cells.get((nx, ny))
                if cell is None or cell.state not in (4, -1, 3):
                    continue

                visited.add(node)
                queue.append((node, path + [node]))
            for direction, next_camera in connections.get(camera, {}).items():
                if direction in ("up-left", "up-right", "down-left", "down-right"):
                    continue
                if next_camera not in grids:
                    continue
                if direction == "right" and x != grid.columns - 2:
                    continue
                if direction == "left" and x != 1:
                    continue
                if direction == "down" and y != grid.rows - 2:
                    continue
                if direction == "up" and y != 1:
                    continue

                next_grid = grids[next_camera]
                if direction == "right":
                    nx, ny = 1, y
                elif direction == "left":
                    nx, ny = next_grid.columns - 2, y
                elif direction == "down":
                    nx, ny = x, 1
                else:
                    nx, ny = x, next_grid.rows - 2
                cell = next_grid.cells.get((nx, ny))
                if cell is None or cell.state not in (4, -1, 3):
                    continue

                node = (next_camera, nx, ny)
                if node in visited:
                    continue

                visited.add(node)
                queue.append((node, path + [node]))
        return []
