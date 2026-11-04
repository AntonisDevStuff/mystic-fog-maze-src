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


class Selection:
    def __init__(self, manager, grid, size, offset):
        self.manager = manager
        self._initialize_runtime(grid, size, offset)

    def __str__(self):
        return self._buttons

    def process_event(self, event):
        if event.type == engine._pygame_gui.UI_BUTTON_PRESSED:
            for name, button in self._buttons.items():
                if not event.ui_element == button:
                    continue
                scene = engine.Scene.manager.scene
                if event.ui_element == self._buttons["Play"]:
                    scene.loader.toggle()
                elif event.ui_element == self._buttons["Options"]:
                    scene.settings.toggle()
                elif event.ui_element == self._buttons["Quit"]:
                    engine.utils.quit()
        elif event.type == engine._pygame_gui.UI_BUTTON_ON_HOVERED:
            for name, button in self._buttons.items():
                if not event.ui_element == button:
                    continue
                self._sfx.play

    def _initialize_runtime(self, grid, size, offset):
        cell_width = size[0] / len(grid[0])
        cell_height = size[1] / len(grid)
        button_width = int(cell_width) * 2
        button_height = int(cell_height)
        column = padding = 1
        text = ("Play", "Options", "Quit")

        self._buttons = {}
        for row in range(3):
            button_x = offset[0] + column * cell_width + padding
            button_y = offset[1] + row * cell_height + padding
            button = engine._pygame_gui.elements.UIButton(
                relative_rect=engine._pygame.Rect(
                    (button_x, button_y), (button_width, button_height)
                ),
                text=text[row],
                manager=self.manager,
                object_id="#big",
            )
            self._buttons[text[row]] = button

        self._sfx = engine.SoundEffect(engine.Assets.get("sfx", "hover"), 0.7)
