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

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import pygame
import pygame_shaders
import os


class Display:
    window = None
    surface = None
    clock = None

    _title = ""
    _icon = None
    _res = None
    _index = 0
    _vsync = -1
    _fullscreen = False
    _shaders = True

    _screen_shader = None

    @classmethod
    def init(cls, title, resolution, monitor=0, fullscreen=False):
        cls._title = title
        cls._res = tuple(resolution)
        cls._fullscreen = fullscreen
        cls._index = monitor

        cls._shaders = True if os.environ["SHADERS"] == "1" else False

        cls.clock = pygame.time.Clock()
        cls.surface = pygame.Surface(resolution)
        cls.set_title(title)
        cls._set_mode()

    @classmethod
    def set_shader(cls, path):
        if cls._shaders:
            cls._screen_shader = pygame_shaders.Shader(
                pygame_shaders.DEFAULT_VERTEX_SHADER,
                path,
                cls.surface,
            )

    @classmethod
    def render_screen(cls):
        if cls._shaders:
            rect = pygame.Rect(0, 0, cls._res[0], cls._res[1])
            if isinstance(cls._screen_shader, pygame_shaders.Shader):
                cls._screen_shader.render_direct(rect)
            else:
                cls._screen_shader.render()
        else:
            cls.window.blit(cls.surface)

    @classmethod
    def get_title(cls):
        return cls._title

    @classmethod
    def set_title(cls, value):
        pygame.display.set_caption(value)
        cls._title = value

    @classmethod
    def get_icon(cls):
        return cls._icon

    @classmethod
    def set_icon(cls, surf):
        pygame.display.set_icon(surf)
        cls._icon = surf

    @classmethod
    def get_resolution(cls):
        return cls._res

    @classmethod
    def get_center(cls):
        w, h = cls._res
        return (w / 2, h / 2)

    @classmethod
    def get_size(cls):
        return cls._res

    @classmethod
    def draw_shape(cls, shape, fill=0, scale=1):
        shape.draw(cls.surface, fill=fill, scale=scale)

    @classmethod
    def draw_text(cls, txt, scale=1):
        txt.draw(cls.surface, scale=scale)

    @classmethod
    def draw_image(cls, image, scale=1):
        image.draw(cls.surface, scale=scale)

    @classmethod
    def draw_surface(cls, surface, scale=1):
        surface.draw(cls.surface, scale=scale)

    @classmethod
    def _set_mode(cls):
        vsync = cls._vsync
        display = cls._index

        flags = 0
        if cls._shaders:
            flags = pygame.OPENGL | pygame.DOUBLEBUF
        if cls._fullscreen:
            flags |= pygame.FULLSCREEN | pygame.SCALED | pygame.HWSURFACE

        try:
            if cls._shaders:
                cls.window = pygame.display.set_mode(
                    cls._res, flags=flags, vsync=-1, display=display
                )
            else:
                cls.window = pygame.display.set_mode(
                    cls._res, flags=flags, vsync=1, display=display
                )
        except pygame.error:
            cls.window = pygame.display.set_mode(cls._res, flags=flags, display=display)

        if cls._shaders:
            cls._screen_shader = pygame_shaders.DefaultScreenShader(cls.surface)
