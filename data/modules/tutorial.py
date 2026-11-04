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


class Tutorial:
    def __init__(self, manager):
        self.manager = manager
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

    def option(self, status):
        scene = engine.Scene.manager.scene
        if not status:
            self.toggle()
            return
        level = engine.Assets.get("custom", "levels", "tutorial")
        engine.Scene.manager.change("tutorial", _level=level)

    def process_event(self, event):
        if event.type == engine._pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._btn_yes:
                self.option(True)
            elif event.ui_element == self._btn_no:
                self.option(False)
        elif event.type == engine._pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element == self._btn_yes or event.ui_element == self._btn_no:
                self._play_hover()

    def _initialize_runtime(self):
        window_size = engine.Display.get_size()
        size = (330, 200)
        pos = ((window_size[0] - size[0]) / 2, (window_size[1] - size[1]) / 2)
        self._window = engine._pygame_gui.elements.UIWindow(
            rect=engine._pygame.Rect(pos, size),
            manager=self.manager,
            window_display_title="Tutorial",
            resizable=False,
            draggable=True,
            always_on_top=False,
            visible=False,
        )
        self._visible = False

        padding = 15
        text_size = (size[0] - 2 * padding - 20, 60)
        self._label_text_1 = engine._pygame_gui.elements.UILabel(
            relative_rect=engine._pygame.Rect((padding, padding), text_size),
            text="Welcome! This is your first time playing.",
            manager=self.manager,
            container=self._window,
        )

        self._label_text_2 = engine._pygame_gui.elements.UILabel(
            relative_rect=engine._pygame.Rect((padding, padding * 3), text_size),
            text="Should we start with a tutorial?",
            manager=self.manager,
            container=self._window,
        )

        btn_w, btn_h = 80, 40
        btn_spacing = 20
        buttons_width = 2 * btn_w + btn_spacing
        buttons_x = (size[0] - buttons_width) / 2
        y_buttons = size[1] - btn_h - padding - 15

        self._btn_yes = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (buttons_x, y_buttons - 18), (btn_w, btn_h)
            ),
            text="Yes",
            manager=self.manager,
            container=self._window,
        )
        self._btn_no = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (buttons_x + btn_w + btn_spacing, y_buttons - 18), (btn_w, btn_h)
            ),
            text="No",
            manager=self.manager,
            container=self._window,
        )

        self._window.on_close_window_button_pressed = lambda: (self.option(False))

    @staticmethod
    def _play_hover():
        engine.SoundEffect(engine.Assets.get("sfx", "hover"), 0.7).play()
