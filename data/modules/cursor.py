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
import time
import math


class Cursor:
    def __init__(self, speed, visible):
        self._speed = speed
        self._visible = visible
        self._initialize_runtime()

    @property
    def position(self):
        return self._image.position

    @property
    def rect(self):
        return self._image.rect

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    @property
    def speed(self):
        return self._current_speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    def _update_acceleration(self, is_moving, dt):
        target_speed = self._speed if is_moving else 0

        if is_moving:
            blend_factor = 0.15
        else:
            blend_factor = 0.05

        self._current_speed += (target_speed - self._current_speed) * blend_factor

        self._current_speed = max(0, min(self._current_speed, self._max_speed))

    def update(self):
        scene = engine.Scene.manager.scene

        x, y = self._controller_motion
        if math.hypot(x, y) < 0.10:
            x, y = 0.0, 0.0

        self._controller_motion[0] = x
        self._controller_motion[1] = y

        controller_moving = bool(x or y)
        mouse_moving = engine._pygame.mouse.get_rel() != (0, 0)

        if not hasattr(scene, "dt"):
            return

        if controller_moving:
            self._update_acceleration(is_moving=controller_moving, dt=scene.dt)

        if mouse_moving:
            self._update_acceleration(is_moving=mouse_moving, dt=scene.dt)

        if controller_moving:
            mouse_pos = engine._pygame.mouse.get_pos()
            window_size = engine._pygame.display.get_window_size()
            display_size = engine.Display.get_resolution()
            pos = (
                mouse_pos[0] * display_size[0] / window_size[0],
                mouse_pos[1] * display_size[1] / window_size[1],
            )
            move_amount = (
                x * self._current_speed * scene.dt * 1000,
                y * self._current_speed * scene.dt * 1000,
            )
            self._image.move(move_amount)

            self._moving_time = scene.dt

            new_x = max(0, min(self._image.position[0], display_size[0]))
            new_y = max(0, min(self._image.position[1], display_size[1]))
            self._image.move_at((new_x, new_y))

            scene._on_mousemove((new_x, new_y), (x, y))

            engine._pygame.mouse.set_pos((int(new_x), int(new_y)))

    def draw(self):
        self._visible and engine.Display.draw_image(self._image)

    def process_event(self, event):
        if event.type == engine._pygame.MOUSEMOTION:
            mouse_pos = engine._pygame.mouse.get_pos()
            window_size = engine._pygame.display.get_window_size()
            display_size = engine.Display.get_resolution()

            pos = (
                mouse_pos[0] * display_size[0] / window_size[0],
                mouse_pos[1] * display_size[1] / window_size[1],
            )

            x, y = event.rel
            move_amount = (x * self._current_speed, y * self._current_speed)
            self._image.move(move_amount)

            new_x = max(0, min(self._image.position[0], display_size[0]))
            new_y = max(0, min(self._image.position[1], display_size[1]))
            self._image.move_at((new_x, new_y))

            engine._pygame.mouse.set_pos((int(new_x), int(new_y)))

        elif event.type == engine._pygame.JOYAXISMOTION:
            if event.axis >= 2:
                return
            self._controller_motion[event.axis] = event.value

        elif event.type == engine._pygame.JOYBUTTONDOWN:
            scene = engine.Scene.manager.scene
            button = scene._controler_map.get(0)
            for joy in scene.joysticks.values():
                if joy.get_button(button):
                    scene._on_event(
                        engine._pygame.event.Event(
                            engine._pygame.MOUSEBUTTONDOWN,
                            {
                                "pos": (
                                    int(self._image.position[0]),
                                    int(self._image.position[1]),
                                ),
                                "button": 1,
                            },
                        )
                    )
                    scene._on_mousedown("left")

        elif event.type == engine._pygame.JOYBUTTONUP:
            scene = engine.Scene.manager.scene
            button = scene._controler_map.get(0)
            for joy in scene.joysticks.values():
                if not joy.get_button(button):
                    scene._on_event(
                        engine._pygame.event.Event(
                            engine._pygame.MOUSEBUTTONUP,
                            {
                                "pos": (
                                    int(self._image.position[0]),
                                    int(self._image.position[1]),
                                ),
                                "button": 1,
                            },
                        )
                    )
                    scene._on_mouseup("left")

    def _initialize_runtime(self):
        self._image = engine.Image(
            engine.Assets.get("images", "cursor"),
            engine.Display.get_center(),
            align="center",
            custom_size=(48, 48),
        )

        self._current_speed = 0
        self._acceleration = 6.0
        self._deceleration = 3.0
        self._max_speed = 400

        self._controller_motion = [0, 0]

        engine._pygame.mouse.set_pos(engine.Display.get_center())
