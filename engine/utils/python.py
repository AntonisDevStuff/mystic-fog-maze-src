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

import os
import sys
from os.path import basename, splitext
from importlib.util import spec_from_file_location, module_from_spec
from importlib import reload
from types import ModuleType
from sys import path as sys_path, modules
from os import getcwd

__all__ = ["get_filename", "get_filetype", "load_module", "load_class"]


def get_filename(file_path):
    return splitext(basename(file_path))[0]


def get_filetype(file_path):
    return splitext(basename(file_path))[1]


def load_module(file_path):
    full_path = os.path.normpath(os.path.join(os.getcwd(), file_path))

    if not os.path.exists(full_path):
        return None

    main_dir = os.path.dirname(full_path)
    if main_dir not in sys_path:
        sys_path.append(main_dir)

    module_name = get_filename(full_path)
    spec = spec_from_file_location(module_name, full_path)
    if spec is None or spec.loader is None:
        return None

    module = module_from_spec(spec)
    modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def load_class(file_path, name):
    module = load_module(file_path)
    the_class = getattr(module, name, None)
    return the_class
