import csv


class Weapon:
    def __init__(self, name, category, cadence, sprite, image_src, damages, shooting_speed, magazine, reload_speed,
                 gear_slots, distance):
        # Infos
        self.name = name  # Unique designation
        self.category = category  # Maybe useless
        self.cadence = cadence  # manual, semi, or automatic
        self.distance = distance  # True if the weapon can shoot

        # Graphics
        self.sprite = sprite  # Which survivor sprite to display in game
        self.image_src = image_src  # Weapon image in the menu

        # Stats
        self._base_damages = damages
        self.damages = self._base_damages
        self._base_speed = shooting_speed
        self.shooting_speed = self._base_speed

        # Magazine
        self._base_magazine = magazine
        self.magazine = [magazine, magazine]
        self._base_reload_speed = reload_speed
        self.reload_speed = reload_speed

        # Gear
        if gear_slots is None:
            self.gear_slots = []
            self.gear = []
        else:
            self.gear_slots = gear_slots
            self.gear = [None for x in self.gear_slots]
        self.effects = []

        # Display
        self.muzzle_offset = None  # Difference between the sprite center and the muzzle

    def __repr__(self):
        return self.name

    def set_gear(self, new_gear):
        for i, gear_slot in enumerate(self.gear_slots):
            if new_gear.slot == gear_slot:
                self.gear[i] = new_gear
        self._reset_effects()
        self._apply_effects()

    def _reset_effects(self):
        self.effects = []
        for gear in self.gear:
            if gear is None:
                self.effects.append(None)
            else:
                self.effects.append(gear.effect)

    def _apply_effects(self):
        # Reset
        # Stats
        self.damages = self._base_damages
        self.shooting_speed = self._base_speed

        # Magazine
        self.magazine = [self._base_magazine, self._base_magazine]
        self.reload_speed = self._base_reload_speed

        for effect in self.effects:
            if effect == 'big_magazine':
                self.magazine = [self._base_magazine * 2, self._base_magazine * 2]
            if effect == 'speedy_magazine':
                self.reload_speed = self._base_reload_speed // 2

    def unload(self):
        self.magazine[0] -= 1
        if self.magazine[0] < 0:
            self.magazine[0] = 0
            return False
        else:
            return True

    def reload(self):
        self.magazine[0] = self.magazine[1]


class Gear:
    def __init__(self, name, effect, slot):
        self.name = name
        self.effect = effect
        self.slot = slot


