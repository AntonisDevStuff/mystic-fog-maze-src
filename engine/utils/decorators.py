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

__all__ = ["run_every", "event_listener"]


def run_every(ms):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            if self is None:
                raise ValueError(
                    "The decorator was applied to a function, not a method"
                )
            if not hasattr(self, "is_time"):
                raise ValueError(
                    "The decorator was applied to a method that lacks 'is_time'"
                )
            if self.is_time(ms):
                return method(self, *args, **kwargs)

        return wrapper

    return decorator


def event_listener(event_name):
    def decorator(method):
        def wrapper(self=None, *args, force=False, **kwargs):
            if self is None:
                raise ValueError(
                    "The decorator was applied to a function, not a method"
                )
            if not hasattr(self, "is_custom_event"):
                raise ValueError(
                    "The decorator was applied to a method that lacks 'is_custom_event'"
                )
            if force or self.is_custom_event(event_name):
                return method(self, *args, **kwargs)

        return wrapper

    return decorator
