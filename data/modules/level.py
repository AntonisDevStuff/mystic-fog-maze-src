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
from random import randint, random
from datetime import datetime


class Level:
    def __init__(self, path, console):
        self.console = console
        self._path = path
        self._initialize_runtime()

    def end(self):
        level = self.data.get("Info").get("level")
        next = self.data.get("Info").get("next", None)
        if not next:
            return
        with open(
            engine.Assets.get("custom", "levels", "save"), "r+", encoding="utf-8"
        ) as f:
            major, minor = f.read().split("\n")[0].split("=")[1].split("-")
            major, minor = int(major), int(minor)

            next_major, next_minor = next.split("-")
            next_major, next_minor = int(next_major), int(next_minor)

            need_write = (next_major > major or next_minor > minor) and not engine.DEV
            if level == "3-10":
                major, minor = (4, 1) if major == 3 and minor == 10 else (major, minor)
            else:
                if minor >= 10 and major == 4:
                    minor += 1
                elif minor == 10:
                    major += 1
                    minor = 1
                else:
                    minor += 1
            if need_write:
                f.seek(0)
                f.write(f"level={major}-{minor}\n")
                f.truncate()
        return next

    def __repr__(self):
        return str(self.data)

    def _handle_data(self, index=0, end_index=0):
        end_index = len(self._raw_data) if not end_index else end_index

        while index < end_index:
            expression = self._raw_data[index].replace("\t", "").replace(" ", "")
            if expression == "\n":
                index += 1
                continue
            if expression.startswith("#"):
                index += 1
                continue
            if not expression.startswith("@"):
                index += 1
                self._warnings += 1
                continue

            type_name = expression[1:]
            self.data[type_name] = {}

            while True:
                index += 1
                if index == len(self._raw_data):
                    self._errors += 1
                    break

                expression = self._raw_data[index].replace("\t", "").replace(" ", "")
                if expression == "\n":
                    continue
                if expression == "end":
                    break
                if expression.startswith("#"):
                    continue

                if (
                    "grid:" in expression
                    and "[" in expression
                    and "]" not in expression
                ):
                    grid_chunk = expression
                    while True:
                        index += 1
                        if index == len(self._raw_data):
                            self._errors += 1
                            break
                        next_line = self._raw_data[index]
                        grid_chunk += "\n" + next_line
                        if "]" in next_line:
                            break
                    expression = grid_chunk

                assign_expression = expression.split("->")
                key = None
                value = expression
                if len(assign_expression) == 2:
                    key, value = assign_expression

                value = self._convert_type(value, type_name)

                if key:
                    self.data[type_name].update({key: value})

            index += 1

    def _initialize_runtime(self):
        self._warnings = 0
        self._errors = 0

        self._load_data = self._load(self._path, "\n")
        self.data = {}
        self._raw_data = self._load_data[::]
        self._counter = 0

        self._log("-" * 50)

        self._replace_default_vars()
        self._handle_data()

    def _replace_default_vars(self):
        counter = self._counter

        for idx in range(len(self._raw_data)):
            line = self._raw_data[idx]

            if "$counter" in line:
                counter += 1
                self._raw_data[idx] = line.replace("$counter", str(counter))

            if "$randomRange" in line:
                s = line
                start = s.find("$randomRange(")
                if start != -1:
                    open_i = start + len("$randomRange(")
                    args = s[open_i:].split(",", 2)
                    if len(args) < 2:
                        self._raw_data[idx] = s[:start] + "0"
                        continue

                    var1_raw = args[0].strip()
                    var2_raw = args[1].strip()
                    if var2_raw.endswith(")"):
                        var2_raw = var2_raw[:-1]

                    try:
                        var1 = int(float(var1_raw))
                        var2 = int(float(var2_raw))
                        random_number = randint(var1, var2)
                    except ValueError:
                        random_number = 0

                    # keep your original replace pattern
                    self._raw_data[idx] = s.replace(
                        f"$randomRange({args[0]},{args[1]}",
                        str(random_number),
                    )

            if "$random" in line:
                self._raw_data[idx] = self._raw_data[idx].replace(
                    "$random", str(random())
                )

            if "$local_season" in line:
                self._raw_data[idx] = self._raw_data[idx].replace(
                    "$local_season", self._get_season()
                )

        self._counter = counter

    def _convert_type(self, value, declaration):
        type_value = "string"

        if ":" in value:
            type_value, value = value.split(":", 1)

        if type_value == "string":
            return value

        if type_value == "int":
            return int(float(value))

        if type_value == "decimal":
            return float(value)

        if type_value == "boolean":
            return bool(int(value))

        if type_value == "grid":
            s = value.strip()
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1].strip()

            lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
            grid = []

            for ln in lines:
                if "," in ln:
                    parts = [p.strip() for p in ln.split(",") if p.strip() != ""]
                else:
                    parts = [p.strip() for p in ln.split() if p.strip() != ""]
                row = [int(float(p)) for p in parts]
                grid.append(row)

            if grid:
                w = len(grid[0])
                for r in grid:
                    if len(r) != w:
                        engine.utils.error(
                            ValueError(
                                f"Grid rows have inconsistent lengths: {w} vs {len(r)}"
                            )
                        )
                        engine.utils.quit()
            return grid

        if type_value == "var":
            data = self.data[declaration].get(value)
            if data:
                return data
            return value

        if type_value == "print":
            values = value.split(",")
            self._log(
                " ".join(
                    list((self._convert_type(item, declaration) for item in values))
                )
            )

        return value

    def _log(self, string, offset=60):
        if len(string) > offset:
            string = string[:offset] + "..."
        self.console.log(string)

    @staticmethod
    def _load(file_path, new_expression):
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        return data.split(new_expression)

    @staticmethod
    def _get_season():
        month = datetime.now().month
        if month in (12, 1, 2):
            return "winter"
        if month in (3, 4, 5):
            return "spring"
        if month in (6, 7, 8):
            return "summer"
        return "autumn"
