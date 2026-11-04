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


class Pause:
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
            self._scene.manager.pause()
            self._scene.music.pause()
        else:
            self._window.hide()
            self._window.disable()
            self._scene.manager.resume()
            self._scene.music.resume()

    def process_event(self, event):
        if event.type == engine._pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._btn_resume:
                self.toggle()
            elif event.ui_element == self._btn_restart:
                self.toggle()
                self._scene.player.steps = 0
            elif event.ui_element == self._btn_exit:
                self._scene.manager.change("menu")

    def _initialize_runtime(self):
        self._scene = engine.Scene.manager.scene

        window_size = engine.Display.get_size()
        size = (window_size[0] * 0.15, window_size[1] * 0.3)
        pos = ((window_size[0] - size[0]) / 2, (window_size[1] - size[1]) / 2)
        self._window = engine._pygame_gui.elements.UIWindow(
            rect=engine._pygame.Rect(pos, size),
            manager=self.manager,
            window_display_title="Pause",
            resizable=False,
            draggable=False,
            always_on_top=True,
            visible=False,
        )
        self._visible = False

        padding = 20
        btn_w = size[0] - 2 * padding
        btn_h = 40

        y_pos = padding

        self._btn_resume = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect((padding, y_pos), (btn_w, btn_h)),
            text="Resume",
            manager=self.manager,
            container=self._window,
        )

        y_pos += btn_h + padding

        self._btn_restart = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect((padding, y_pos), (btn_w, btn_h)),
            text="Restart",
            manager=self.manager,
            container=self._window,
        )

        y_pos += btn_h + padding

        self._btn_exit = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect((padding, y_pos), (btn_w, btn_h)),
            text="Exit",
            manager=self.manager,
            container=self._window,
        )

        self._window.on_close_window_button_pressed = self.toggle
