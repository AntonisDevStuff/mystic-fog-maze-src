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
from pathlib import Path


class Intro(engine.Scene):
    def _on_create(self):
        self.duration = 3
        self.fade_in = 0
        self.fade_out = 1
        self.scale = 0.7
        self.color = (30, 30, 30)
        self.background = self.color

        self.elapsed = 0.0

        sound_path = self.get_sound_path()
        self.music = engine.Music(sound_path, volume=0.65) if sound_path else None

        w, h = self.display.get_resolution()
        self.intro_surface = engine.Surface((w, h), pos=(0, 0))

        image_path = self.get_image_path()
        img = engine._pygame.image.load(image_path).convert_alpha()
        center_pos = (w // 2, h // 2)
        self.logo = engine.Image(
            img,
            center_pos,
            shape_type=0,
            align="center",
            custom_size=(int(w * self.scale), int(h * self.scale)),
        )

        bar_scale = 0.4
        bar_width = int(w * 2 * bar_scale)
        bar_height = int(10 * bar_scale)
        bar_x = (w - bar_width) // 2
        bar_y = h - int(30 * bar_scale)

        self.bar_bg = engine.Rect((bar_x, bar_y), (bar_width, bar_height), (64, 64, 64))
        self.bar_fill = engine.Rect((bar_x, bar_y), (0, bar_height), (0, 200, 0))
        self.bar_max_width = bar_width

        self.current_progress = 0.0
        self.current_alpha = 255

        self.build_intro_surface()

    def _start(self):
        self.max_fps = 60
        self.elapsed = 0.0
        if self.music:
            self.music.play()

    def _update(self):
        self.elapsed += self.dt
        if self.elapsed >= self.duration:
            if self.music:
                self.music.stop()
            self.manager.change("menu")

        progress = min(self.elapsed / self.duration, 1.0)
        alpha = self.fade_alpha(self.elapsed)

        if self.current_progress != progress or self.current_alpha != alpha:
            self.current_progress = progress
            self.current_alpha = alpha
            self.build_intro_surface()

    def _draw(self):
        self.intro_surface.draw(self.display.surface)

    def build_intro_surface(self):
        self.intro_surface.clear((30, 30, 30))

        if self.current_alpha < 255:
            fade_overlay = engine._pygame.Surface(
                self.intro_surface.size, engine._pygame.SRCALPHA
            )
            fade_overlay.fill((0, 0, 0, 255 - self.current_alpha))
            self.intro_surface.blit(fade_overlay, (0, 0))

        logo_surface = self.logo.value.copy()
        logo_surface.set_alpha(self.current_alpha)
        self.intro_surface.blit(logo_surface, self.logo.rect.topleft)

        self.intro_surface.update()

    def fade_alpha(self, elapsed):
        alpha = 255
        if self.fade_in and elapsed < self.fade_in:
            alpha = int(255 * (elapsed / max(self.fade_in, 0.01)))
        elif self.fade_out and elapsed > (self.duration - self.fade_out):
            out_progress = (elapsed - (self.duration - self.fade_out)) / max(
                self.fade_out, 0.01
            )
            alpha = int(255 * (1 - min(1.0, out_progress)))
        return max(0, min(255, alpha))

    def on_error(self, error):
        engine._pygame.mouse.set_visible(True)
        engine._pygame.event.set_grab(False)

    @staticmethod
    def get_image_path():
        return str(
            Path(engine._pygame.__file__).parent
            / "docs"
            / "generated"
            / "_images"
            / "pygame_ce_powered.webp"
        )

    @staticmethod
    def get_sound_path():
        return engine.Assets.data.files["sfx"]["pygame_ce"]
