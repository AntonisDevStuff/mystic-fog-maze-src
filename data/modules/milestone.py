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


class Milestone:
    def __init__(self, manager, text):
        self.manager = manager
        self.text = text
        self._initialize_runtime()

    @property
    def visible(self):
        return self._visible

    def toggle(self):
        self._visible = not self._visible
        if self._visible:
            self._window.show()
            self._window.enable()
        else:
            self._window.hide()
            self._window.disable()

    def process_event(self, event):
        if event.type == engine._pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._btn_ok:
                self.toggle()
        elif event.type == engine._pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element == self._btn_ok:
                self._play_hover()

    def _initialize_runtime(self):
        self._visible = False

        if not self.text:
            self.text = (None, None)

        self.text = tuple(str(text) for text in self.text)

        display_w, display_h = engine.Display.get_size()

        window_w = 280
        window_h = 140
        window_x = (display_w - window_w) / 2
        window_y = (display_h - window_h) / 2

        self._window = engine._pygame_gui.elements.UIWindow(
            rect=engine._pygame.Rect((window_x, window_y), (window_w, window_h)),
            manager=self.manager,
            window_display_title="Session",
            resizable=False,
            draggable=True,
            always_on_top=False,
            visible=self._visible,
        )

        padding = 5
        label_width = window_w - padding * 2
        label_height = 20
        y_pos = padding

        for i in range(2):
            label = engine._pygame_gui.elements.UILabel(
                relative_rect=engine._pygame.Rect(
                    (padding, y_pos), (label_width, label_height)
                ),
                text=self.text[i],
                manager=self.manager,
                container=self._window,
            )
            y_pos += label_height + 5

        button_width = 80
        button_height = 40
        button_x = (window_w - button_width) / 2
        button_y = window_h - button_height - padding - 36

        self._btn_ok = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (button_x, button_y), (button_width, button_height)
            ),
            text="OK",
            manager=self.manager,
            container=self._window,
        )

        self._window.on_close_window_button_pressed = lambda: self.toggle()

    @staticmethod
    def _play_hover():
        engine.SoundEffect(engine.Assets.get("sfx", "hover"), 0.7).play()
