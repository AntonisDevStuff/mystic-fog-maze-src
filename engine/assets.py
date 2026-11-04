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

from .utils import get_filename, load_class, error, quit

from dataclasses import dataclass, field
from pathlib import Path
import sys, os

import pygame

loaders = {
    "images": lambda path: pygame.image.load(path).convert_alpha(),
    "music": lambda path: path,
    "sfx": lambda path: pygame.mixer.Sound(path),
    "fonts": lambda path: {
        size: pygame.font.Font(path, size)
        for size in {
            1,
            2,
            4,
            8,
            10,
            12,
            14,
            16,
            18,
            24,
            32,
            48,
            64,
            72,
            96,
            128,
            144,
            192,
            256,
        }
    },
    "scenes": lambda path: load_class(
        path, get_filename(path).title().replace(" ", "_")
    ),
    "modules": lambda path: load_class(
        path, get_filename(path).title().replace(" ", "_")
    ),
}


@dataclass
class Data:
    files: dict = field(default_factory=dict)
    path: dict = field(default_factory=dict)
    images: dict = field(default_factory=dict)
    fonts: dict = field(default_factory=dict)
    scenes: dict = field(default_factory=dict)
    music: dict = field(default_factory=dict)
    sfx: dict = field(default_factory=dict)
    modules: dict = field(default_factory=dict)
    custom: dict = field(default_factory=dict)

    def __repr__(self):
        return (
            f"<Loaded Data | "
            f"images: {len(self.images)}, "
            f"fonts: {len(self.fonts)}, "
            f"scenes: {len(self.scenes)}, "
            f"music: {len(self.music)}, "
            f"sfx: {len(self.sfx)}, "
            f"modules: {len(self.modules)}, "
            f"custom: {sum(len(v) for v in self.custom.values())}>"
        )


class Assets:
    data = Data()

    @classmethod
    def init(
        cls,
        pre_load=True,
        images=None,
        fonts=None,
        scenes=None,
        music=None,
        sfx=None,
        modules=None,
        **custom_types,
    ):
        caller = cls.__get_caller_path()
        cls._load_data_files(
            caller, images, fonts, scenes, music, sfx, modules, **custom_types
        )
        cls._load_default_font()
        pre_load and cls.load("data")

    @classmethod
    def get(cls, *loc, exit=True):
        if not loc:
            error(KeyError("Asset lookup failed, no asset path provided"))
            quit()

        source = "data"
        keys = loc

        if loc[0].lower() == "data":
            source = loc[0].lower()
            keys = loc[1:]

        data = getattr(cls, source)
        for key in keys:
            key = key.lower()
            if isinstance(data, dict):
                data = data.get(key)
            else:
                data = getattr(data, key, None)
            if data is None:
                exit and error(
                    KeyError(f"Could not find asset at path: {'->'.join(loc)}")
                )
                exit and quit()
                return None
        return data

    @classmethod
    def load(cls, source):
        data = getattr(cls, source)
        for category, loader in loaders.items():
            file_dict = data.files.get(category)
            if not file_dict:
                continue

            if hasattr(data, category):
                asset_store = getattr(data, category)
            else:
                if category not in data.custom:
                    data.custom[category] = {}
                asset_store = data.custom[category]

            for name, path in file_dict.items():
                asset_store[name] = loader(path)

    @classmethod
    def refresh(cls, *names):
        files = dict()
        for name in names:
            files[name] = Assets.data.path[name]
        cls.data.files.update(cls.__get_all_files(files))
        cls.load("data")  # load all (need update)

    @staticmethod
    def register(name, loader):
        builtin_types = {"images", "fonts", "scenes", "music", "sfx"}
        if name in builtin_types:
            error(ValueError(f"Cannot override built-in asset type: {name}"))
            quit()
        loaders[name] = loader

    @classmethod
    def _load_data_files(
        cls,
        caller,
        path_images=None,
        path_fonts=None,
        path_scenes=None,
        path_music=None,
        path_sfx=None,
        path_modules=None,
        **path_custom,
    ):
        full_paths = {
            name: cls.__get_full_path(caller, path)
            for name, path in {
                "images": path_images,
                "fonts": path_fonts,
                "scenes": path_scenes,
                "music": path_music,
                "sfx": path_sfx,
                "modules": path_modules,
                **path_custom,
            }.items()
            if path
        }
        cls.data.path = full_paths
        cls.data.files = cls.__get_all_files(full_paths)

    @classmethod
    def _load_default_font(cls):
        name = pygame.font.get_default_font().split(".")[0]
        sizes = {
            size: pygame.font.SysFont(name, size)
            for size in {
                1,
                2,
                4,
                8,
                10,
                12,
                14,
                16,
                18,
                24,
                32,
                48,
                64,
                72,
                96,
                128,
                144,
                192,
                256,
            }
        }
        cls.data.fonts[name] = sizes

    @staticmethod
    def __get_all_files(paths, ignore=None):
        if not ignore:
            ignore = set()

        ignore.add("__pycache__")
        data = {}
        for key, value in paths.items():
            root_path = Path(value)
            for file in sorted(root_path.rglob("*")):
                if any(part in ignore for part in file.parts):
                    continue
                if not file.is_file():
                    continue
                data.setdefault(key, {})
                data[key][file.stem] = str(file)
        return data

    @staticmethod
    def __get_full_path(caller, path):
        full = Path(caller, path).resolve()
        if not full.exists():
            error(OSError(f"The path doesn't exist: {full}"))
            quit()
        return full

    @staticmethod
    def __get_caller_path():
        return os.getcwd()
