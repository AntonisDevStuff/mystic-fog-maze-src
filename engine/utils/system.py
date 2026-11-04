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
from traceback import extract_tb

import pygame

__all__ = ["error", "quit"]


def error(err):
    error_type = type(err).__name__
    error_message = str(err)
    traceback_list = extract_tb(err.__traceback__)

    error_details = [
        f"File: {os.path.basename(tb.filename)}, Line: {tb.lineno}"
        for tb in traceback_list
    ]
    formatted_traceback = (
        "\n".join(error_details)
        if len(error_details) <= 1
        else "\n" + "\n".join(error_details)
    )

    nice_error_message = (
        f"Type: {error_type}\n"
        f"Message: {error_message}\n"
        f"Traceback: {formatted_traceback}"
    )
    pygame.event.set_grab(False)
    pygame.display.message_box(
        "An unexpected error occurred", nice_error_message, "error"
    )


def quit():
    sys.exit()
