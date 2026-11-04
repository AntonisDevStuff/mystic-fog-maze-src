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

# A custom version of the public domain pygame example: alinets.py

import engine
from pathlib import Path
import random


def _get_data_path():
    return Path(engine._pygame.__file__).parent / "examples" / "data"


class Player(engine._pygame.sprite.Sprite):
    speed = 300
    bounce = 24
    gun_offset = -11
    images = []
    containers = None

    def __init__(self):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = False
        self.origtop = self.rect.top
        self.facing = -1
        self._x = float(self.rect.x)

    def move(self, direction, dt):
        if direction:
            self.facing = direction
        self._x += direction * self.speed * dt
        self._x = max(SCREENRECT.left, min(self._x, SCREENRECT.right - self.rect.width))
        self.rect.x = int(self._x)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Alien(engine._pygame.sprite.Sprite):
    speed = 200
    animcycle = 0.3
    images = []
    containers = None

    def __init__(self):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Alien.speed
        self._anim_timer = 0.0
        self._anim_frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right
        self._x = float(self.rect.x)
        self._y = float(self.rect.y)

    def update(self, dt):
        self._x += self.facing * dt
        self.rect.x = int(self._x)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self._y = self.rect.bottom + 1
            self.rect.y = int(self._y)
            self.rect = self.rect.clamp(SCREENRECT)
            self._x = float(self.rect.x)
            self._y = float(self.rect.y)
        self._anim_timer += dt
        self._anim_frame = int(self._anim_timer / self.animcycle) % 3
        self._anim_frame = 1  # no frames, to make it better for the eye
        self.image = self.images[self._anim_frame]


class Explosion(engine._pygame.sprite.Sprite):
    defaultlife = 0.3
    animcycle = 0.075
    images = []
    containers = None

    def __init__(self, actor):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self, dt):
        self.life -= dt
        self.image = self.images[int(self.life / self.animcycle) % 2]
        if self.life <= 0:
            self.kill()


class Shot(engine._pygame.sprite.Sprite):
    speed = 400
    images = []
    containers = None

    def __init__(self, pos):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)
        self._y = float(self.rect.y)

    def update(self, dt):
        self._y -= self.speed * dt
        self.rect.y = int(self._y)
        if self.rect.top <= 0:
            self.kill()


class Bomb(engine._pygame.sprite.Sprite):
    speed = 250
    images = []
    containers = None

    def __init__(self, alien):
        super().__init__(self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=alien.rect.move(0, 5).midbottom)
        self._y = float(self.rect.y)

    def update(self, dt):
        self._y += self.speed * dt
        self.rect.y = int(self._y)
        if self.rect.bottom >= SCREENRECT.bottom - 10:
            Explosion(self)
            self.kill()


class Secret(engine.Scene):
    def _on_create(self):
        global SCREENRECT
        res = self.display.get_resolution()
        SCREENRECT = engine._pygame.Rect(0, 0, res[0], res[1])

        self.MAX_SHOTS = 2
        self.ALIEN_ODDS = 2.0
        self.BOMB_ODDS = 0.5
        self.ALIEN_RELOAD = 0.3

        self.score = 0
        self.alienreload = self.ALIEN_RELOAD

        self.aliens = engine._pygame.sprite.Group()
        self.shots = engine._pygame.sprite.Group()
        self.bombs = engine._pygame.sprite.Group()
        self.all_sprites = engine._pygame.sprite.Group()
        self.lastalien = engine._pygame.sprite.GroupSingle()

        Player.containers = self.all_sprites
        Alien.containers = self.aliens, self.all_sprites, self.lastalien
        Shot.containers = self.shots, self.all_sprites
        Bomb.containers = self.bombs, self.all_sprites
        Explosion.containers = self.all_sprites

        Player.images = self._load_player_images()
        Explosion.images = self._load_explosion_images()
        Alien.images = self._load_alien_images()
        Bomb.images = [self.load_image("bomb.gif")]
        Shot.images = [self.load_image("shot.gif")]

        self.background = "black"
        self.background_image = engine.Image(
            self._build_background(),
            (0, 0),
            custom_size=(SCREENRECT.width, SCREENRECT.height * 1.7),
        )

        self.boom_sound = engine.SoundEffect(
            engine._pygame.mixer.Sound(str(_get_data_path() / "boom.wav")), volume=0.5
        )
        self.shoot_sound = engine.SoundEffect(
            engine._pygame.mixer.Sound(str(_get_data_path() / "car_door.wav")),
            volume=0.5,
        )
        self.music = engine.Music(str(_get_data_path() / "house_lo.wav"), volume=0.5)
        self.music.play(loops=-1)

        self.controller_motion = [0.0, 0.0]
        self._joy_fire = False
        self._joy_deadzone = 0.2

        shader = engine.Assets.get("custom", "shaders", "arcade")
        engine.Display.set_shader(shader)

    def _start(self):
        self.max_fps = 40
        self.player = Player()
        Alien()

    def _update(self):
        if not self.player.alive():
            self.music.stop()
            self.manager.change("menu")
            self.boom_sound.stop()
            self.shoot_sound.stop()
            return

        kb_direction = (1 if "right" in self.keys_pressed else 0) - (
            1 if "left" in self.keys_pressed else 0
        )

        axis_val = self.controller_motion[0]
        if abs(axis_val) > self._joy_deadzone:
            axis_direction = 1 if axis_val > 0 else -1
        else:
            axis_direction = 0

        direction = axis_direction if axis_direction != 0 else kb_direction
        self.player.move(direction, self.dt)

        firing = (
            "space" in self.keys_pressed or "w" in self.keys_pressed
        ) or self._joy_fire
        if not self.player.reloading and firing and len(self.shots) < self.MAX_SHOTS:
            Shot(self.player.gunpos())
            self.shoot_sound.play()
        self.player.reloading = firing

        if self.alienreload > 0:
            self.alienreload -= self.dt
        elif random.random() < self.ALIEN_ODDS * self.dt:
            Alien()
            self.alienreload = self.ALIEN_RELOAD

        if self.lastalien and random.random() < self.BOMB_ODDS * self.dt:
            Bomb(self.lastalien.sprite)

        self.all_sprites.update(self.dt)

        for alien in engine._pygame.sprite.spritecollide(
            self.player, self.aliens, True
        ):
            self.boom_sound.play()
            Explosion(alien)
            Explosion(self.player)
            self.score += 1
            self.player.kill()

        for alien in engine._pygame.sprite.groupcollide(
            self.aliens, self.shots, True, True
        ):
            self.boom_sound.play()
            Explosion(alien)
            self.score += 1

        for bomb in engine._pygame.sprite.spritecollide(self.player, self.bombs, True):
            self.boom_sound.play()
            Explosion(self.player)
            Explosion(bomb)
            self.player.kill()

        self.score_text = engine.Text(
            f"Score: {self.score}",
            (10, SCREENRECT.height - 30),
            "white",
            size=32,
        )

    def _draw(self):
        engine.Display.draw_image(self.background_image)
        self.all_sprites.draw(self.display.surface)
        self.score_text.draw(self.display.surface, 1)

    def _on_keydown(self, key):
        if key == "escape":
            self.music.stop()
            self.boom_sound.stop()
            self.shoot_sound.stop()
            self.manager.change("menu")

    def _on_joydown(self, id, button):
        if button == 0:
            self._joy_fire = True
        elif button == 3:
            self._on_keydown("escape")
        elif button == 13:
            self.controller_motion[0] = -1
        elif button == 14:
            self.controller_motion[0] = 1.0

    def _on_joyup(self, id, button):
        if button == -1:
            self.controller_motion[0] = 0
        if button == 0:
            self._joy_fire = False

    def _on_error(self, error):
        engine._pygame.mouse.set_visible(True)
        engine._pygame.event.set_grab(False)

    @staticmethod
    def load_image(filename):
        path = str(_get_data_path() / filename)
        return engine._pygame.image.load(path).convert()

    @staticmethod
    def _load_player_images():
        img = Secret.load_image("player1.gif")
        return [img, engine._pygame.transform.flip(img, True, False)]

    @staticmethod
    def _load_explosion_images():
        img = Secret.load_image("explosion1.gif")
        return [img, engine._pygame.transform.flip(img, True, True)]

    @staticmethod
    def _load_alien_images():
        return [
            Secret.load_image(f) for f in ("alien1.gif", "alien2.gif", "alien3.gif")
        ]

    @staticmethod
    def _build_background():
        res = engine.Display.get_resolution()
        bgdtile = Secret.load_image("background.gif")
        background = engine._pygame.Surface(res)
        for x in range(0, res[0], bgdtile.get_width()):
            background.blit(bgdtile, (x, 0))
        return background
