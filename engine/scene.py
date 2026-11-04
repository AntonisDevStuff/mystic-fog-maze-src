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

from .display import Display
from .assets import Assets
from .wrapper import Text, Image
from .utils import error, quit, is_windows, is_linux, is_mac

from time import perf_counter as time
from json import load as json_load

import pygame
from pygame._sdl2 import controller

# Events & Lifecycle
# Last Update: 11/3/26
# ==================
# Lifecycle:
#   _start()                      once when scene starts
#   _update()                     every frame
#   _draw()                       every frame
#   _paused_update()              every frame when paused
#   _paused_draw()                every frame when paused
#
#   _on_create()                  scene created
#   _on_exit()                    scene exits
#   _on_quit()                    quit app
#   _on_restart()                 restart scene
#   _on_reset()                   reset scene
#   _on_event(event)              scene event
#   _on_change()                  change scene
#   _on_resume()                  resume from pause
#   _on_pause()                   pause
#   _on_error(error)              error occurred
#
# Keyboard:
#   _on_keydown(key)              "a", "space", "return", etc
#   _on_keyup(key)                "a", "space", "return", etc
#   _on_keypressed(keys)          {"a", "space"}, etc
#
# Mouse:
#   _on_mousemove(pos, movement)  pos=(x, y), movement=(dx, dy)
#   _on_mousedown(button)         "left", "right", "middle", "back", "forward"
#   _on_mouseup(button)           "left", "right", "middle", "back", "forward"
#   _on_mousepressed(buttons)     {"left", "right"}, etc
#   _on_mousewheel(direction)     "up" or "down"
#
# Joystick:
#   _on_joyaxismotion(id, axis, value)        id=0+, axis=0+, value=-1.0 to 1.0
#   _on_joyballmotion(id, ball, rel)          id=0+, ball=0+, rel=(dx, dy)
#   _on_joydown(id, button)                   id=0+, button=0+
#   _on_joyup(id, button)                     id=0+, button=0+
#   _on_joyhatmotion(id, hat, value)          id=0+, hat=0+, value=(-1,0,1, -1,0,1)
#   _on_joydeviceadded(id)                    id=0+
#   _on_joydeviceremoved(id)                  id=0+
# ==================

CONTROLLER_MAP = {
    0: pygame.CONTROLLER_BUTTON_A,
    1: pygame.CONTROLLER_BUTTON_B,
    2: pygame.CONTROLLER_BUTTON_X,
    3: pygame.CONTROLLER_BUTTON_Y,
    4: pygame.CONTROLLER_BUTTON_BACK,
    5: pygame.CONTROLLER_BUTTON_GUIDE,
    6: pygame.CONTROLLER_BUTTON_START,
    7: pygame.CONTROLLER_BUTTON_LEFTSTICK,
    8: pygame.CONTROLLER_BUTTON_RIGHTSTICK,
    9: pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
    10: pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
    11: pygame.CONTROLLER_BUTTON_DPAD_UP,
    12: pygame.CONTROLLER_BUTTON_DPAD_DOWN,
    13: pygame.CONTROLLER_BUTTON_DPAD_LEFT,
    14: pygame.CONTROLLER_BUTTON_DPAD_RIGHT,
}


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class SceneManager:
    scenes = {}
    selected = None

    @classproperty
    def scene(cls):
        if not cls.selected:
            error(RuntimeError("No scene selected"))
            quit()
        return cls.scenes[cls.selected][1]

    @classmethod
    def start(cls):
        while True:
            if not cls.selected:
                error(RuntimeError("No scene selected"))
                quit()
            name, scene_object, _ = cls.scenes[cls.selected]
            scene_object._Scene__run()

    @classmethod
    def create(cls, name, **kwargs):
        scene_cls = Assets.get("data", "scenes", name)
        if not scene_cls:
            error(RuntimeError(f"Scene: {name}, not found in data/scenes folder"))
            quit()
        obj = scene_cls(**kwargs)
        cls.scenes[name] = (name, obj, kwargs)
        cls.selected = name

    @classmethod
    def change(cls, name, **kwargs):
        scene_obj = cls.scene
        scene_obj._on_change()
        scene_obj._Scene__running = False
        cls.create(name, **kwargs)

    @classmethod
    def pause(cls):
        scene_obj = cls.scene
        scene_obj._on_pause()
        scene_obj._Scene__paused = True
        scene_obj._Scene__pause_last_time = time()

    @classmethod
    def resume(cls):
        scene_obj = cls.scene
        scene_obj._on_resume()
        scene_obj._Scene__paused = False
        scene_obj._Scene__dt = 0

    @classmethod
    def restart(cls):
        scene_obj = cls.scene
        scene_obj._on_restart()
        scene_obj._Scene__running = False

    @classmethod
    def reset(cls):
        name, scene_obj, kwargs = cls.scenes[cls.selected]
        scene_obj._on_reset()
        scene_obj._Scene__running = False
        cls.create(name, **kwargs)

    @classmethod
    def exit(cls):
        scene_obj = cls.scene
        scene_obj._on_exit()
        scene_obj._Scene__running = False
        cls.selected = None

    @classmethod
    def quit(cls):
        scene_obj = cls.scene
        scene_obj._on_quit()
        quit()


class SceneEvent:
    def __init__(self, scene):
        self.__data = {}
        self.__scene = scene

    def create(self, name, state=0, **kwargs):
        event_id = pygame.event.custom_type()
        create_time = self._now(state)
        last_time = create_time
        basic_argv = {
            "name": name,
            "custom": True,
            "create_time": create_time,
            "calls": 0,
            "last_time": last_time,
            "timer": None,
            "loops": None,
            "state": state,
        }
        kwargs.update(basic_argv)
        event = pygame.event.Event(event_id, kwargs)
        self.__data[name] = event
        return event_id

    def get(self, name):
        return self.__data.get(name, None)

    def remove(self, name):
        return self.__data.pop(name)

    def post(self, name):
        event = self.get(name)
        return pygame.event.post(event)

    def match(self, name, other_event):
        event = self.get(name)
        return event.type == other_event.type

    def schedule(self, name, timer, loops=-1):
        event = self.get(name)
        event.timer = timer
        event.loops = loops

    def update(self, state):
        for event_name in self.__data:
            event = self.get(event_name)
            if not (self._is_state(state, event.state)):
                continue
            if not event.timer:
                continue
            if event.calls == event.loops:
                continue
            self._update_time(event)

    def _now(self, state):
        runtime = self.__scene.runtime
        pausetime = self.__scene.pausetime
        if state == 0:
            return runtime + pausetime
        now = runtime if state > 0 else pausetime
        return now

    def _update_time(self, event):
        now = self._now(event.state)
        diff = (now - event.last_time) * 1000
        is_time = diff >= event.timer
        if not is_time:
            return
        self.post(event.name)
        event.last_time = now
        event.calls += 1

    @staticmethod
    def _is_state(state, event_state):
        same = event_state == state
        is_zero = event_state == 0
        return same or is_zero


class Scene:
    _joysticks = {}
    _global_runtime = _global_pausetime = 0
    _controler_map = CONTROLLER_MAP
    __display_fps = False
    __global_start_time = time()

    def __init__(self, **kwargs):
        if not self.display.window:
            error(
                RuntimeError(
                    "Display has not been initialized! Call Display.init first."
                )
            )
            self.quit()
        self.__initialize(kwargs)

    @classproperty
    def manager(cls):
        return SceneManager

    @classproperty
    def display(cls):
        return Display

    @classproperty
    def assets(cls):
        return Assets

    @classproperty
    def global_runtime(cls):
        return cls._global_runtime

    @classproperty
    def global_pausetime(cls):
        return cls._global_pausetime

    @property
    def event(self):
        return self._event

    @property
    def events(self):
        return self._events

    @property
    def custom_events(self):
        return self._custom_events

    @property
    def keys_pressed(self):
        return self._keys_pressed

    @property
    def buttons_pressed(self):
        return self._buttons_pressed

    @property
    def joystick_motion(self):
        return self._joy_motion

    @property
    def joysticks(self):
        return self._joysticks

    @property
    def dt(self):
        return self._dt

    @property
    def fps(self):
        return self._fps

    @property
    def max_fps(self):
        return self._max_fps

    @max_fps.setter
    def max_fps(self, value):
        self._max_fps = value

    @property
    def background(self):
        return self._background_color

    @background.setter
    def background(self, value):
        self._background_color = value

    @property
    def runtime(self):
        return self._runtime

    @property
    def pausetime(self):
        return self._pausetime

    def is_time(self, ms):
        multiplier = 1 / ms * 1000
        return int(self._runtime * multiplier) != int(
            (self._runtime - self._dt) * multiplier
        )

    def is_event(self, event_id):
        return event_id in self._events

    def is_custom_event(self, event_name):
        return event_name in self._custom_events

    def is_paused(self):
        return self.__paused

    def _start(self):
        raise NotImplementedError("start() must be overridden in subclass.")

    def _update(self):
        raise NotImplementedError("update() must be overridden in subclass.")

    def _draw(self):
        raise NotImplementedError("draw() must be overridden in subclass.")

    def _paused_update(self):
        pass

    def _paused_draw(self):
        pass

    def _on_create(self):
        pass

    def _on_exit(self):
        pass

    def _on_quit(self):
        pass

    def _on_restart(self):
        pass

    def _on_reset(self):
        pass

    def _on_change(self):
        pass

    def _on_resume(self):
        pass

    def _on_pause(self):
        pass

    def _on_error(self, error):
        pass

    def _on_event(self, event):
        pass

    def _on_keydown(self, key):
        pass

    def _on_keyup(self, key):
        pass

    def _on_keypressed(self, keys):
        pass

    def _on_mousemove(self, position, movement):
        pass

    def _on_mousedown(self, button):
        pass

    def _on_mouseup(self, button):
        pass

    def _on_mousepressed(self, buttons):
        pass

    def _on_mousewheel(self, wheel):
        pass

    def _on_joyaxismotion(self, id, axis, value):
        pass

    def _on_joyballmotion(self, id, ball, rel):
        pass

    def _on_joydown(self, id, button):
        pass

    def _on_joyup(self, id, button):
        pass

    def _on_joyhatmotion(self, id, hat, value):
        pass

    def _on_joydeviceadded(self, id):
        pass

    def _on_joydeviceremoved(self, id):
        pass

    def _on_paused_event(self, event):
        pass

    def _on_paused_keydown(self, key):
        pass

    def _on_paused_keyup(self, key):
        pass

    def _on_paused_keypressed(self, key):
        pass

    def _on_paused_mousemove(self, position, movement):
        pass

    def _on_paused_mousedown(self, button):
        pass

    def _on_paused_mouseup(self, button):
        pass

    def _on_paused_mousepressed(self, buttons):
        pass

    def _on_paused_mousewheel(self, wheel):
        pass

    def _on_paused_joyaxismotion(self, id, axis, value):
        pass

    def _on_paused_joyballmotion(self, id, ball, rel):
        pass

    def _on_paused_joydown(self, id, button):
        pass

    def _on_paused_joyup(self, id, button):
        pass

    def _on_paused_joyhatmotion(self, id, hat, value):
        pass

    def _on_paused_joydeviceadded(self, id):
        pass

    def _on_paused_joydeviceremoved(self, id):
        pass

    def __run(self):
        try:
            self.__initialize_runtime()
            self._start()
            while self.__running:
                self.__handle_events()
                self.__update()
                self.__render()
                self.__flip()
            if not self.manager.selected:
                quit()
        except Exception as e:
            self.__handle_error(e)

    def __initialize(self, kwargs):
        try:
            self._max_fps = -1
            self._background_color = (0, 0, 0)
            self.__running = True
            self.__paused = False
            self.__event_handlers = {
                True: (
                    self._on_paused_keydown,
                    self._on_paused_keyup,
                    self._on_paused_keypressed,
                    self._on_paused_mousemove,
                    self._on_paused_mousedown,
                    self._on_paused_mouseup,
                    self._on_paused_mousepressed,
                    self._on_paused_mousewheel,
                    self._on_paused_joyaxismotion,
                    self._on_paused_joyballmotion,
                    self._on_paused_joydown,
                    self._on_paused_joyup,
                    self._on_paused_joyhatmotion,
                    self._on_paused_joydeviceadded,
                    self._on_paused_joydeviceremoved,
                    self._on_paused_event,
                ),
                False: (
                    self._on_keydown,
                    self._on_keyup,
                    self._on_keypressed,
                    self._on_mousemove,
                    self._on_mousedown,
                    self._on_mouseup,
                    self._on_mousepressed,
                    self._on_mousewheel,
                    self._on_joyaxismotion,
                    self._on_joyballmotion,
                    self._on_joydown,
                    self._on_joyup,
                    self._on_joyhatmotion,
                    self._on_joydeviceadded,
                    self._on_joydeviceremoved,
                    self._on_event,
                ),
            }
            for k, v in kwargs.items():
                setattr(self, k, v)
            self._on_create()
        except Exception as e:
            self.__handle_error(e)

    def __initialize_runtime(self):
        self._dt = self._fps = self._runtime = self._pausetime = 0
        self._joy_motion = dict()
        self._keys_pressed = set()
        self._buttons_pressed = set()
        self._joysticks_pressed = set()
        self._events = set()
        self._custom_events = set()

        self._event = SceneEvent(self)

        self._start_time = time()
        self._cursor = None

        self.__running = True

        self.__last_surface = Display.surface

    def __handle_error(self, err):
        if err:
            self._on_error(err)
            error(err)
        quit()

    def __handle_events(self):
        self._events.clear()
        self._custom_events.clear()
        self._event.update(-1 if self.__paused else 1)
        (
            on_keydown,
            on_keyup,
            on_keypressed,
            on_mousemove,
            on_mousedown,
            on_mouseup,
            on_mousepressed,
            on_mousewheel,
            on_joyaxismotion,
            on_joyballmotion,
            on_joydown,
            on_joyup,
            on_joyhatmotion,
            on_joydeviceadded,
            on_joydeviceremoved,
            on_event,
        ) = self.__event_handlers[self.__paused]
        for event in pygame.event.get():
            self._events.add(event.type)
            if hasattr(event, "custom"):
                self._custom_events.add(event.name)
                continue
            if event.type == pygame.QUIT:
                self.manager.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    on_mousedown("left")
                    self._buttons_pressed.add("left")
                elif event.button == 2:
                    on_mousedown("middle")
                    self._buttons_pressed.add("middle")
                elif event.button == 3:
                    on_mousedown("right")
                    self._buttons_pressed.add("right")
                elif event.button == 4:
                    pass
                elif event.button == 5:
                    pass
                elif event.button == 6:
                    on_mousedown("back")
                    self._buttons_pressed.add("back")
                elif event.button == 7:
                    on_mousedown("forward")
                    self._buttons_pressed.add("forward")
                else:
                    name = f"button_{event.button}"
                    on_mousedown(name)
                    self._buttons_pressed.add(name)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    on_mouseup("left")
                    self._buttons_pressed.discard("left")
                elif event.button == 2:
                    on_mouseup("middle")
                    self._buttons_pressed.discard("middle")
                elif event.button == 3:
                    on_mouseup("right")
                    self._buttons_pressed.discard("right")
                elif event.button == 4:
                    pass
                elif event.button == 5:
                    pass
                elif event.button == 6:
                    on_mouseup("back")
                    self._buttons_pressed.discard("back")
                elif event.button == 7:
                    on_mouseup("forward")
                    self._buttons_pressed.discard("forward")
                else:
                    name = f"button_{event.button}"
                    on_mouseup(name)
                    self._buttons_pressed.discard(name)
            elif event.type == pygame.MOUSEWHEEL:
                on_mousewheel("up") if event.y > 0 else on_mousewheel("down")

            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                self._keys_pressed.add(key)
                on_keydown(key)
                key == "f3" and self.__toggle_fps()
            elif event.type == pygame.KEYUP:
                key = pygame.key.name(event.key)
                self._keys_pressed.discard(key)
                on_keyup(key)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                pos = (
                    mouse_pos[0]
                    * Display.get_resolution()[0]
                    / pygame.display.get_window_size()[0],
                    mouse_pos[1]
                    * Display.get_resolution()[1]
                    / pygame.display.get_window_size()[1],
                )
                on_mousemove(pos, event.rel)
            elif event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                name = joy.get_name().lower()
                # controller
                pygame._sdl2.controller.init()
                controller = pygame._sdl2.controller.Controller.from_joystick(joy)
                self.joysticks[joy.get_instance_id()] = controller
                on_joydeviceadded(joy.get_instance_id())
            elif event.type == pygame.JOYDEVICEREMOVED:
                on_joydeviceremoved(event.instance_id)
                if event.instance_id in self.joysticks:
                    del self.joysticks[event.instance_id]
            elif event.type == pygame.JOYBUTTONDOWN:
                joy = self.joysticks[event.instance_id]
                down = -1
                for id, button in self._controler_map.items():
                    if id in self._joysticks_pressed:
                        continue
                    if joy.get_button(button):
                        self._joysticks_pressed.add(id)
                        down = id
                        break
                down != -1 and self._on_joydown(joy, down)
            elif event.type == pygame.JOYBUTTONUP:
                joy = self.joysticks[event.instance_id]
                up = -1
                for id, button in self._controler_map.items():
                    if id not in self._joysticks_pressed:
                        continue
                    if not joy.get_button(button):
                        self._joysticks_pressed.discard(id)
                        up = id
                        break
                up != -1 and self._on_joyup(joy, up)
            elif event.type == pygame.JOYAXISMOTION:
                self._joy_motion[event.axis] = event.value
                on_joyaxismotion(event.instance_id, event.axis, event.value)
            elif event.type == pygame.JOYBALLMOTION:
                on_joyballmotion(event.instance_id, event.ball, event.rel)
            elif event.type == pygame.JOYHATMOTION:
                on_joyhatmotion(event.instance_id, event.hat, event.value)
                if event.value != (0, 0):
                    on_joydown(
                        event.instance_id,
                        {
                            (-1, 0): 13,
                            (1, 0): 14,
                            (0, 1): 11,
                            (0, -1): 12,
                        }.get(event.value),
                    )
                else:
                    on_joyup(event.instance_id, -1)
            on_event(event)
        if self._keys_pressed:
            on_keypressed(self._keys_pressed)
        if self._buttons_pressed:
            on_mousepressed(self._buttons_pressed)

    def __update(self):
        update = self._paused_update if self.__paused else self._update
        update_timers = (
            self.__update_paused_timers if self.__paused else self.__update_timers
        )
        update()
        update_timers()

    def __update_timers(self):
        delta = time() - self._start_time
        global_delta = time() - self.__global_start_time
        self._runtime = delta - self._pausetime
        self._global_runtime = global_delta - self._global_pausetime

    def __update_paused_timers(self):
        delta = time() - self.__pause_last_time
        self._pausetime += delta
        self._global_pausetime += delta
        self.__pause_last_time = time()

    def __update_fps(self):
        if self.is_time(250):
            self._fps = Display.clock.get_fps()

    def __render(self):
        self.__draw_background()
        if not self.__paused:
            self._draw()
            self.__last_surface = Display.surface.copy()
        else:
            Display.surface.blit(self.__last_surface)
            self._paused_draw()
        self.__display_fps and self.__draw_fps()

    def __draw_background(self):
        Display.surface.fill(self._background_color)

    def __draw_display(self):
        Display.render_screen()

    def __draw_fps(self):
        fps = Text(
            str(int(self.fps)),
            (Display.get_center()[0], 10),
            "green",
            size=64,
            align="center",
        )
        Display.draw_text(fps)

    def __flip(self):
        self.__update_fps()
        self._dt = round(Display.clock.tick(self._max_fps) / 1000, 3)
        self.__draw_display()
        pygame.display.flip()

    def __toggle_fps(self):
        Scene.__display_fps = not Scene.__display_fps
