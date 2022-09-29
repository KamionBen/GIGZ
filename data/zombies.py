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

        self.position = pg.Vector2(position)

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

        self.kickback_flag = False
        self.kickback_force = 0
        self.kickback_direction = (0, 0)

        self.current_chunks = []
        self._update_current_chunks()
        self.update_sprite()

        self.projection = tools.Projection(self.position, self.radius, (0, 0))

    def update(self):
        if self.active:
            if self.status == 'attack':
                self.cooldown += 1
                if self.cooldown >= self.attack_speed:
                    self.cooldown = 0
                    self.idle()
            if self.status == 'kickback':
                self.cooldown += 1
                if self.cooldown < self.kickback_force:
                    self.position += self.kickback_direction
                    self._update_current_chunks()
                else:
                    self.idle()
                    self.kickback_flag = False

            if self.target is not None:
                angle = self.position.angle_to(self.target.position-self.position)
                self.orientation = 315-angle
            if self.on_screen:
                pass
                #self.update_sprite()

    def kickback(self, direction, force):
        """ The zombie took some damages and move back for a while """
        self.kickback_flag = True
        self.status = 'kickback'
        self.anim_status = 'idle'
        self.kickback_direction = direction
        self.kickback_force = force
        self.cooldown = 0

    def _update_current_chunks(self):
        self.current_chunks = []
        x, y = self.position[0], self.position[1]
        r = self.radius * 2
        topleft = f"{int((x - r) // 256)}.{int((y - r) // 256)}"
        topright = f"{int((x + r) // 256)}.{int((y - r) // 256)}"
        bottomleft = f"{int((x - r) // 256)}.{int((y + r) // 256)}"
        bottomright = f"{int((x + r) // 256)}.{int((y + r) // 256)}"
        for pos in [topleft, topright, bottomleft, bottomright]:
            if pos not in self.current_chunks and pos in tools.State.level.chunks.keys():
                self.current_chunks.append(pos)

    def move(self, vector):
        self.position += vector
        self._update_current_chunks()
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
        self.seek_target()

    def set_target(self, targeted_survivor):
        self.target = targeted_survivor

    def seek_target(self):
        """ Find the closest survivor """
        target = None
        for player in tools.State.players:
            if target is None:
                target = player.survivor
            else:
                new_distance = self.position.distance_squared_to(player.survivor.position)
                current_distance = self.position.distance_squared_to(target.position)
                if new_distance < current_distance:
                    target = player.survivor
        self.set_target(target)



