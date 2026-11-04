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

Text = engine.Assets.get("scenes", "credits")


class Story(Text):
    def _start(self):
        super()._start()
        self.story = (
            "You are an angel who gave in to gluttony and was cast out of heaven.",
            "As punishment, the gods sealed you inside an infinite maze world.",
            "Every maze leads somewhere new, but your hunger never ends.",
            "Find your way through the mazes before your energy runs out.",
        )
        self.title = "\n".join(self.story)
        self.title_size = 32
        self.title_color = "orange"
        self.text2 = self.username = self.get_empty()

        self.center = (
            engine.Display.get_center()[0],
            engine.Display.get_center()[1] - self.title_size * len(self.story) / 2,
        )
        self.cx, self.cy = self.center

        self.next_scene = "game"
        self.next_scene_args = {"auto": self.auto, "_level": self._level}

        self.event.schedule("show_prompt", 15 * 1000, 1)
        self.event.schedule("typing", 50)
        self.event.schedule("blink", 500)

    def animate(self):
        return

    @staticmethod
    def get_empty():
        return engine.Text("", (0, 0), "white")
