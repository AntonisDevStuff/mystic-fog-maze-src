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

import os
import sys
from pathlib import Path

TITLE = "Mystic Fog Maze"
VERSION = 1.0
RESOLUTION = (1280, 800)

# Flags
os.environ["SHADERS"] = "0" if "-noshaders" in sys.argv else "1"
os.environ["INTRO"] = "0" if "-novid" in sys.argv else "1"
os.environ["SOUND"] = "0" if "-nosound" in sys.argv else "1"
os.environ["DEV"] = "1" if "-dev" in sys.argv else "0"
os.environ["WINDOW"] = "1" if "-window" in sys.argv else "0"

# Help flag
if "help" in sys.argv:
    print(
        """Custom Flags:
      -dev                    Enable developer/debug mode
      -window                 Run in windowed mode
      -noshaders              Disable shader rendering
      -novid                  Disable intro video
      -nosound                Disable sound"""
    )
    engine.utils.quit()

is_dev = lambda: os.environ["DEV"] == "1"
need_fullscreen = lambda: os.environ["WINDOW"] == "0"
need_intro = lambda: os.environ["INTRO"] == "1"
need_audio = lambda: os.environ["SOUND"] == "1"


def set_caller_path():
    os.chdir(Path(sys.argv[0]).resolve().parent)


def load_counter():
    path = engine.Assets.get("custom", "saves", ".counter")
    with open(path, "r", encoding="utf-8") as f:
        counter = int(f.read())
    return counter


def close_audio():
    engine.Music.change_volume(0)
    engine.SoundEffect.change_volume(0)


def load_grass(path):
    image = engine._pygame.image.load(path).convert()
    image.set_colorkey((0, 0, 0))
    return image


def load_empty(path):
    return path


def load_icon(path):
    surface = engine._pygame.image.load(path)
    return surface


def main():
    # Set debug mode based on runtime environment
    DEV = is_dev()
    AUDIO = need_audio()
    FULLSCREEN = need_fullscreen()

    # Set engine metadata
    engine.VERSION = VERSION
    engine.DEV = DEV

    # Initialize the display (window size, title, etc.)
    engine.Display.init(
        title=TITLE,
        resolution=RESOLUTION,
        fullscreen=FULLSCREEN,
    )

    # Move to the game folder path
    set_caller_path()

    # Initialize the game saves
    engine.Saves.init(TITLE, ("settings", "levels"), "data/saves")

    # Register custom assets types
    engine.Assets.register("grass", load_grass)
    engine.Assets.register("shaders", load_empty)
    engine.Assets.register("json", load_empty)
    engine.Assets.register("scripts", load_empty)
    engine.Assets.register("levels", load_empty)
    engine.Assets.register("settings", load_empty)
    engine.Assets.register("saves", load_empty)
    engine.Assets.register("defaults", load_empty)

    # Load game assets (e.g., images, sounds, etc.)
    engine.Assets.init(
        pre_load=True,
        scenes="data/scenes",
        shaders="data/shaders",
        modules="data/modules",
        json="data/json",
        scripts="data/scripts",
        defaults="data/defaults",
        levels="data/saves/levels",
        settings="data/saves/settings",
        saves="data/saves",
        sfx="assets/sfx",
        grass="assets/grass",
        images="assets/images",
        music="assets/music",
    )

    # Update the game saves
    engine.Saves.update()
    engine.COUNTER = load_counter()

    # Create and configure the initial scene (scene name,**kwargs)
    scene, kwargs = "menu", {}
    scene = "intro" if need_intro() else scene

    # Hide and grab mouse
    engine._pygame.mouse.set_visible(False)
    engine._pygame.event.set_grab(True)

    # Set icon
    engine.Display.set_icon(load_icon("assets/icon.png"))

    # Special cases
    not AUDIO and close_audio()

    # Create scene
    engine.Scene.manager.create(scene, **kwargs)

    # Start the scene
    engine.Scene.manager.start()


if __name__ == "__main__":
    main()
