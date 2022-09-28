import pygame as pg
from . import tools, prepare


class ZombieSprite(pg.sprite.Sprite):
    def __init__(self, position=None):
        """ Display and survivor animation """
        pg.sprite.Sprite.__init__(self)

        self.spriteset = prepare.ZOMBIE_SPRITESET
        self.anim_status = 'idle'
        self.sprite_index = 0
        self.anim_speed = .2
        self.orientation = 0

        self.position = position

        self.image = pg.Surface((140, 140), pg.SRCALPHA, 32)
        self.radius = 35

    def get_current_spritename(self):
        return self.spriteset[self.anim_status]['files'][int(self.sprite_index)]

    def update_sprite(self):
        self.sprite_index += self.anim_speed
        if self.sprite_index >= len(self.spriteset[self.anim_status]['files']):
            self.sprite_index = 0
        self.image.fill((0, 0, 0, 0))
        img = prepare.IMAGES[self.get_current_spritename()]
        # offset = pg.Vector2(self.spriteset[self.weapon_img][self.anim_status]['offset']).rotate(self.orientation)

        rotated = pg.transform.rotate(img, self.orientation)
        # TODO : Rotate around the actual center
        self.image.blit(rotated, (70 - rotated.get_width() / 2, 70 - rotated.get_height() / 2))

    def set_position(self, new_position):
        self.position = new_position


class ZombieControl(ZombieSprite):
    def __init__(self, position=None):
        ZombieSprite.__init__(self, position)
        self._speed_base = 1

        self.status = 'idle'
        self.speed = self._speed_base

        self.force = 35
        self.attack_speed = 36  # Actually attack duration
        self.cooldown = 0

        self.target = None

        # render status
        self.active = False
        self.on_screen = False

        self.current_chunk = f"{int(self.position[0] // 256)}.{int(self.position[1] // 256)}"
        self.kickback_flag = False
        self.kickback_force = 0
        self.kickback_direction = (0,0)

        self.update_sprite()

    def update(self):
        if self.status == 'attack':
            self.cooldown += 1
            if self.cooldown >= self.attack_speed:
                self.cooldown = 0
                self.idle()
        if self.status == 'kickback':
            self.cooldown += 1
            if self.cooldown < self.kickback_force:
                self.position += self.kickback_direction
                self._update_current_chunk()
            else:
                self.idle()
                self.kickback_flag = False

        if self.target is not None:
            angle = pg.Vector2(self.position).angle_to(pg.Vector2(self.target.position)-self.position)
            self.orientation = 315-angle
        if self.on_screen:
            self.update_sprite()

    def kickback(self, direction, force):
        """ The zombie took some damages and move back for a while """
        self.kickback_flag = True
        self.status = 'kickback'
        self.anim_status = 'idle'
        self.kickback_direction = direction
        self.kickback_force = force
        self.cooldown = 0

    def _update_current_chunk(self):
        self.current_chunk = f"{int(self.position[0] // 256)}.{int(self.position[1] // 256)}"

    def move(self, vector):
        self.position += vector
        self._update_current_chunk()
        self.status = 'move'
        self.anim_status = 'move'

    def idle(self):
        self.status = 'idle'
        self.anim_status = 'idle'

    def attack(self):
        self.status = 'attack'
        self.anim_status = 'attack'
        self.sprite_index = 0

    def activate(self):
        self.active = True

