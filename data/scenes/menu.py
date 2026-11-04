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

import random


class Menu(engine.Scene):
    def _on_create(self):
        self.background = "white"
        self.grid_data = [
            [2, 0, 0, 2],
            [2, 0, 0, 2],
            [2, 0, 0, 2],
        ]
        self.grid_size = (986, 602)
        self.grid_offset = (140, 100)
        self.grass_offset = (-140, -120)
        self.grass_amount = 600
        self.grass_settings = {
            "stiffness": 600,
            "max_unique": 8,
            "place_range": [0, 1, 2, 3, 4, 5, 6, 7],
        }
        self.grass_shadows = {
            "shadow_radius": 4,
            "shadow_color": (30, 30, 30),
            "shadow_shift": (1, 2, 3),
        }

        self.music_volue = 0.5
        self.mouse_speed = 0.6
        self.is_mousedown = False

        # 10% for secret
        self.secret = int(random.random() + 10 / 100)

    def _start(self):
        self.create_cursor()
        self.create_grid()
        self.create_grass()
        self.create_secret()
        self.create_frame()
        self.create_gui()
        self.create_buttons()
        self.create_console()
        self.create_settings()
        self.create_loader()
        self.create_tutorial()
        self.create_milestone()
        self.set_shader()
        self.play_music()

    def _update(self):
        self.update_grass()
        self.update_gui()
        self.update_cursor()

    def _draw(self):
        self.draw_grid()
        self.draw_alien()
        self.draw_grass()
        self.draw_custom_lines()
        self.draw_frame()
        self.draw_gui()
        self.draw_cursor()

    def _on_event(self, event):
        self.cursor.process_event(event)
        self.tutorial.process_event(event)
        self.gui.process_events(event)
        self.console.process_event(event)
        self.milestone.process_event(event)
        self.settings.process_event(event)
        self.selection.process_event(event)
        self.loader.process_event(event)

    def _on_mousemove(self, position, movement):
        hover_cell = self.grid.cell(self.cursor.position)
        if (
            hover_cell
            and hover_cell.state == 2
            and not self.settings._visible
            and self.is_mousedown
            and not self.loader._visible
        ):
            self.apply_grass_presure(self.cursor.position)
            self.play_grass()

    def _on_mousedown(self, button):
        self.is_mousedown = True
        self.secret and self.alien.rect.colliderect(
            self.cursor.rect
        ) and not self.settings.visible and not self.loader.visible and self.manager.change(
            "secret"
        )

    def _on_mouseup(self, button):
        self.is_mousedown = False

    def _on_joydown(self, joy, button):
        button == 4 and self.console.toggle()

    def _on_change(self):
        self.music.stop()

    def _on_error(self, error):
        engine._pygame.mouse.set_visible(True)
        engine._pygame.event.set_grab(False)

    def create_cursor(self):
        Cursor = engine.Assets.get("modules", "cursor")
        self.cursor = Cursor(self.mouse_speed, visible=True)

    def create_grid(self):
        Grid = engine.Assets.get("modules", "grid")
        self.grid = Grid(self.grid_data, self.grid_size, lines=0)
        self.grid.offset = self.grid_offset
        self.grid.create()  # pre-update

    def create_grass(self):
        Grass = engine.Assets.get("modules", "grass")
        self.grass = Grass(tile_size=int(self.grid.cell_size[0]), **self.grass_settings)
        self.grass.enable_ground_shadows(**self.grass_shadows)
        self.grass.offset = self.grid_offset
        for col, row in self.grid.cells:
            cell = self.grid.get(col, row)
            if cell.state == 2:
                self.grass.place_tile((col, row), self.grass_amount)

    def create_secret(self):
        cell = self.grid.get(
            *random.choice(((0, 0), (0, 1), (0, 2), (3, 0), (3, 1), (3, 2)))
        )
        pos = (
            lambda c: (
                c.rect.x + self.grid_offset[0] + self.grid.cell_size[0] / 2,
                c.rect.y + self.grid_offset[1] + self.grid.cell_size[1] / 2,
            )
        )(cell)
        self.alien = engine.Image(
            engine._pygame.image.load(self.get_alien_path()),
            pos,
            align="center",
        )

    def create_frame(self):
        frame_path = engine.Assets.get("images", "overlay")
        self.frame = engine.Image(
            engine.Assets.get("images", "overlay"),
            (0, 0),
            custom_size=engine.Display.get_resolution(),
        )

    def create_gui(self):
        self.gui = engine._pygame_gui.UIManager(
            engine.Display.get_resolution(),
            theme_path=engine.Assets.get("custom", "json", "gui"),
        )

    def create_buttons(self):
        Selection = engine.Assets.get("modules", "selection")
        self.selection = Selection(
            self.gui, self.grid_data, self.grid_size, self.grid_offset
        )

    def create_console(self):
        Console = engine.Assets.get("modules", "console")
        self.console = Console(self.gui)

    def create_settings(self):
        Settings = engine.Assets.get("modules", "settings")
        self.settings = Settings(self.gui)
        pre_laod = getattr(self, "_settings", False)
        pre_laod and self.settings.toggle()

    def create_loader(self):
        Loader = engine.Assets.get("modules", "loader")
        self.loader = Loader(self.gui)
        pre_laod = getattr(self, "_loader", False)
        pre_laod and self.loader.toggle()

    def create_tutorial(self):
        Tutorial = engine.Assets.get("modules", "tutorial")
        self.tutorial = Tutorial(self.gui)

        if engine.COUNTER == 1:
            engine.COUNTER = -1
            self.tutorial.toggle()

    def create_milestone(self):
        Milestone = engine.Assets.get("modules", "milestone")
        milestones = {
            3: (
                "You've reached 3 sessions: ",
                "That's a good time to write a review :)",
            ),
            10: ("You've reached 10 sessions: ", "Welcome Back!"),
            25: ("You've reached 25 sessions: ", "You clearly enjoy solving mazes"),
            50: ("You've reached 50 sessions: ", "That's impressive dedication"),
            100: ("You've reached 100 sessions: ", "Unstoppable!!!"),
        }
        self.milestone = Milestone(self.gui, milestones.get(engine.COUNTER, None))
        if engine.COUNTER in milestones:
            engine.COUNTER = -1
            self.milestone.toggle()

    def play_music(self):
        self.music = engine.Music(
            engine.Assets.get("music", "menu"), volume=self.music_volue
        )
        self.music.play(loops=-1)

    @engine.utils.run_every(800)
    def play_grass(self):
        self.grass_hover = engine.SoundEffect(
            engine.Assets.get("sfx", "grass"), volume=0.6
        )
        self.grass_hover.play()

    def set_shader(self):
        shader_path = engine.Assets.get("custom", "shaders", "crt")
        engine.Display.set_shader(shader_path)

    # 75 ms for better performance
    @engine.utils.run_every(120)
    def apply_grass_presure(self, position):
        self.grass.apply_force(
            (position[0] + self.grass_offset[0], position[1] + self.grass_offset[1]),
            80,
            7,
        )

    # 10 ms for better performance
    @engine.utils.run_every(40)
    def update_grass(self):
        self.grass.update()

    def update_gui(self):
        self.gui.update(self.dt)

    def update_cursor(self):
        self.cursor.update()

    def draw_grass(self):
        self.grass.draw(engine.Display.surface, offset=self.grass_offset)

    def draw_grid(self):
        self.grid.draw()

    def draw_frame(self):
        engine.Display.draw_image(self.frame)

    def draw_alien(self):
        if not self.secret:
            return
        engine.Display.draw_image(self.alien)

    def draw_custom_lines(self):
        cell_w = int(self.grid.cell_size[0])
        cell_h = int(self.grid.cell_size[1])
        ox, oy = self.grid_offset
        width = self.grid_size[0]
        height = self.grid_size[1]

        for col in range(self.grid._cols + 1):
            if col == 2:
                continue
            x = ox + col * cell_w
            engine._pygame.draw.line(
                engine.Display.surface, "black", (x, oy), (x, oy + height), 5
            )

        for row in range(self.grid._rows + 1):
            y = oy + row * cell_h
            engine._pygame.draw.line(
                engine.Display.surface,
                "black",
                (ox + cell_w, y),
                (ox + width - cell_w, y),
                5,
            )

    def draw_gui(self):
        self.gui.draw_ui(engine.Display.surface)

    def draw_cursor(self):
        self.cursor.draw()

    @staticmethod
    def get_alien_path():
        from pathlib import Path

        return str(
            Path(engine._pygame.__file__).parent / "examples" / "data" / "alien1.png"
        )
