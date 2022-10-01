import pygame as pg
from random import choice, randrange
from .. import tools, prepare, level, player, survivor, zombies


class Game(tools.State):
    def __init__(self):
        tools.State.__init__(self)

        self.next = 'pause'
        self.previous = 'menu'

        self.survivors = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.zombie_left = [0, 0]  # Zombie left, zombie total

        self.camera = pg.math.Vector2(0, 0)
        self.loaded_chunks = []

        self.font = pg.font.Font(None, 26)
        self.big_font = prepare.FONTS['Biometric Joe'][58]
        self.medium_font = prepare.FONTS['Courier New Bold'][26]

        self.debug = True
        self.game_started = False

        self.effect_list = []

    def startup(self):
        if self.game_started is False:
            self.start_game()

    def _in_level_coord(self, coord, span):
        """ Return the coordinates corrected so they don't exit the level limits """
        # Left and top limits
        if coord[0] < span:
            coord[0] = span
        if coord[1] < span:
            coord[1] = span

        # Right and bottom limits
        if coord[0] > tools.State.level.width - span:
            coord[0] = tools.State.level.width - span
        if coord[1] > tools.State.level.height - span:
            coord[1] = tools.State.level.height - span

        return coord

    def spawn_zombies(self):
        if tools.State.level.zombie_number not in [None, 'Unlimited']:
            while self.zombie_left[1] < self.level.zombie_number:
                # TODO : Check for collision
                spawn = choice(self.level.zombies_spawns)
                rect = pg.Rect(spawn[0]+35, spawn[1]+35, 70, 70)
                if self.check_collision(rect, 'all') is False:
                    self.zombies.add(zombies.ZombieControl(spawn))
                    self.zombie_left[0] += 1
                    self.zombie_left[1] += 1

    def check_collision(self, item, chunks, ignore=()):
        collision = False
        if chunks == 'all':
            chunks = tools.State.level.chunks
        for chunk in chunks:
            if 'walls' not in ignore:
                for wall in tools.State.level.chunks[chunk].walls:
                    if pg.sprite.collide_mask(wall, item):
                        collision = True
                        break
            if 'zombies' not in ignore:
                for zombie in self.zombies:
                    if chunk in zombie.current_chunks:
                        if pg.sprite.collide_mask(zombie.projection, item):
                            collision = True
                            break
        return collision

    def update(self):
        # Check for pause
        for u_player in tools.State.players:
            if u_player.buttons['pause']:
                self.set_pause()
                break

        # Prepare screen and tick
        prepare.CLOCK.tick(prepare.FPS)
        # Check survivors projections for colllisions
        for surv in self.survivors:
            if surv.is_moving():
                projection = pg.Vector2(surv.projection_x.rect.centerx,
                                        surv.projection_y.rect.centery)
                projection = self._in_level_coord(projection, surv.radius)
                if self.check_collision(surv.projection_x, surv.current_chunks):
                    projection.x = surv.projection_x.position.x
                if self.check_collision(surv.projection_y, surv.current_chunks):
                    projection.y = surv.projection_y.position.y

                surv.set_position(projection)

        for zombie in self.zombies:
            if zombie.is_dead():
                self.zombies.remove(zombie)
            else:
                on_screen = False
                for z_chunk in zombie.current_chunks:
                    if z_chunk in self.loaded_chunks:
                        on_screen = True
                zombie.on_screen = on_screen
                if on_screen and zombie.active is False:
                    zombie.activate()
                if zombie.active:
                    if zombie.target is None:
                        zombie.seek_target()

        self.survivors.update()
        self.zombies.update()
        self._update_camera()
        self._load_chunks()

        while len(self.trigger_list) > 0:
            trigger = self.trigger_list.pop(0)
            if trigger.genre == 'shoot':
                t_survivor = trigger['survivor']
                start = survivor.weapon_offset[t_survivor.weapon_img].rotate(-t_survivor.orientation)
                start += t_survivor.position
                end = pg.Vector2(2000, survivor.weapon_offset[t_survivor.weapon_img][1]).rotate(-t_survivor.orientation)
                end += t_survivor.position
                _, _, target = self._get_sightline(start, end)
                if type(target) is zombies.ZombieControl:
                    target.take_damages(t_survivor.weapon.damages)

                rand = randrange(1,6)
                b_start = start + (end-start) * (rand/10)
                b_end = start + (end-start) * ((rand/10) + .05)
                self.effect_list.append(['bullet', b_start, b_end])

    def _load_chunks(self):
        """ Recreate the chunk list from scratch """
        self.loaded_chunks = []
        center_chunk_coord = int(self.camera[0] // (32 * 8)), int(self.camera[1] // (32 * 8))
        surroundings = []
        # TODO : Get rid of the first loop
        for y in range(-3, 3):
            for x in range(-4, 5):
                surroundings.append((x, y))

        for surround in surroundings:
            coord = pg.math.Vector2(surround) + pg.Vector2(center_chunk_coord)
            key = f"{int(coord[0])}.{int(coord[1])}"
            if key in self.level.chunks.keys():
                self.loaded_chunks.append(key)

        """ display only player chunks """
        """
        self.loaded_chunks = []
        for player in tools.State.players:
            for key in player.survivor.current_chunks:
                self.loaded_chunks.append(key)
        """
    def _update_camera(self):
        new_cam = pg.math.Vector2(0, 0)
        for surv in self.survivors:
            new_cam += surv.position
        new_cam /= len(self.survivors)
        self.camera = new_cam

    def _camera_offset(self):
        """ Return a value that need to be added to the sprite position """
        center = pg.Vector2(1920 / 2, 1080 / 2)
        return -self.camera+center

    def draw(self, screen):
        screen.fill('black')
        self._draw_level(screen)
        self._draw_zombies(screen)
        self._draw_survivors(screen)
        self._draw_effects(screen)
        self._draw_interface(screen)
        if self.debug:
            self._draw_debug(screen)

    def _draw_effects(self, screen):
        while len(self.effect_list) > 0:
            effect = self.effect_list.pop(0)
            if effect[0] == 'bullet':
                pg.draw.line(screen, 'black', effect[1] + self._camera_offset(), effect[2] + self._camera_offset())
            if effect[0] == 'round':
                pg.draw.circle(screen, 'orange', effect[1] + self._camera_offset(), 5)

    def _draw_level(self, screen):
        for key in self.loaded_chunks:
            chunk = tools.State.level.chunks[key]
            position = chunk.position + self._camera_offset()
            screen.blit(chunk.image, position)

    def _draw_survivors(self, screen):
        for i, surv in enumerate(self.survivors):
            position = pg.math.Vector2(surv.position) + self._camera_offset()

            pg.draw.circle(screen, (0, 0, 0, 128), position, surv.radius)  # Shadow
            # pg.draw.circle(screen, self.players[i].color, position, surv.radius + 10, 10)  # Player color
            # Draw Laser pointer
            start = survivor.weapon_offset[surv.weapon_img].rotate(-surv.orientation) + surv.position
            end = pg.Vector2(2000, survivor.weapon_offset[surv.weapon_img][1]).rotate(-surv.orientation) + surv.position

            n_start, n_end, _ = self._get_sightline(start, end)
            pg.draw.line(screen, 'red', n_start + self._camera_offset(), n_end + self._camera_offset())
            pg.draw.circle(screen, 'red', n_end + self._camera_offset(), 2)

            screen.blit(surv.image, position - pg.Vector2(70, 70))

    def _get_sightline(self, start_pos, end_pos, allied=False):
        """ Return the sightline used for laser pointer and tracer bullets """
        on_sight = []
        for zombie in self.zombies:
            clipline = zombie.hitbox.rect.clipline(start_pos, end_pos)
            if clipline:
                clip_s, clip_e = clipline
                distance_sq = start_pos.distance_squared_to(clip_s)
                on_sight.append((zombie, distance_sq, clip_s))
        for wall in tools.State.level.walls:
            clipline = wall.rect.clipline(start_pos, end_pos)
            if clipline:
                clip_s, clip_e = clipline
                distance_sq = start_pos.distance_squared_to(clip_s)
                on_sight.append((wall, distance_sq, clip_s))

        if allied:
            for surv in self.survivors:
                clipline = surv.rect.clipline(start_pos, end_pos)
                if clipline:
                    clip_s, _ = clipline
                    distance_sq = start_pos.distance_squared_to(clip_s)
                    on_sight.append((surv, distance_sq, clip_s))

        on_sight.sort(key=lambda x: x[1])
        if len(on_sight) > 0:
            item = on_sight[0][0]
            impact = on_sight[0][2]
        else:
            item = None
            impact = end_pos

        return start_pos, impact, item

    def _draw_zombies(self, screen):
        for zombie in self.zombies:
            position = pg.Vector2(zombie.position) + self._camera_offset()
            pg.draw.circle(screen, (0, 0, 0, 128), position, zombie.radius)  # Shadow
            screen.blit(zombie.image, position - pg.Vector2(70, 70))

    def _draw_interface(self, screen):
        for i, g_player in enumerate(tools.State.players):
            name_txt = self.big_font.render(g_player.name, True, g_player.color)
            screen.blit(name_txt, (50, 800))
            infos = [g_player.survivor.status, str(g_player.survivor.health), str(g_player.survivor.weapon)]
            for n, info in enumerate(infos):
                txt = self.medium_font.render(info, True, 'white')
                screen.blit(txt, (50, 850 + n * 25))

    def _draw_debug(self, screen):
        txt_list = [f"Level name : {self.level.name}",
                    f"Difficulty : {self.level.difficulty}",
                    f"Zombie number : {self.level.zombie_number}",
                    f"Friendly fire : {self.level.friendly_fire}",
                    f"Players : {len(self.players)}",
                    f"Camera : {self.camera}",
                    f"FPS : {int(prepare.CLOCK.get_fps())}",
                    f"Loaded chunks : {len(self.loaded_chunks)}",
                    f"Zombies left : {len(self.zombies)}",
                    f"Health : {[s.health for s in self.survivors]}",
                    f"Player chunks : {[s.current_chunks for s in self.survivors]}"]

        for i, txt in enumerate(txt_list):
            btxt = self.font.render(txt, True, 'white')
            screen.blit(btxt, (20, 20 + i * 30))

        # Center cross
        res = 1920, 1080  # Sugar
        pg.draw.line(screen, 'black', (res[0] / 2 - 10, res[1] / 2), (res[0] / 2 + 10, res[1] / 2), 2)
        pg.draw.line(screen, 'black', (res[0] / 2, res[1] / 2 - 10), (res[0] / 2, res[1] / 2 + 10), 2)


    # Event functions
    def get_event(self, event):
        """ Get the event and dispatch it to the correct function """
        if event.type in [pg.JOYAXISMOTION, pg.JOYBUTTONDOWN, pg.JOYBUTTONUP]:
            e_player = self.players[event.joy]
            e_player.get_event(event)
            e_player.survivor.get_event(event)

    def set_pause(self):
        """ Pause game, switch to pause state """
        self.done = True

    def start_game(self):
        """ Initiate the players and zombies """
        # ZOMBIES
        if tools.State.level.zombie_number not in [None, 'Unlimited']:
            while len(self.zombies) < self.level.zombie_number:
                # TODO : Achtung ! Infinite loop if too much zombies and not enough spawns
                spawn = choice(self.level.zombies_spawns)
                self.zombies.add(zombies.ZombieControl(spawn))

        # SURVIVORS
        for i, i_player in enumerate(tools.State.players):
            new_survivor = survivor.SurvivorControl(self.level.survivors_spawns[i])
            self.survivors.add(new_survivor)
            i_player.set_survivor(new_survivor)

        self._update_camera()
        self.game_started = True
