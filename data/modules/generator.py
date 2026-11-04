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

"""
The maze generator:
1. Creates a random 3x3 maze and optionally adds loops.
2. Chooses a start and distant goal using BFS.
3. Reconstructs the path and determines camera transitions.
4. Validates the path, camera requirements, and solution.
5. Calculates steps and splits the maze into 9 camera maps.
6. Writes the completed level to a .level file, or uses a fallback if generation fails.
"""

import os
import random
import time
import sys
from collections import deque

import numpy as np


class Generator:
    CAMERA_NAMES = {
        (0, 0): "up-left",
        (1, 0): "up",
        (2, 0): "up-right",
        (0, 1): "left",
        (1, 1): "center",
        (2, 1): "right",
        (0, 2): "down-left",
        (1, 2): "down",
        (2, 2): "down-right",
    }

    MAP_ORDER = [
        "center",
        "up",
        "down",
        "left",
        "right",
        "up-left",
        "up-right",
        "down-left",
        "down-right",
    ]

    CONFIGS = {
        "easy": {
            "loop_chance": 0.12,
            "min_path": 25,
            "min_camera_cells": 3,
            "min_camera_changes": 2,
            "min_horizontal_transitions": 1,
            "min_vertical_transitions": 1,
            "step_multiplier": 2.2,
            "goal_distance_ratio": 0.45,
            "unique_solution": False,
        },
        "mid": {
            "loop_chance": 0.02,
            "min_path": 50,
            "min_camera_cells": 5,
            "min_camera_changes": 4,
            "min_horizontal_transitions": 2,
            "min_vertical_transitions": 2,
            "step_multiplier": 1.8,
            "goal_distance_ratio": 0.60,
            "unique_solution": True,
        },
        "hard": {
            "loop_chance": 0.0,
            "min_path": 75,
            "min_camera_cells": 7,
            "min_camera_changes": 6,
            "min_horizontal_transitions": 3,
            "min_vertical_transitions": 3,
            "step_multiplier": 1.5,
            "goal_distance_ratio": 0.80,
            "unique_solution": True,
        },
    }

    def __init__(
        self,
        level,
        difficulty,
        grid_size,
        fog,
        music,
        camera,
        output,
        max_attempts=100,
        seed=time.time(),
    ):
        self.level = level
        self.difficulty = difficulty
        self.grid_size = max(5, int(grid_size))
        if self.grid_size % 2 == 0:
            self.grid_size += 1
        self.fog = fog
        self.music = music
        self.camera = camera
        self.output = output
        self.max_attempts = max(1, int(max_attempts))
        self.seed = seed
        self._rng = random.Random(seed)
        self.world_size = self.grid_size * 3

    def _config(self):
        return self.CONFIGS.get(self.difficulty, self.CONFIGS["mid"])

    def create(self):
        os.makedirs(self.output, exist_ok=True)
        config = self._config()

        for _ in range(self.max_attempts):
            result = self._generate_attempt(config)
            if result is None:
                continue

            grid, start, goal, path, cameras = result
            steps = self._calculate_steps(path, cameras, config)
            steps = steps * self._rng.randint(3, 5) if self.fog > 0 else steps
            output = grid.copy()

            sx, sy = start
            gx, gy = goal
            output[sy, sx] = 3
            output[gy, gx] = -1

            self._write_level(
                self.output,
                self.seed,
                self.level,
                output,
                steps,
                self.fog,
                self.music,
                self.camera,
            )
            return True

        self._write_fallback_level()
        return False

    def _generate_attempt(self, config):
        grid = self._generate_global_grid(config)
        start, distances = self._choose_start(grid)

        if start is None:
            return None

        goal = self._choose_goal(start, distances, config)
        if goal is None:
            return None

        path = self._reconstruct_path(distances, start, goal)
        if not path:
            return None

        cameras = self._camera_path(path)

        if not self._validate_path_length(path, config):
            return None
        if not self._validate_camera_requirements(cameras, config):
            return None
        if not self._validate_camera_path(path):
            return None
        if config["unique_solution"] and self._has_multiple_paths(grid, start, goal):
            return None
        if not self._validate_level(grid, start, goal, path, cameras, config):
            return None

        return grid, start, goal, path, cameras

    def benchmark(self, count=1000, output=None):
        count = max(1, int(count))
        config = self._config()
        times, paths, steps, attempts_used = [], [], [], []
        fallbacks = 0
        total_start = time.perf_counter()

        output = output or print
        output(f"Benchmarking...")
        for i in range(count):
            start_time = time.perf_counter()
            result = None
            attempts = 0

            for attempts in range(1, self.max_attempts + 1):
                result = self._generate_attempt(config)
                if result is not None:
                    break

            times.append(time.perf_counter() - start_time)
            attempts_used.append(attempts)

            if result is None:
                fallbacks += 1
                continue

            _, _, _, path, cameras = result
            paths.append(len(path) - 1)
            steps.append(self._calculate_steps(path, cameras, config))
            output(f"\rProgress: {(i + 1) / count * 100:6.1f}%", end="", flush=True)

        total_time = time.perf_counter() - total_start
        times = np.asarray(times, dtype=np.float64)
        output("Results:", flush=True)
        output(
            f"{count} mazes | {self.difficulty} | " f"{self.grid_size}x{self.grid_size}"
        )
        output(
            f"time avg={times.mean():.2f}sec "
            f"min={times.min():.2f}sec "
            f"max={times.max():.2f}sec"
        )
        output(f"speed={count/total_time:.1f}/s ")
        if fallbacks:
            output(f"fallbacks={fallbacks}/{count}")

        if not paths:
            return

        steps = np.asarray(steps, dtype=np.float64)
        attempts = np.asarray(attempts_used, dtype=np.float64)

        output(
            f"steps avg={steps.mean():.1f} "
            f"min={steps.min():.0f} max={steps.max():.0f}"
        )

    def _generate_global_grid(self, config):
        size = self.world_size
        grid = np.ones((size, size), dtype=np.int8)
        positions = list(range(1, size - 1, 2))
        start = (self._rng.choice(positions), self._rng.choice(positions))
        stack = [start]
        visited = {start}
        grid[start[1], start[0]] = 2
        directions = ((2, 0), (-2, 0), (0, 2), (0, -2))

        while stack:
            x, y = stack[-1]
            shuffled = list(directions)
            self._rng.shuffle(shuffled)
            next_cell = None

            for dx, dy in shuffled:
                nx, ny = x + dx, y + dy
                if not (1 <= nx < size - 1 and 1 <= ny < size - 1):
                    continue
                if (nx, ny) in visited:
                    continue
                next_cell = nx, ny, dx, dy
                break

            if next_cell is None:
                stack.pop()
                continue

            nx, ny, dx, dy = next_cell
            grid[y + dy // 2, x + dx // 2] = 2
            grid[ny, nx] = 2
            visited.add((nx, ny))
            stack.append((nx, ny))

        self._add_loops(grid, config["loop_chance"])
        self._set_global_walls(grid)
        return grid

    def _add_loops(self, grid, chance):
        if chance <= 0:
            return

        height, width = grid.shape
        candidates = []

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if grid[y, x] != 1:
                    continue

                horizontal = grid[y, x - 1] == 2 and grid[y, x + 1] == 2
                vertical = grid[y - 1, x] == 2 and grid[y + 1, x] == 2

                if horizontal or vertical:
                    candidates.append((x, y))

        self._rng.shuffle(candidates)

        for x, y in candidates:
            if self._rng.random() < chance:
                grid[y, x] = 2

    def _set_global_walls(self, grid):
        grid[0, :] = grid[-1, :] = 1
        grid[:, 0] = grid[:, -1] = 1

    def _choose_start(self, grid):
        center = (self.grid_size + 1, self.grid_size + 1)
        open_cells = np.argwhere(grid == 2)

        candidates = [
            (int(x), int(y)) for y, x in open_cells if x % 2 == 1 and y % 2 == 1
        ]

        if not candidates:
            candidates = [(int(x), int(y)) for y, x in open_cells]

        if not candidates:
            return None, None

        if (
            0 <= center[0] < self.world_size
            and 0 <= center[1] < self.world_size
            and grid[center[1], center[0]] == 2
        ):
            candidates.append(center)

        start = self._rng.choice(candidates)
        return start, self._distance_array(grid, start)

    def _choose_goal(self, start, distances, config):
        valid = distances >= 0
        if not np.any(valid):
            return None

        max_distance = int(distances[valid].max())
        minimum = max(
            config["min_path"],
            int(max_distance * config["goal_distance_ratio"]),
        )

        positions = np.argwhere(distances >= minimum)
        candidates = []

        for y, x in positions:
            candidate = (int(x), int(y))
            if candidate == start:
                continue

            path = self._reconstruct_path(distances, start, candidate)
            if not path:
                continue

            cameras = self._camera_path(path)
            if self._validate_camera_requirements(cameras, config):
                candidates.append(candidate)

        if not candidates:
            positions = np.argwhere(distances == max_distance)
            candidates = [
                (int(x), int(y)) for y, x in positions if (int(x), int(y)) != start
            ]

        return self._rng.choice(candidates) if candidates else None

    def _distance_array(self, grid, start):
        height, width = grid.shape
        distances = np.full((height, width), -1, dtype=np.int32)
        sx, sy = start
        distances[sy, sx] = 0
        queue = deque([start])

        while queue:
            x, y = queue.popleft()
            distance = distances[y, x] + 1

            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if distances[ny, nx] != -1 or grid[ny, nx] != 2:
                    continue

                distances[ny, nx] = distance
                queue.append((nx, ny))

        return distances

    def _reconstruct_path(self, distances, start, goal):
        gx, gy = goal
        if distances[gy, gx] < 0:
            return []

        path = [goal]
        current = goal

        while current != start:
            x, y = current
            distance = distances[y, x]
            candidates = []

            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if (
                    0 <= nx < distances.shape[1]
                    and 0 <= ny < distances.shape[0]
                    and distances[ny, nx] == distance - 1
                ):
                    candidates.append((nx, ny))

            if not candidates:
                return []

            candidates.sort(key=lambda p: (self._camera_position(*p), p[1], p[0]))
            current = candidates[0]
            path.append(current)

        path.reverse()
        return path

    def _has_multiple_paths(self, grid, start, goal):
        height, width = grid.shape
        distances = np.full((height, width), -1, dtype=np.int32)
        counts = np.zeros((height, width), dtype=np.uint8)
        sx, sy = start
        gx, gy = goal

        distances[sy, sx] = 0
        counts[sy, sx] = 1
        queue = deque([start])

        while queue:
            x, y = queue.popleft()

            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if grid[ny, nx] != 2:
                    continue

                new_distance = distances[y, x] + 1

                if distances[ny, nx] == -1:
                    distances[ny, nx] = new_distance
                    counts[ny, nx] = counts[y, x]
                    queue.append((nx, ny))
                elif distances[ny, nx] == new_distance:
                    counts[ny, nx] = min(2, int(counts[ny, nx]) + int(counts[y, x]))

        return counts[gy, gx] > 1

    def _camera_position(self, x, y):
        size = self.grid_size
        return min(2, x // size), min(2, y // size)

    def _camera_path(self, path):
        result = []

        for x, y in path:
            camera = self._camera_position(x, y)
            if not result or result[-1] != camera:
                result.append(camera)

        return result

    def _validate_camera_path(self, path):
        if not path:
            return False

        previous = self._camera_position(*path[0])

        for x, y in path[1:]:
            current = self._camera_position(x, y)

            if current == previous:
                continue

            dx = abs(current[0] - previous[0])
            dy = abs(current[1] - previous[1])

            if dx + dy != 1:
                return False

            previous = current

        return True

    def _validate_camera_requirements(self, cameras, config):
        if len(cameras) < config["min_camera_cells"]:
            return False

        if len(cameras) - 1 < config["min_camera_changes"]:
            return False

        horizontal = vertical = 0

        for previous, current in zip(cameras, cameras[1:]):
            dx = current[0] - previous[0]
            dy = current[1] - previous[1]

            if dx:
                horizontal += 1
            if dy:
                vertical += 1

        return (
            horizontal >= config["min_horizontal_transitions"]
            and vertical >= config["min_vertical_transitions"]
        )

    def _validate_path_length(self, path, config):
        return bool(path) and len(path) - 1 >= config["min_path"]

    def _calculate_steps(self, path, cameras, config):
        if not path:
            return 0

        movement = len(path) - 1
        camera_changes = max(0, len(cameras) - 1)
        base = movement + camera_changes
        scaled = int(round(base * config["step_multiplier"]))

        return max(config["min_path"], scaled)

    def _validate_global_boundary(self, grid):
        return (
            np.all(grid[0, :] == 1)
            and np.all(grid[-1, :] == 1)
            and np.all(grid[:, 0] == 1)
            and np.all(grid[:, -1] == 1)
        )

    def _validate_level(self, grid, start, goal, path, cameras, config):
        if grid.shape != (self.world_size, self.world_size):
            return False

        if not self._validate_global_boundary(grid):
            return False

        sx, sy = start
        gx, gy = goal

        if grid[sy, sx] != 2 or grid[gy, gx] != 2:
            return False

        if path[0] != start or path[-1] != goal:
            return False

        if not self._validate_path_length(path, config):
            return False

        if not self._validate_camera_path(path):
            return False

        if not self._validate_camera_requirements(cameras, config):
            return False

        for previous, current in zip(path, path[1:]):
            if abs(current[0] - previous[0]) + abs(current[1] - previous[1]) != 1:
                return False

        if any(grid[y, x] != 2 for x, y in path):
            return False

        return all(0 <= cx < 3 and 0 <= cy < 3 for cx, cy in cameras)

    def _split_global_grid(self, grid):
        size = self.grid_size
        grids = {}

        for (cx, cy), name in self.CAMERA_NAMES.items():
            sx, sy = cx * size, cy * size
            local = np.ones((size, size), dtype=np.int8)
            ex = min(sx + size, grid.shape[1])
            ey = min(sy + size, grid.shape[0])
            local[: ey - sy, : ex - sx] = grid[sy:ey, sx:ex]
            grids[name] = local

        return grids

    def _write_level(self, output, seed, level, grid, steps, fog, music, camera):
        filepath = os.path.join(output, f"{level}.level")
        grids = self._split_global_grid(grid)

        lines = [
            "# Game: Mystic Fog Maze",
            f"# Seed: {seed}",
            "",
            "@Info",
            f"\tlevel -> string:{level}",
            f"\tnext -> string:{self._next_level(level)}",
            "\tname -> string:Endless",
            "\tauthor -> string:Computer",
            "\tprint -> string:Level:,var:level,string::,var:name",
            "\tprint -> string:Creator:,var:author",
            "end",
            "",
            "@Settings",
            f"\tfog -> int:{fog}",
            f"\tmusic -> str:{music}",
            f"\tsteps -> int:{steps}",
            f"\tcamera -> boolean:{1 if camera else 0}",
            "end",
            "",
            "@Map",
        ]

        for index, name in enumerate(self.MAP_ORDER):
            local = grids[name]
            lines.append(f"\t{name} -> grid: [")

            for y, row in enumerate(local):
                values = ", ".join(str(int(value)) for value in row)
                if y < len(local) - 1:
                    values += ","
                lines.append(f"\t\t{values}")

            lines.append("\t]")

            if index < len(self.MAP_ORDER) - 1:
                lines.append("")

        lines.append("end")

        with open(filepath, "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")

    def _write_fallback_level(self):
        size = 6
        world_size = size * 3

        grid = np.full((world_size, world_size), 2, dtype=np.int8)

        grid[0, 0] = 3

        grid[-1, -1] = -1

        steps = 999

        old_grid_size = self.grid_size
        old_world_size = self.world_size

        self.grid_size = size
        self.world_size = world_size

        self._write_level(
            self.output,
            self.seed,
            self.level,
            grid,
            steps,
            0,
            self.music,
            True,
        )

    def _next_level(self, level):
        parts = level.split("-")

        if len(parts) == 2:
            try:
                return f"{parts[0]}-{int(parts[1]) + 1}"
            except ValueError:
                pass

        return "end"
