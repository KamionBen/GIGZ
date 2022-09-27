import pygame as pg
from . import tools, prepare


class SurvivorSprite(pg.sprite.Sprite):
    def __init__(self, position=None):
        """ Display and survivor animation """
        pg.sprite.Sprite.__init__(self)

        self.spriteset = prepare.SURVIVOR_SPRITESET
        self.weapon_img = 'handgun'
        self.anim_status = 'idle'
        self.anim_speed = .5
        self.sprite_index = 0
        self.orientation = 0

        self.position = position

        self.image = pg.Surface((140, 140), pg.SRCALPHA, 32)
        self.rect = self.image.get_rect()

        # Hitbox test
        self.radius = 35
        # TODO Penser aux jambes ?

    def get_current_spritename(self):
        return self.spriteset[self.weapon_img][self.anim_status]['files'][int(self.sprite_index)]

    def update_sprite(self):
        self.sprite_index += self.anim_speed
        if self.sprite_index >= len(self.spriteset[self.weapon_img][self.anim_status]['files']):
            self.sprite_index = 0
        self.image.fill((0, 0, 0, 0))
        img = prepare.IMAGES[self.get_current_spritename()]
        # offset = pg.Vector2(self.spriteset[self.weapon_img][self.anim_status]['offset']).rotate(self.orientation)

        rotated = pg.transform.rotate(img, self.orientation)
        # TODO : Rotate around the actual center
        self.image.blit(rotated, (70 - rotated.get_width() / 2, 70 - rotated.get_height() / 2))

        pg.draw.rect(self.image, 'blue', (0, 0, self.rect.width, self.rect.height), 1)

    def set_position(self, new_position):
        self.position = new_position


class SurvivorControl(SurvivorSprite):
    def __init__(self, position=None):
        SurvivorSprite.__init__(self, position)
        self._speed_base = 5

        self.status = 'idle'

        # Stats
        self.speed = self._speed_base
        self.meleeattack_speed = 30
        self.health = [100, 100]

        self.cooldown = 0
        self.meleeattack_flag = True



        # Control
        self.leftstick = pg.Vector2(0, 0)
        self.rightstick = pg.Vector2(0, 0)

        self.move_flag = False
        self.projection = self.leftstick * self.speed

    def get_event(self, event):
        pass

    def meleeattack(self):
        if self.meleeattack_flag:
            self.status = 'meleeattack'
            self.anim_status = 'meleeattack'
            self.cooldown = 0
            self.sprite_index = 0
            self.meleeattack_flag = False

    def update(self):
        if self.leftstick.length_squared() > .3**2:
            self.move_flag = True
        else:
            self.move_flag = False
        self.projection = self.leftstick * self.speed

        if self.status == 'meleeattack':
            self.cooldown += 1
            if self.cooldown >= self.meleeattack_speed:
                self.cooldown = 0
                self.idle()
        self.update_sprite()

    def _set_orientation(self):
        angle = pg.math.Vector2(0, 0)
        leftstick = pg.math.Vector2((self.leftstick[0], self.leftstick[1]))
        if leftstick.length() > .3:
            self.orientation = -angle.angle_to(leftstick)
        rightstick = pg.math.Vector2((self.rightstick[0], self.rightstick[1]))
        if rightstick.length() > .8:
            self.orientation = -angle.angle_to(rightstick)

    def set_leftstick(self, index, value):
        self.leftstick[index] = value
        self._set_orientation()

    def set_rightstick(self, index, value):
        self.rightstick[index] = value
        self._set_orientation()

    def get_damages(self, damages):
        self.health[0] -= damages
        if self.health[0] < 0:
            self.health[0] = 0

    def move(self, vector):
        self.position += vector * self.speed
        if self.status in ['idle']:
            self.status = 'move'
            self.status = 'move'

    def idle(self):
        self.status = 'idle'
        self.anim_status = 'idle'

    def is_moving(self):
        return self.move_flag
