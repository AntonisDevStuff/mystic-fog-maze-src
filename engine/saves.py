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

import shutil
import os
import json
from pathlib import Path
from .assets import Assets
from .wrapper import Music, SoundEffect
from .utils import error, quit


class Saves:
    location = None
    new = False

    @classmethod
    def init(cls, name, saves, location):
        location = Path(location)
        name = cls._sanitize_name(name)
        cls.location = location
        cls.new = cls._check_new(location)
        cls.new and cls._create_defaults(name, saves, location)

    @classmethod
    def update(cls):
        if cls.location is None:
            error(RuntimeError("Saves not initialized. Call Saves.init() first."))
            quit()

        cls.new and cls._set_defaults(cls.location)

        Assets.refresh("settings", "levels")
        cls._set_data()

    @staticmethod
    def _sanitize_name(name):
        return name.strip().lower().replace(" ", "-")

    @staticmethod
    def _create_defaults(name, files, location):
        for item in files:
            target = location / item
            target.mkdir(parents=True, exist_ok=False)

    @staticmethod
    def _check_new(location):
        counter_file = location / ".counter"
        try:
            with open(counter_file, "r+", encoding="utf-8") as f:
                counter = int(f.read().strip())
                f.seek(0)
                f.write(str(counter + 1))
                f.truncate()
                return False
        except FileNotFoundError:
            with open(counter_file, "w", encoding="utf-8") as f:
                f.write("1")
            return True
        except Exception as e:
            error(Exception(f"An error occurred: {e}"))
            quit()

    @staticmethod
    def _set_defaults(location):
        try:
            defaults = Assets.get("custom", "defaults")
            default_file = Path(next(iter(defaults.values())))

            base = next(
                (
                    parent
                    for parent in default_file.parents
                    if parent.name.lower() == "saves"
                ),
                None,
            )

            if base is None or not base.exists():
                error(FileNotFoundError(f"Default saves directory not found: {base}"))
                quit()

            for item in base.iterdir():
                if item.is_dir():
                    dest = location / item.name
                    shutil.copytree(item, dest, dirs_exist_ok=True)

        except StopIteration as e:
            error(RuntimeError("No default saves available"))
            quit()

    @staticmethod
    def _set_data():
        file_path = Assets.get("custom", "settings", "data")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        music_vol = max(0, min(100, data.get("music_volume", 100))) / 100
        sfx_vol = max(0, min(100, data.get("sfx_volume", 100))) / 100

        Music.change_volume(music_vol)
        SoundEffect.change_volume(sfx_vol)

        if os.environ["INTRO"] == "1":
            os.environ["INTRO"] = "1" if data.get("intro", True) else "0"
