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


class Data:
    def __init__(self):
        self._file = engine.Assets.get("custom", "settings", "data")
        with open(self._file, "r", encoding="utf-8") as file:
            self._data = json.load(file)

    def save(self):
        with open(self._file, "w", encoding="utf-8") as file:
            json.dump(self._data, file, indent=2)

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        engine.utils.error(AttributeError(f"No such setting: {name}"))
        engine.utils.quit()

    def __setattr__(self, name, value):
        if name in {"_data", "_file"}:
            super().__setattr__(name, value)
        elif "_data" in self.__dict__ and name in self._data:
            self._data[name] = value
        else:
            engine.utils.error(AttributeError(f"No such setting: {name}"))
            engine.utils.quit()


class Settings:
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

    def process_event(self, event):
        if event.type == engine._pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self._btn_save:
                self._data.music_volume = int(self._slider_music.get_current_value())
                self._data.sfx_volume = int(self._slider_sfx.get_current_value())
                self._data.intro = (
                    True if self._menu_intro.selected_option[0] == "Yes" else False
                )
                self._data.auto = (
                    True if self._menu_auto.selected_option[0] == "Yes" else False
                )
                self._data.save()
                self._set_data()
                self.toggle()
            elif event.ui_element == self._btn_cancel:
                self._slider_music.kill()
                self._slider_sfx.kill()
                self._menu_intro.kill()
                self.toggle()
                self._initialize_runtime()
        elif event.type == engine._pygame_gui.UI_BUTTON_ON_HOVERED:
            if (
                event.ui_element == self._btn_save
                or event.ui_element == self._btn_cancel
            ):
                self._play_hover()

        elif event.type == engine._pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if (
                event.ui_element == self._slider_music
                or event.ui_element == self._slider_sfx
            ):
                self._play_slider()

        elif event.type == engine._pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if (
                event.ui_element == self._menu_intro
                or event.ui_element == self._menu_auto
            ):
                self._play_slider()

    def _set_data(self):
        engine.Music.change_volume(self._data.music_volume / 100)
        engine.SoundEffect.change_volume(self._data.sfx_volume / 100)
        engine.Scene.manager.scene.loader._auto = self._data.auto

    def _initialize_runtime(self):
        window_size = engine.Display.get_size()
        size = (window_size[0] * 0.5, window_size[1] * 0.5)
        pos = ((window_size[0] - size[0]) / 2, (window_size[1] - size[1]) / 2)
        self._window = engine._pygame_gui.elements.UIWindow(
            rect=engine._pygame.Rect(pos, size),
            manager=self.manager,
            window_display_title="Settings",
            resizable=False,
            draggable=True,
            always_on_top=False,
            visible=False,
        )
        self._visible = False
        self._data = Data()

        padding = 40
        label_width = 120
        slider_width = size[0] - label_width - 3 * padding

        self._label_music = engine._pygame_gui.elements.UILabel(
            relative_rect=engine._pygame.Rect((padding, padding), (label_width, 30)),
            text="Music Volume",
            manager=self.manager,
            container=self._window,
        )
        self._slider_music = engine._pygame_gui.elements.UIHorizontalSlider(
            relative_rect=engine._pygame.Rect(
                (label_width + 2 * padding, padding), (slider_width, 30)
            ),
            start_value=self._data.music_volume,
            value_range=(0, 100),
            manager=self.manager,
            container=self._window,
        )

        y2 = padding + 50
        self._label_sfx = engine._pygame_gui.elements.UILabel(
            relative_rect=engine._pygame.Rect((padding, y2), (label_width, 30)),
            text="SFX Volume",
            manager=self.manager,
            container=self._window,
        )
        self._slider_sfx = engine._pygame_gui.elements.UIHorizontalSlider(
            relative_rect=engine._pygame.Rect(
                (label_width + 2 * padding, y2), (slider_width, 30)
            ),
            start_value=self._data.sfx_volume,
            value_range=(0, 100),
            manager=self.manager,
            container=self._window,
        )

        y3 = padding + 100
        self._label_intro = engine._pygame_gui.elements.UILabel(
            relative_rect=engine._pygame.Rect((padding, y3), (label_width, 30 + 10)),
            text="Splash Screen",
            manager=self.manager,
            container=self._window,
        )
        self._menu_intro = engine._pygame_gui.elements.UIDropDownMenu(
            options_list=["Yes", "No"],
            starting_option="Yes" if self._data.intro else "No",
            relative_rect=engine._pygame.Rect(
                (label_width + 2 * padding + slider_width / 4, y3),
                (slider_width / 2, 30 + 10),
            ),
            manager=self.manager,
            container=self._window,
        )

        y4 = padding + 150
        self._label_auto = engine._pygame_gui.elements.UILabel(
            relative_rect=engine._pygame.Rect((padding, y4), (label_width, 30 + 10)),
            text="Next Level",
            manager=self.manager,
            container=self._window,
        )
        self._menu_auto = engine._pygame_gui.elements.UIDropDownMenu(
            options_list=["Yes", "No"],
            starting_option="Yes" if self._data.auto else "No",
            relative_rect=engine._pygame.Rect(
                (label_width + 2 * padding + slider_width / 4, y4),
                (slider_width / 2, 30 + 10),
            ),
            manager=self.manager,
            container=self._window,
        )

        y_buttons = size[1] - 60
        btn_w, btn_h = 140, 30
        self._btn_save = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (size[0] - 2 * btn_w - 2 * padding, y_buttons), (btn_w, btn_h)
            ),
            text="Save",
            manager=self.manager,
            container=self._window,
        )
        self._btn_cancel = engine._pygame_gui.elements.UIButton(
            relative_rect=engine._pygame.Rect(
                (size[0] - btn_w - padding, y_buttons), (btn_w, btn_h)
            ),
            text="Cancel",
            manager=self.manager,
            container=self._window,
        )

        self._window.on_close_window_button_pressed = lambda: (
            self._window.hide()
            or self._window.disable()
            or setattr(self, "_visible", False)
        )

    @staticmethod
    def _play_slider():
        now = time.time() * 1000
        last_call = getattr(Settings._play_slider, "_last_slider_call", 0)
        interval = 100

        if now - last_call >= interval:
            Settings._play_slider._last_slider_call = now
            engine.SoundEffect(engine.Assets.get("sfx", "slider"), 0.7).play()

    @staticmethod
    def _play_hover():
        engine.SoundEffect(engine.Assets.get("sfx", "hover"), 0.7).play()
