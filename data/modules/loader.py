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
import json
import time

celi = lambda x: int(x) + (x % 1 != 0)


class Loader:
    def __init__(self, manager):
        self.manager = manager
        self._initialize_runtime()

    @property
    def visible(self):
        return self._visible

    def __str__(self):
        return self._buttons

    def toggle(self):
        self._visible = not self._visible
        if self._visible:
            self._window.show()
            self._window.enable()
        else:
            self._window.hide()
            self._window.disable()

    def process_event(self, event):
        self._selected.disable()
        if event.type == engine._pygame_gui.UI_BUTTON_PRESSED:
            for name, button in self._major_buttons.items():
                if not event.ui_element == button:
                    continue
                self._selected.enable()
                if event.ui_element == self._major_buttons["LV 1"]:
                    self._selected = button
                    self._major_button_pressed = 1
                    self._right_arrow_button.disable()
                    self._left_arrow_button.disable()
                    self._extra_page = 1
                    button.disable()
                elif event.ui_element == self._major_buttons["LV 2"]:
                    self._selected = button
                    self._major_button_pressed = 2
                    self._right_arrow_button.disable()
                    self._left_arrow_button.disable()
                    self._extra_page = 1
                    button.disable()
                elif event.ui_element == self._major_buttons["LV 3"]:
                    self._selected = button
                    self._major_button_pressed = 3
                    self._right_arrow_button.disable()
                    self._left_arrow_button.disable()
                    self._extra_page = 1
                    button.disable()
                elif event.ui_element == self._major_buttons["LV 4"]:
                    button.disable()
                    self._major_button_pressed = 4
                    self._right_arrow_button.enable()
                    self._left_arrow_button.enable()
                    self._selected = button
                    self._extra_page = (
                        celi(self._unlocked[1] / 10) if self._unlocked[0] == 4 else 1
                    )

            for name, button in self._minor_buttons.items():
                if not event.ui_element == button:
                    continue
                self._selected.enable()
                if event.ui_element == self._minor_buttons[1]:
                    self._minor_button_pressed = 1
                elif event.ui_element == self._minor_buttons[2]:
                    self._minor_button_pressed = 2
                elif event.ui_element == self._minor_buttons[3]:
                    self._minor_button_pressed = 3
                elif event.ui_element == self._minor_buttons[4]:
                    self._minor_button_pressed = 4
                elif event.ui_element == self._minor_buttons[5]:
                    self._minor_button_pressed = 5
                elif event.ui_element == self._minor_buttons[6]:
                    self._minor_button_pressed = 6
                elif event.ui_element == self._minor_buttons[7]:
                    self._minor_button_pressed = 7
                elif event.ui_element == self._minor_buttons[8]:
                    self._minor_button_pressed = 8
                elif event.ui_element == self._minor_buttons[9]:
                    self._minor_button_pressed = 9
                elif event.ui_element == self._minor_buttons[10]:
                    self._minor_button_pressed = 10
                engine.Assets.refresh("levels")
                path = f"{self._major_button_pressed}-{(int(self._minor_button_pressed)) + ((self._extra_page-1) * 10)}"
                level = engine.Assets.get("custom", "levels", path, exit=False)
                if path == "1-1":
                    engine.Scene.manager.change("story", auto=self._auto, _level=level)
                    return
                if not level:
                    engine.Scene.manager.change(
                        "generator", auto=self._auto, target=path
                    )
                    return
                engine.Scene.manager.change("game", auto=self._auto, _level=level)

            if self._major_button_pressed not in {0, 4}:
                self._right_arrow_button.disable()
                self._left_arrow_button.disable()
            else:
                self._right_arrow_button.enable()
                self._left_arrow_button.enable()
                deltas = {self._left_arrow_button: -1, self._right_arrow_button: 1}
                if event.ui_element in deltas and (
                    event.ui_element != self._left_arrow_button or self._extra_page > 1
                ):
                    self._extra_page += deltas[event.ui_element]
                self._extra_page == 1 and self._left_arrow_button.disable()
                self._unlocked[0] != 4 and self._right_arrow_button.disable()
                celi(
                    self._unlocked[1] / 10
                ) < self._extra_page + 1 and self._right_arrow_button.disable()

            for name, button in self._minor_buttons.items():
                index = self._extra_page - 1
                number = (int(name)) + (index * 10)
                button.set_text(str(number))
                button.enable()
                if self._unlocked[0] > self._major_button_pressed:
                    button.enable()
                elif self._unlocked[0] < self._major_button_pressed:
                    button.disable()
                else:
                    number > self._unlocked[1] and button.disable()

        elif event.type == engine._pygame_gui.UI_BUTTON_ON_HOVERED:
            for name, button in self._major_buttons.items():
                if not event.ui_element == button:
                    continue
                self._sfx.play()
            for name, button in self._minor_buttons.items():
                if not event.ui_element == button:
                    continue
                if time.time() - self._last_minor_hover < 0.07:
                    continue
                self._sfx.play()
                self._last_minor_hover = time.time()

            if (
                self._left_arrow_button == event.ui_element
                or self._right_arrow_button == event.ui_element
            ):
                self._sfx_2.play()
                self._last_minor_hover = time.time()

    def _initialize_runtime(self):
        window_size = engine.Display.get_size()
        size = (window_size[0] * 0.5, window_size[1] * 0.5)
        pos = ((window_size[0] - size[0]) / 2, (window_size[1] - size[1]) / 2)

        self._window = engine._pygame_gui.elements.UIWindow(
            rect=engine._pygame.Rect(pos, size),
            manager=self.manager,
            window_display_title="Selection",
            resizable=False,
            draggable=True,
            always_on_top=False,
            visible=False,
        )

        self._visible = False

        with open(
            engine.Assets.get("custom", "levels", "save"), "r", encoding="utf-8"
        ) as f:
            major, minor = f.read().split("\n")[0].split("=")[1].split("-")
            major, minor = int(major), int(minor)
            self._unlocked = major, minor

        with open(
            engine.Assets.get("custom", "settings", "data"), "r", encoding="utf-8"
        ) as f:
            data = json.load(f)

        self._auto = data["auto"]

        if engine.DEV:
            self._unlocked = (4, 1) if self._unlocked[0] < 4 else self._unlocked

        major_button_width = size[0] * 0.3
        major_button_height = size[1] * 1 / 4.2

        self._major_buttons = {}
        for i, text in enumerate(("LV 1", "LV 2", "LV 3", "LV 4")):
            button = engine._pygame_gui.elements.UIButton(
                relative_rect=engine._pygame.Rect(
                    (0, major_button_height * i),
                    (major_button_width, major_button_height),
                ),
                text=text,
                manager=self.manager,
                container=self._window,
            )
            self._major_buttons[text] = button
        self._major_buttons["LV 4"].set_text("EXTRA")

        minor_button_width = size[0] * 0.14
        minor_button_height = size[1] * 1 / 4.2 * 1.5

        self._minor_buttons = {}
        for i in range(10):
            button = engine._pygame_gui.elements.UIButton(
                relative_rect=engine._pygame.Rect(
                    (
                        minor_button_width * (i % 5) + major_button_width,
                        (i // 5) * minor_button_height,
                    ),
                    (minor_button_width, minor_button_height),
                ),
                text=str(i + 1),
                manager=self.manager,
                container=self._window,
            )
            i >= self._unlocked[1] and button.disable()
            self._minor_buttons[i + 1] = button

        self._extra_page = 1
        if self._unlocked[0] == 4:
            self._extra_page = celi(self._unlocked[1] / 10)
        self._major_button_pressed = self._unlocked[0]
        self._minor_button_pressed = self._unlocked[1]

        for name, button in self._minor_buttons.items():
            index = self._extra_page - 1
            number = (int(name)) + (index * 10)
            button.set_text(str(number))
            button.enable()
            if self._unlocked[0] > self._major_button_pressed:
                button.enable()
            elif self._unlocked[0] < self._major_button_pressed:
                button.disable()
            else:
                number > self._unlocked[1] and button.disable()

        self._right_arrow_button = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (
                    minor_button_width * 1.1 + major_button_width,
                    2 * minor_button_height + 17,
                ),
                (46, 46),
            ),
            text="->",
            manager=self.manager,
            container=self._window,
        )

        self._left_arrow_button = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (
                    minor_button_width * 0.2 + major_button_width,
                    2 * minor_button_height + 17,
                ),
                (46, 46),
            ),
            text="<-",
            manager=self.manager,
            container=self._window,
        )

        self._right_arrow_button.disable()
        self._unlocked[1] <= 10 and self._left_arrow_button.disable()

        self._selected = self._major_buttons[f"LV {self._unlocked[0]}"]

        self._window.on_close_window_button_pressed = lambda: (
            self._window.hide()
            or self._window.disable()
            or setattr(self, "_visible", False)
        )

        self._last_minor_hover = 0
        self._sfx = engine.SoundEffect(engine.Assets.get("sfx", "hover"), 0.7)
        self._sfx_2 = engine.SoundEffect(engine.Assets.get("sfx", "slider"), 0.7)
