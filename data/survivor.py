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

        self.position = pg.Vector2(position)
        self.projection = pg.Vector2(0, 0)

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

        # Debug lines
        # Rect
        pg.draw.rect(self.image, 'blue', (0, 0, self.rect.width, self.rect.height), 1)
        # Radius
        pg.draw.circle(self.image, 'green', (70, 70), self.radius, 1)
        # Projection
        direction = self.projection.copy()
        if direction.length_squared() > 0:
            direction.scale_to_length(200)
            pg.draw.line(self.image, 'blue', (70, 70), (70, 70) + direction, 1)
        # Orientation
        front = pg.Vector2(200, 0).rotate(-self.orientation)
        pg.draw.line(self.image, 'green', (70, 70), (70, 70) + front, 1)

    def set_position(self, new_position):
        self.position = new_position


class SurvivorControl(SurvivorSprite):
    def __init__(self, position=None):
        SurvivorSprite.__init__(self, position)
        self._speed_base = 5

        self.status = 'idle'
        self.weapon = prepare.WEAPONS[0]
        self.weapon_img = self.weapon.sprite

        # Stats
        self.speed = self._speed_base
        self.meleeattack_speed = 30
        self.health = [100, 100]

        self.cooldown = 0
        self.meleeattack_flag = True
        self.move_flag = False
        self.shoot_flag = True

        # Control
        self.leftstick = pg.Vector2(0, 0)
        self.rightstick = pg.Vector2(0, 0)
        self.lefttrigger = 0
        self.righttrigger = 0

        self.current_chunks = []
        self.projection_x = tools.Projection(self.position, self.radius, (self.leftstick.x * self.speed, 0))
        self.projection_y = tools.Projection(self.position, self.radius, (0, self.leftstick.y * self.speed))

    def update_current_chunks(self):
        """ Update the chunks where the game need to check for collision"""
        self.current_chunks = []
        topleft = f"{int((self.position[0]-self.radius) // 256)}.{int((self.position[1]-self.radius) // 256)}"
        topright = f"{int((self.position[0]+self.radius) // 256)}.{int((self.position[1]-self.radius) // 256)}"
        bottomleft = f"{int((self.position[0]-self.radius) // 256)}.{int((self.position[1]+self.radius) // 256)}"
        bottomright = f"{int((self.position[0]+self.radius) // 256)}.{int((self.position[1]+self.radius) // 256)}"
        for pos in [topleft, topright, bottomleft, bottomright]:
            if pos not in self.current_chunks:
                self.current_chunks.append(pos)

    def get_event(self, event):
        if event.type == pg.JOYAXISMOTION:
            if event.axis in (0, 1):  # Left stick
                self.leftstick[event.axis] = event.value
            if event.axis in (2, 3):  # Right stick
                self.rightstick[event.axis-2] = event.value
            if event.axis == 4:  # Left trigger
                self.lefttrigger = event.value
            if event.axis == 5:  # Right trigger
                self.righttrigger = event.value

    def meleeattack(self):
        if self.meleeattack_flag:
            self.status = 'meleeattack'
            self.anim_status = 'meleeattack'
            self.cooldown = 0
            self.sprite_index = 0
            self.meleeattack_flag = False

    def update(self):
        """ Check the controls and trigger actions """
        """ Priority : idle < move < shoot < reload < meleeattack """
        self.update_current_chunks()

        if self.leftstick.length_squared() > .3**2:
            # Left stick = movement + orientation
            self.set_status('move')
            self.move_flag = True

            self.projection_x.update(self.position, (self.leftstick.x * self.speed, 0))
            self.projection_y.update(self.position, (0, self.leftstick.y * self.speed))

            angle = pg.math.Vector2(0, 0)
            self.orientation = -angle.angle_to(self.leftstick)
        else:
            self.set_status('idle')
            self.move_flag = False

        if self.rightstick.length_squared() > .7**2:
            # Right stick = orientation
            angle = pg.math.Vector2(0, 0)
            self.orientation = -angle.angle_to(self.rightstick)

        if self.righttrigger > .9 and self.shoot_flag:
            self.set_status('shoot')

        if self.lefttrigger > .9 and self.meleeattack_flag:
            self.meleeattack()

        self.update_sprite()

    def get_damages(self, damages):
        self.health[0] -= damages
        if self.health[0] < 0:
            self.health[0] = 0

    def set_status(self, new_status):
        self.status = new_status
        if new_status in ['idle', 'move', 'shoot', 'reload', 'meleeattack']:
            self.anim_status = new_status

    def is_moving(self):
        return self.move_flag
