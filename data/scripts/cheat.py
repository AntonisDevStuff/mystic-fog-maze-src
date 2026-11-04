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

if engine.Scene.manager.selected == "game":
    scene = engine.Scene.manager.scene
    target = None
    target_dir = None

    scene.move_to_player()

    for direction, grid in scene.grids.items():
        for pos, cell in grid.cells.items():
            if cell.state == 2:
                cell.state = 4

            if cell.state == -1:
                target = pos
                target_dir = direction

        grid.create(need_offset=False)

    if target is not None:
        camera_positions = scene.camera_moves

        directions = {v: k for k, v in camera_positions.items()}

        target_position = camera_positions.get(target_dir)

        if target_position is not None:
            while tuple(scene.camera_index) != target_position:
                current_x, current_y = scene.camera_index
                target_x, target_y = target_position

                dx = target_x - current_x
                dy = target_y - current_y

                step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
                step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

                move_direction = directions.get((step_x, step_y))

                if move_direction is None:
                    break

                scene.move_camera(move_direction)
        scene.handle_target(target)
    else:
        print("[Error] No target found")
else:
    print("[Error] That script works only in game scene")
