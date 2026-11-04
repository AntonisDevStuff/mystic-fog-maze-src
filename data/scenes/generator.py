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
from threading import Thread
from pathlib import Path
from random import randint as random, seed


class Generator(engine.Scene):
    def _on_create(self):
        self.total = 10
        self.index = 1
        self.counter = 0
        self.finished = False

    def _start(self):
        self.create_gui()
        self.create_bar()
        self.start_thread()

    def _update(self):
        self.update_gui()
        self.update_bar()
        self.update_finished()

    def _draw(self):
        self.draw_gui()
        self.draw_text()

    def _on_event(self, event):
        self.gui.process_events(event)

    def create_gui(self):
        self.gui = engine._pygame_gui.UIManager(
            engine.Display.get_resolution(),
            theme_path=engine.Assets.get("custom", "json", "gui"),
        )

    def create_bar(self):
        size = (
            engine.Display.get_resolution()[0] / 1.35,
            engine.Display.get_resolution()[1] / 6,
        )
        pos = (
            engine.Display.get_center()[0] - size[0] / 2,
            engine.Display.get_center()[1] - size[1] / 2,
        )
        self.bar = engine._pygame_gui.elements.UIStatusBar(
            engine._pygame.Rect(pos, size),
            self.gui,
        )

        text_pos = (pos[0] - 400, pos[1] - 70)
        self.text = engine.Text(
            "Generating...", text_pos, "white", align="right", size=64
        )

    def create_levels(self):
        Module = engine.Assets.get("modules", "generator")
        info = engine.Assets.get("custom", "levels", ".index")
        with open(info, "r", encoding="utf-8") as f:
            data = f.read()
            self.index = int(data)

        levels = range(self.index * 10 - 10, self.index * 10)
        var = 1 * (self.index + 10)
        for level in levels:
            seed(var + level)
            config = {
                "level": f"4-{level+1}",
                "difficulty": "hard",
                "grid_size": random(20, 25),
                "fog": random(3, 5),
                "music": "rain",
                "camera": True,
                "output": Path(info).parent,
                "seed": var + level,
            }
            Module(**config).create()
            self.counter += 1
        with open(info, "w", encoding="utf-8") as f:
            f.write(str(self.index + 1))
        self.finished = True

    def start_thread(self):
        thread = Thread(target=self.create_levels)
        thread.setDaemon(True)
        thread.start()

    def update_gui(self):
        self.gui.update(self.dt)

    def update_bar(self):
        progress = self.counter / self.total
        self.bar.percent_full = progress

    def update_finished(self):
        if not self.finished:
            return
        engine.Assets.refresh("levels")
        level = engine.Assets.get("custom", "levels", self.target, exit=False)
        if level:
            engine.Scene.manager.change("game", auto=self.auto, _level=level)
        else:
            engine.Scene.manager.change("menu", _loader=True)

    def draw_gui(self):
        self.gui.draw_ui(engine.Display.surface)

    def draw_text(self):
        engine.Display.draw_text(self.text)
