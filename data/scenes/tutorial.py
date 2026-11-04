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

Game = engine.Assets.get("scenes", "game")


class Tutorial(Game):
    def _on_create(self):
        super()._on_create()
        self.text = {
            1: "Move the cell selector",
            2: "Center the selector on the player",
            3: "Restart the level",
            4: "Move player to dark green cell",
            5: "Cancel moving path",
            6: "Place explosive at green cell",
            7: "Center the selector on the red cell",
            8: "Make super step (x2 cost)",
            9: "Reach the red cell to win",
            10: "Good Job!",
        }
        self.input = {
            1: "Press 'Arrow Keys'",
            2: "Press 'A'",
            3: "Press 'R'",
            4: "Press 'Space'",
            5: "Press 'X' (while moving)",
            6: "Press 'Space'",
            7: "Press '2xA'",
            8: "Press 'Space' (while moving)",
        }
        self.input2 = {
            1: "Press 'D-Pad'",
            2: "Press 'X'",
            3: "Press 'B'",
            4: "Press 'A'",
            5: "Press 'Y' (while moving)",
            6: "Press 'A'",
            7: "Press '2xA'",
            8: "Press 'A' (while moving)",
        }
        self.button_states = {
            0: "space",
            1: "r",
            2: "a",
            3: "x",
            11: "up",
            12: "down",
            13: "left",
            14: "right",
        }
        self.text_pos = (engine.Display.get_center()[0], 40)
        self.text_size = 42
        self.text_color = "purple"

        self.input_pos = (self.text_pos[0], self.text_pos[1] + 80)
        self.input_size = 32
        self.input_color = "yellow"

        self.next = engine.SoundEffect(engine.Assets.get("sfx", "start"))

    def _start(self):
        super()._start()
        self.index = getattr(self, "_index", 1)
        self.controller = len(self.joysticks) > 0
        self.text_data = self.create_text()
        self.input_data = self.create_input()

    def _draw(self):
        super()._draw()
        self.renderer.draw_text(self.text_data[self.index])
        self.index <= 8 and self.renderer.draw_text(self.input_data[self.index])

    def _update(self):
        super()._update()

        if self.index == 9 and self.player.path:
            cell = self.grid.get(self.player.path[-1][1], self.player.path[-1][2])
            if cell.state == -1:
                self.index += 1
                self.next.play()

    def _on_joydeviceadded(self, id):
        super()._on_joydeviceadded(id)
        self.controller = True
        self.input_data = self.create_input()

    def _on_joydeviceremoved(self, id):
        super()._on_joydeviceremoved(id)
        self.controller = False
        self.input_data = self.create_input()

    def _on_keydown(self, key):
        self.handle_state(key)
        self.handle_double_input(key)
        super()._on_keydown(key)

    def _on_joydown(self, joy, button):
        state = self.button_states.get(button, None)
        state and self.handle_state(state)
        self.handle_double_input(button)
        super()._on_joydown(joy, button)

    def handle_state(self, key):
        if self.index == 1 and key in {"left", "right", "up", "down"}:
            self.index += 1
            self.next.play()
        elif self.index == 2 and key == "a":
            self.index += 1
            self.next.play()
        elif self.index == 3 and key == "r":
            self.index += 1
            self.restart()
        elif self.index == 4 and key == "space":
            cell = self.grid.get(*self.selection_index)
            if cell.state == 4:
                self.index += 1
                self.next.play()
        elif self.index == 5 and key == "x":
            if self.player.moving:
                self.index += 1
                self.next.play()
        elif self.index == 6 and key == "space":
            cell = self.grid.get(*self.selection_index)
            if cell.state == 2:
                self.index += 1
                self.next.play()
            self.end_index = (10, 6)
            self.grid.get(10, 6).state = -1
            self.grid.create(need_offset=False)
        elif self.index == 8 and key == "space":
            if self.player.moving:
                self.index += 1
                self.next.play()

    def handle_double_input(self, input):
        if self.index == 7 and (input == "a" or input == 2) and not self.player.moving:
            keyboard_double = (
                self.last_keydown is not None
                and input == self.last_keydown[0]
                and time.time() - self.last_keydown[1] < self.double_click_threshold
            )

            joystick_double = (
                self.last_joydown is not None
                and input == self.last_joydown[1]
                and time.time() - self.last_joydown[2] < self.double_click_threshold
            )

            if keyboard_double or joystick_double:
                self.index += 1
                self.next.play()

    def create_text(self):
        text = {}
        for key, value in self.text.items():
            text[key] = engine.Text(
                f"{value}",
                self.text_pos,
                self.text_color,
                size=self.text_size,
                align="center",
            )
        return text

    def create_input(self):
        input = {}
        data = self.input2 if self.controller else self.input
        for key, value in data.items():
            input[key] = engine.Text(
                f"{value}",
                self.input_pos,
                self.input_color,
                size=self.input_size,
                align="center",
            )
        return input

    # overwites
    def restart(self):
        level = engine.Assets.get("custom", "levels", "tutorial")
        self.manager.change("tutorial", _level=level, _index=self.index)

    def update_player(self):
        self.player.update(self.dt)
        if self.player.cell.state == -1 and self.player.steps > 0:
            self.manager.change("menu")

    def draw_level(self):
        return
