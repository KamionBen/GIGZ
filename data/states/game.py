import pygame as pg
from random import choice
from .. import tools, prepare, level, player, survivor, zombies


class Game(tools.State):
    def __init__(self):
        tools.State.__init__(self)

        self.next = 'pause'
        self.previous = 'menu'

        self.ui_surface = pg.Surface(prepare.RESOLUTION, pg.SRCALPHA, 32)
        self.debug_surface = None
        self.debug = True

        self.survivors = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.zombie_left = [0, 0]  # Zombie left, zombie total

        self.camera = pg.math.Vector2(0, 0)
        self.loaded_chunks = []

        self.font = pg.font.Font(None, 26)

    def _update_ui(self):
        """ Show all the non-diegetic informations """
        self.ui_surface.fill((0, 0, 0, 0))
        for i, g_player in enumerate(tools.State.players):
            big_font = prepare.FONTS['Biometric Joe'][58]
            medium_font = prepare.FONTS['Courier New Bold'][26]
            name_txt = big_font.render(g_player.name, True, g_player.color)
            self.ui_surface.blit(name_txt, (50, 800))
            infos = [g_player.survivor.status, str(g_player.survivor.health), str(g_player.survivor.weapon)]
            for n, info in enumerate(infos):
                txt = medium_font.render(info, True, 'white')
                self.ui_surface.blit(txt, (50, 850 + n * 25))

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

    def _check_level_limits(self, c_survivor):
        """ Should check coordinates and return a correct value """
        # TODO :
        if c_survivor.position[0] < c_survivor.radius:
            c_survivor.position[0] = c_survivor.radius
        if c_survivor.position[1] < c_survivor.radius:
            c_survivor.position[1] = c_survivor.radius

        if c_survivor.position[0] > self.level.width - c_survivor.radius:
            c_survivor.position[0] = self.level.width - c_survivor.radius
        if c_survivor.position[1] > self.level.height - c_survivor.radius:
            c_survivor.position[1] = self.level.height - c_survivor.radius

    def _check_wall_collision(self, rect, allwalls=True):
        # TODO : Don't check all the walls
        collision = False
        for wall in self.level.walls:
            if wall.rect.colliderect(rect):
                collision = True
                break
        return collision

    def _check_zombie_collision(self, rect, ignore=()):
        collision = False
        for zombie in self.zombies:
            if zombie not in ignore:
                z_pos_x, z_pos_y = zombie.position[0] - zombie.radius, zombie.position[1] - zombie.radius
                z_size = zombie.radius * 2
                z_rect = pg.Rect(z_pos_x, z_pos_y, z_size, z_size)
                if z_rect.colliderect(rect):
                    collision = True
                    break
        return collision

    def _move_entity(self, vector, entity):
        """ Check for collision and move the survivor (or the zombie) accordingly """
        posx, posy = entity.position[0] - entity.radius, entity.position[1] - entity.radius
        size = entity.radius * 2
        projection_x = pg.rect.Rect(posx + vector[0] * entity.speed, posy, size, size)
        projection_y = pg.rect.Rect(posx, posy + vector[1] * entity.speed, size, size)

        if self._check_wall_collision(projection_x) or self._check_zombie_collision(projection_x, ignore=[entity]):
            vector.x = 0
        if self._check_wall_collision(projection_y) or self._check_zombie_collision(projection_y, ignore=[entity]):
            vector.y = 0

        # TODO : Allow the survivor to move around walls

        entity.move(vector)
        self._check_level_limits(entity)

    def spawn_zombies(self):
        if tools.State.level.zombie_number not in [None, 'Unlimited']:
            while self.zombie_left[1] < self.level.zombie_number:
                # TODO : Achtung ! Infinite loop if too much zombies and not enough spawns
                spawn = choice(self.level.zombies_spawns)
                rect = pg.Rect(spawn[0], spawn[1], 70, 70)
                if self._check_wall_collision(rect) is False and self._check_zombie_collision(rect) is False:
                    self.zombies.add(zombies.ZombieControl(spawn))
                    self.zombie_left[0] += 1
                    self.zombie_left[1] += 1

    def update(self):
        # Check for pause
        for u_player in tools.State.players:
            if u_player.buttons['pause']:
                self.set_pause()
                break

        # Spawn zombies in not already done
        self.spawn_zombies()
        if len(self.survivors) < len(tools.State.players):
            for play in tools.State.players:
                self.survivors.add(play.survivor)

        # Prepare screen and tick
        prepare.CLOCK.tick(prepare.FPS)
        prepare.SCREEN.fill('black')

        # Check survivors projections for colllisions
        for surv in self.survivors:
            if surv.is_moving():
                projection = pg.Vector2(surv.projection_x.rect.centerx,
                                        surv.projection_y.rect.centery)
                for chunk in surv.current_chunks:
                    for wall in tools.State.level.chunks[chunk].walls:
                        if pg.sprite.collide_mask(wall, surv.projection_x):
                            projection.x = surv.projection_x.position.x
                        if pg.sprite.collide_mask(wall, surv.projection_y):
                            projection.y = surv.projection_y.position.y
                surv.set_position(projection)

        self.survivors.update()
        self.control_zombies()
        self.zombies.update()
        self._update_camera()
        self._load_chunks()
        self._update_ui()
        self.draw(prepare.SCREEN)

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

        # TODO : Put this elsewhere
        for zombie in self.zombies:
            if zombie.current_chunk in self.loaded_chunks:
                zombie.activate()
                zombie.on_screen = True
            else:
                zombie.on_screen = False

    def _update_camera(self):
        new_cam = pg.math.Vector2(0, 0)
        for surv in self.survivors:
            new_cam += surv.position
        new_cam /= len(self.survivors)
        self.camera = new_cam

    def _camera_offset(self):
        """ Return a value that need to be added to the sprite position """
        center = pg.Vector2(prepare.RESOLUTION[0] / 2, prepare.RESOLUTION[1] / 2)
        return -self.camera+center

    def draw(self, screen):
        # screen.fill('black')

        # CHUNKS
        for key in self.loaded_chunks:
            chunk = tools.State.level.chunks[key]
            position = chunk.position + self._camera_offset()
            screen.blit(chunk.image, position)

        # SURVIVORS
        for i, surv in enumerate(self.survivors):
            position = pg.math.Vector2(surv.position) + self._camera_offset()

            pg.draw.circle(screen, (0, 0, 0, 128), position, surv.radius)  # Shadow
            # pg.draw.circle(screen, self.players[i].color, position, surv.radius + 10, 10)  # Player color
            if surv.status == 'meleeattack':
                for zombie in self.zombies:
                    if zombie.on_screen:
                        dist = pg.Vector2(surv.position[0]-zombie.position[0], surv.position[1]-zombie.position[1])
                        direction = pg.Vector2(2,0).rotate(surv.orientation)
                        if dist.length() < 110:
                            zombie.kickback(direction, 30)
            screen.blit(surv.image, position - pg.Vector2(70, 70))

        # ZOMBIES
        for zombie in self.zombies:
            position = pg.Vector2(zombie.position) + self._camera_offset()
            pg.draw.circle(screen, (0, 0, 0, 128), position, zombie.radius)  # Shadow
            screen.blit(zombie.image, position - pg.Vector2(70, 70))

        # USER INTERFACE
        screen.blit(self.ui_surface, (0, 0))

        # DEBUG
        if self.debug:
            self._update_debug_surf()
            screen.blit(self.debug_surface, (0, 0))

    def _update_debug_surf(self):
        self.debug_surface = pg.Surface(prepare.RESOLUTION, pg.SRCALPHA, 32)

        color = 'white'

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
            btxt = self.font.render(txt, True, color)
            self.debug_surface.blit(btxt, (20, 20 + i * 30))

        # Center cross
        res = prepare.RESOLUTION  # Sugar
        pg.draw.line(self.debug_surface, 'black', (res[0]/2 - 10, res[1]/2), (res[0]/2 + 10, res[1]/2), 2)
        pg.draw.line(self.debug_surface, 'black', (res[0]/2, res[1]/2 - 10), (res[0]/2, res[1]/2 + 10), 2)

    # Event functions
    def get_event(self, event):
        """ Get the event and dispatch it to the correct function """
        if event.type in [pg.JOYAXISMOTION, pg.JOYBUTTONDOWN, pg.JOYBUTTONUP]:
            player = self.players[event.joy]
            player.get_event(event)
            player.survivor.get_event(event)

    def set_pause(self):
        """ Pause game, switch to pause state """
        self.done = True

    # Zombie control functions
    def control_zombies(self):
        # TODO : Put in the zombie control class
        for zombie in self.zombies:
            if zombie.active and zombie.status != 'kickback':
                if zombie.target is None:
                    self._seek_target(zombie)
                direction = pg.Vector2(zombie.speed, 0).rotate(-zombie.orientation)
                attack = False
                if zombie.status != 'attack':
                    for surv in self.survivors:
                        # Zombie rect
                        posx, posy = zombie.position[0] - zombie.radius, zombie.position[1] - zombie.radius
                        size = zombie.radius * 2
                        projection = pg.rect.Rect(posx + direction[0], posy + direction[1], size, size)
                        # Surv rect
                        s_posx, s_posy = surv.position[0] - surv.radius, surv.position[1] - surv.radius
                        s_size = surv.radius * 2
                        surv_rect = pg.rect.Rect(s_posx, s_posy, s_size, s_size)
                        if projection.colliderect(surv_rect):
                            attack = True
                            if self.level.difficulty != 'Godmode':
                                surv.get_damages(zombie.force)
                    if attack:
                        zombie.attack()

                    else:
                        self._move_entity(direction, zombie)

    def _seek_target(self, zombie):
        """ The zombie is looking for someone to bite ! """
        # TODO : Put in the zombiecontrol class
        target = None
        for surv in self.survivors:
            if target is None:
                target = surv
            else:
                current_distance = pg.Vector2(target.position).distance_to(zombie.position)
                new_distance = pg.Vector2(surv.position).distance_to(zombie.position)
                if new_distance < current_distance:
                    target = surv
        zombie.target = target

    # Startup
    def start_game(self):
        """ Initiate the players and zombies """
        # ZOMBIES
        if tools.State.level.zombie_number not in [None, 'Unlimited']:
            while len(self.zombies) < self.level.zombie_number:
                # TODO : Achtung ! Infinite loop if too much zombies and not enough spawns
                spawn = choice(self.level.zombies_spawns)
                rect = pg.Rect(spawn[0], spawn[1], 70, 70)
                if self._check_wall_collision(rect) is False and self._check_zombie_collision(rect) is False:
                    self.zombies.add(zombies.ZombieControl(spawn))

        # SURVIVORS
        for i, i_player in enumerate(tools.State.players):
            new_survivor = survivor.SurvivorControl(self.level.survivors_spawns[i])
            self.survivors.add(new_survivor)
            i_player.set_survivor(new_survivor)

        self._update_camera()
