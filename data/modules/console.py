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
import random
import sys
import io
import threading
from datetime import datetime
from sys import version_info as _python_version

START = time.time()


class Console:
    def __init__(self, manager):
        self.manager = manager
        self._initialize_runtime()

    @property
    def visible(self):
        return self._visible

    def log(self, text, *args, **kwargs):
        if kwargs.get("flush", False):
            self._window.clear_log()
        self._window.add_output_line_to_log(text)

    def toggle(self):
        self._visible = not self._visible
        self._window.show() if self._visible else self._window.hide()

    def process_event(self, event):
        if event.type == engine._pygame.KEYDOWN and event.key == engine._pygame.K_F1:
            self.toggle()

        elif (
            event.type == engine._pygame_gui.UI_CONSOLE_COMMAND_ENTERED
            and event.ui_element == self._window
        ):
            raw = event.command.strip()

            if not raw:
                return

            parts = raw.split(" ")
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else ()
            self._handle_command(command, args)

        elif (
            event.type == engine._pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED
            and event.ui_element == self._warning
        ):
            engine.DEV = True

    def _initialize_runtime(self):
        window = engine.Display.get_size()
        size = (window[0] * 0.5, window[1] * 0.5)
        pos = ((window[0] - window[0] * 0.7) / 2, (window[1] - window[1] * 0.7) / 2)
        python_version: str = (
            f"{_python_version[0]}.{_python_version[1]}.{_python_version[2]}"
        )
        pygame_version: str = engine._pygame.version.ver
        sdl_version: str = (
            f"{engine._pygame.version.SDL[0]}.{engine._pygame.version.SDL[1]}.{engine._pygame.version.SDL[2]}"
        )
        self._window = engine._pygame_gui.windows.UIConsoleWindow(
            rect=engine._pygame.Rect(pos, size),
            manager=self.manager,
            visible=False,
            always_on_top=True,
        )
        self._window.on_close_window_button_pressed = lambda: self.toggle()

        self._visible = False
        self.log(
            f"Python {python_version} | Pygame {pygame_version} | SDL {sdl_version}"
        )
        self.log("Type 'help' for a list of commands")

        self._warning = None

    def _handle_command(self, command, args):
        global START
        match command:
            case "clear":
                self._window.clear_log()

            case "help":
                commands = {
                    "help": "Show commands",
                    "time": "Show current time",
                    "uptime": "Show game uptime",
                    "echo": "Print text",
                    "random": "Get random number",
                    "load": "Load a level",
                    "benchmark": "Run generator benchmark",
                    "tutorial": "Play tutorial",
                    "credits": "Show credits",
                    "clear": "Clear the console",
                    "dev": "Enable dev mode",
                    "kit": "Show dev kit",
                }
                for cmd, desc in commands.items():
                    self.log(f"{cmd:<12} - {desc}")

            case "echo":
                self.log(" ".join(args))

            case "time":
                self.log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            case "uptime":
                self.log(f"{int(time.time() - START)}s")

            case "tutorial":
                engine.Scene.manager.change(
                    "tutorial", _level=engine.Assets.get("custom", "levels", "tutorial")
                )

            case "random":
                self.log(f"{random.random()}")

            case "pygame" | "pygame-ce":
                self.log("Best snake <3")

            case "load":
                name = "".join(args)
                level = engine.Assets.get("custom", "levels", name, exit=False)
                if not level:
                    self.log(f"Level {name} not found")
                    return
                if not engine.DEV:
                    save = engine.Assets.get("custom", "levels", "save")
                    with open(
                        engine.Assets.get("custom", "levels", "save"),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        major, minor = f.read().split("\n")[0].split("=")[1].split("-")
                        unlocked = (int(major), int(minor))

                    requested = tuple(map(int, name.split("-")))
                    if requested > unlocked:
                        self.log(f"Level {name} is locked")
                        return
                engine.Scene.manager.change("game", _level=level)

            case "credits":
                engine.Scene.manager.change("credits")

            case "benchmark":
                try:
                    amount = int(args[0])
                except ValueError:
                    self.log("Amount must be an integer")
                    return
                except IndexError:
                    self.log("Amount must be provided")
                    return
                if amount <= 0:
                    self.log("Amount must be greater than 0")
                    return
                if threading.active_count() > 1:
                    self.log("Anothing Thread is running")
                    return
                Generator = engine.Assets.get("modules", "generator")
                generator = Generator(
                    level="benchmark",
                    difficulty="hard",
                    grid_size=random.randint(20, 25),
                    fog=random.randint(3, 5),
                    music="rain",
                    camera=1,
                    output=None,
                )
                thread = threading.Thread(
                    target=generator.benchmark,
                    args=(amount, self.log),
                    daemon=True,
                )
                thread.start()

            case "kit":
                commands = {
                    "script": "Run script from data",
                    "scripts": "Get all script names",
                    "vars": "Get current scene vars",
                    "restart": "Restart scene",
                }
                for cmd, desc in commands.items():
                    self.log(f"{cmd:<12} - {desc}")

            case "dev":
                if not engine.DEV:
                    window = engine.Display.get_size()
                    size = (window[0] * 0.52, window[1] * 0.52)
                    pos = (
                        (window[0] - window[0] * 0.52) / 2,
                        (window[1] - window[1] * 0.52) / 2,
                    )
                    self._warning = engine._pygame_gui.windows.UIConfirmationDialog(
                        rect=engine._pygame.Rect(pos, (size[0] * 0.52, size[1] * 0.52)),
                        manager=self.manager,
                        window_title="Warning",
                        action_long_desc=(
                            "Enabling developer mode will unlock powerful "
                            "and potentially dangerous commands.\n"
                            "Use at your own risk."
                        ),
                        action_short_name="Enable",
                        blocking=True,
                    )
            case "script":
                if not engine.DEV:
                    self.log("Permission denied")
                    return
                try:
                    scene = engine.Scene.manager.scene.__dict__
                    for script in args:
                        file = engine.Assets.get(
                            "custom", "scripts", script, exit=False
                        )
                        if not file:
                            self.log(f"File {script} not found")
                            continue
                        with open(file, "r", encoding="utf-8") as f:
                            code = f.read()
                            old_stdout = sys.stdout
                            sys.stdout = buffer = io.StringIO()
                            try:
                                exec(code, scene)
                            except Exception as e:
                                self.log(f"Error in {script}: {e}")
                            finally:
                                sys.stdout = old_stdout
                                output = buffer.getvalue()
                                if output.strip():
                                    self.log(output.strip())
                except Exception as e:
                    self.log(f"Error: {e}")

            case "scripts":
                if not engine.DEV:
                    self.log("Permission denied")
                    return
                scripts = engine.Assets.get("custom", "scripts", exit=False)
                scripts and self.log(
                    ", ".join(
                        {
                            k: v
                            for k, v in sorted(
                                scripts.items(), key=lambda item: item[1]
                            )
                        }
                    )
                )

            case "vars":
                if not engine.DEV:
                    self.log("Permission denied")
                    return
                lines = []
                for name, value in sorted(vars(engine.Scene.manager.scene).items()):
                    if name.startswith("_"):
                        continue
                    typename = type(value).__name__
                    lines.append(f"{name:<10} [{typename}]")
                lines and self.log("\n".join(lines))

            case "restart":
                if not engine.DEV:
                    self.log("Permission denied")
                    return
                engine.Scene.manager.restart()
            case _:
                self.log(f"Unknown command: {command}. Type 'help'.")
