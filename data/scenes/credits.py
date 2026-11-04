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
import engine.utils


class Credits(engine.Scene):
    typing_speed = 70

    def _start(self):
        self._background_color = (5, 5, 10)

        self.center = engine.Display.get_center()
        self.cx, self.cy = self.center

        self.exit = False
        self.exit_timer = 0

        self.title = "Thanks for playing!"
        self.title_index = 0
        self.title_size = 64
        self.title_color = "white"
        self.cursor_visible = True
        self.typing_finished = False

        self.developer_y = self.cy + 100
        self.prompt_y = self.cy + 320

        self.developer_visible = False
        self.prompt_visible = False

        self.text = engine.Text(
            "_", (self.cx, self.cy - 25), "white", align="center", size=64
        )

        self.text2 = engine.Text(
            "Developed by", (self.cx - 80, self.developer_y), "white", align="center"
        )

        self.username = engine.Text(
            "AntonisDevStuff", (self.cx + 70, self.developer_y), "cyan", align="center"
        )

        self.text3 = engine.Text(
            "Press any key to continue",
            (self.cx, self.prompt_y),
            "gray",
            align="center",
        )

        self.next_scene = "menu"
        self.next_scene_args = {"_loader": True}

        self.event.create("show_developer")
        self.event.create("show_prompt")
        self.event.create("typing")
        self.event.create("blink")

        self.event.schedule("show_developer", 1800, 1)
        self.event.schedule("show_prompt", 2400, 1)
        self.event.schedule("typing", 70)
        self.event.schedule("blink", 450)

    def _update(self):
        if self.exit:
            self.exit_timer += 16
            if self.exit_timer >= 250:
                self.manager.change(self.next_scene, **self.next_scene_args)
            return
        self.type_title()
        self.blink_cursor()
        self.animate()
        self.show_developer()
        self.show_prompt()

    def _on_keydown(self, key):
        if not self.prompt_visible:
            self.title_index = len(self.title)
            self.event.schedule("show_developer", 500, 1)
            self.event.schedule("show_prompt", 1000, 1)
            return
        self.exit = True

    def _on_joydown(self, id, button):
        if not self.prompt_visible:
            self.title_index = len(self.title)
            self.event.schedule("show_developer", 500, 1)
            self.event.schedule("show_prompt", 1000, 1)
            return
        self.exit = True

    def _draw(self):
        engine.Display.draw_text(self.text)
        if self.developer_visible:
            engine.Display.draw_text(self.text2)
            engine.Display.draw_text(self.username)
        if self.prompt_visible:
            engine.Display.draw_text(self.text3)

    @engine.utils.event_listener("typing")
    def type_title(self):
        if self.typing_finished:
            return

        if self.title_index < len(self.title):
            self.title_index += 1
            value = self.title[: self.title_index]
            if self.cursor_visible:
                value += "_"
            self.text = engine.Text(
                value,
                (self.cx, self.cy - 25),
                self.title_color,
                align="center",
                size=self.title_size,
            )
        else:
            self.typing_finished = True
            self.cursor_visible = False
            self.text = engine.Text(
                self.title,
                (self.cx, self.cy - 25),
                self.title_color,
                align="center",
                size=self.title_size,
            )

    @engine.utils.event_listener("blink")
    def blink_cursor(self):
        if self.typing_finished:
            return
        self.cursor_visible = not self.cursor_visible
        value = self.title[: self.title_index]
        if self.cursor_visible:
            value += "_"
        self.text = engine.Text(
            value,
            (self.cx, self.cy - 25),
            self.title_color,
            align="center",
            size=self.title_size,
        )

    @engine.utils.event_listener("show_developer")
    def show_developer(self):
        self.developer_visible = True

    @engine.utils.event_listener("show_prompt")
    def show_prompt(self):
        self.prompt_visible = True

    @engine.utils.run_every(32)
    def animate(self):
        if self.developer_visible and self.developer_y > self.cy + 80:
            self.developer_y -= 3
            self.text2 = engine.Text(
                "Developed by",
                (self.cx - 93, self.developer_y),
                "white",
                align="center",
            )
            self.username = engine.Text(
                "AntonisDevStuff",
                (self.cx + 93, self.developer_y),
                "cyan",
                align="center",
            )

        if self.prompt_visible and self.prompt_y > self.cy + 300:
            self.prompt_y -= 3
            self.text3 = engine.Text(
                "Press any key to continue",
                (self.cx, self.prompt_y),
                "gray",
                align="center",
            )
