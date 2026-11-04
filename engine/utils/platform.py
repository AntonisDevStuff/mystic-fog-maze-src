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

import sys

__all__ = [
    "is_windows",
    "is_linux",
    "is_mac",
    "is_android",
]


def get_platform():
    return sys.platform


def is_windows():
    return get_platform().startswith("win")


def is_linux():
    return get_platform().startswith("linux")


def is_mac():
    return get_platform().startswith("darwin")


def is_android():
    return hasattr(sys, "getandroidapilevel")


def is_web():
    return get_platform() == "emscripten"
