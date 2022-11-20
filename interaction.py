from settings import *
from map import world_map
from ray_casting import mapping
import math
from numba import njit
import pygame

@njit(fastmath=True, cache=True)
def ray_casting_npc_player(npc_x, npc_y, blocked_doors, world_map, player_pos):
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    delta_x, delta_y = ox - npc_x, oy - npc_y
    cur_angle = math.atan2(delta_y, delta_x)
    cur_angle += math.pi

    sin_a = math.sin(cur_angle)
    sin_a = sin_a if sin_a else 0.000001
    cos_a = math.cos(cur_angle)
    cos_a = cos_a if cos_a else 0.000001

    # verticals
    x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
    for i in range(0, int(abs(delta_x)) // TILE):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = mapping(x + dx, yv)
        if tile_v in world_map or tile_v in blocked_doors:
            return False
        x += dx * TILE

    # horizontals
    y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
    for i in range(0, int(abs(delta_y)) // TILE):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = mapping(xh, y + dy)
        if tile_h in world_map or tile_h in blocked_doors:
            return False
        y += dy * TILE
    return True


class Interaction:
    def __init__(self, player, sprites, drawing):
        self.player = player
        self.sprites = sprites
        self.drawing = drawing
        #cool down of davil
        self.cool_down_time_d = 200
        self.cool_down_d = False
        self.cool_down_time_d1 = 900
        self.cool_down_d1 = False
        #cool down of flame
        self.cool_down_time_f = 100
        self.cool_down_f = False
        #cool down of solidor
        self.cool_down_time_s = 500
        self.cool_down_s = False
        #sound
        self.pain_sound = pygame.mixer.Sound('sound/pain.wav')
        self.damage = pygame.mixer.Sound('sound/damage.ogg')


    def interaction_objects(self, chek_music):
        if self.player.shot and self.drawing.shot_animation_trigger:
            for obj in sorted(self.sprites.list_of_objects, key=lambda obj: obj.distance_to_sprite):
                if obj.is_on_fire[1]:
                    if obj.is_dead != 'immortal' and not obj.is_dead:
                        if ray_casting_npc_player(obj.x, obj.y,
                                                  self.sprites.blocked_doors,
                                                  world_map, self.player.pos):
                            if obj.flag == 'npc' and chek_music == 1:
                                self.pain_sound.play()
                            obj.is_dead = True
                            obj.blocked = None
                            self.drawing.shot_animation_trigger = False
                    if obj.flag in {'door_h', 'door_v'} and obj.distance_to_sprite < TILE:
                        obj.door_open_trigger = True
                        obj.blocked = None
                    break

    def npc_action(self):
        for obj in self.sprites.list_of_objects:
            if obj.flag == 'npc' and not obj.is_dead:
                if ray_casting_npc_player(obj.x, obj.y,
                                          self.sprites.blocked_doors,
                                          world_map, self.player.pos):
                    obj.npc_action_trigger = True
                    self.npc_move(obj)
                else:
                    obj.npc_action_trigger = False

    def npc_move(self, obj):
        if abs(obj.distance_to_sprite) > TILE:
            dx = obj.x - self.player.pos[0]
            dy = obj.y - self.player.pos[1]
            obj.x = obj.x + 1 if dx < 0 else obj.x - 1
            obj.y = obj.y + 1 if dy < 0 else obj.y - 1

    def clear_world(self):
        delete_object = self.sprites.list_of_objects[:]
        [self.sprites.list_of_objects.remove(obj) for obj in delete_object if obj.delete]

    def play_music(self, music):
        if music == 1:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            pygame.mixer.music.load('sound/theme.mp3')
            pygame.mixer.music.play(10)

    def chek_win(self, chek_music):
        if not len([obj for obj in self.sprites.list_of_objects if obj.flag == 'npc' and not obj.is_dead]):
            if chek_music == 1:
                pygame.mixer.music.stop()
                pygame.mixer.music.load('sound/win.mp3')
                pygame.mixer.music.play()
            pygame.mouse.set_visible(True)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            if self.drawing.win():
                return 1

    def chek_lose(self,chek_music):
        if self.player.health <= 0:
            if chek_music == 1:
                pygame.mixer.music.stop()
                pygame.mixer.music.load('sound/win.mp3')
                pygame.mixer.music.play()
            pygame.mouse.set_visible(True)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            if self.drawing.lose():
                return 1

    def npc_damage(self, chek_music):
        for obj in sorted(self.sprites.list_of_objects, key=lambda obj: obj.distance_to_sprite):
            if not obj.is_dead or obj.is_dead == 'immortal':
                if ray_casting_npc_player(obj.x, obj.y,
                                        self.sprites.blocked_doors,
                                            world_map, self.player.pos):
                    if obj.teg == 'devil0' and int(abs(math.sqrt(((obj.x - self.player.x)**2)+((obj.y - self.player.y)**2)))) < 100:
                        if self.cool_down_d:
                            self.cool_down_time_d -= 5
                            if self.cool_down_time_d == 0:
                                self.cool_down_d = False
                        else:
                            self.player.health -= 5
                            if chek_music == 1:
                                self.damage.play()
                            self.cool_down_time_d = 200
                            self.cool_down_d = True
                    if obj.teg == 'flame' and int(abs(math.sqrt(((obj.x - self.player.x)**2)+((obj.y - self.player.y)**2)))) < 90:
                        if self.cool_down_f:
                            self.cool_down_time_f -= 5
                            if self.cool_down_time_f == 0:
                                self.cool_down_f = False
                        else:
                            self.player.health -= 2
                            if chek_music == 1:
                                self.damage.play()
                            self.cool_down_time_f = 100
                            self.cool_down_f = True
                    if (obj.teg == 'solider0' or obj.teg == 'solider1') and int(abs(math.sqrt(((obj.x - self.player.x)**2)+((obj.y - self.player.y)**2)))) < 700:
                        if self.cool_down_s:
                            self.cool_down_time_s -= 5
                            if self.cool_down_time_s == 0:
                                self.cool_down_s = False
                        else:
                            self.player.health -= 10
                            if chek_music == 1:
                                self.damage.play()
                            self.cool_down_time_s = 700
                            self.cool_down_s = True
                    if obj.teg == 'devil1' and int(abs(math.sqrt(((obj.x - self.player.x)**2)+((obj.y - self.player.y)**2)))) < 100:
                        if self.cool_down_d1:
                            self.cool_down_time_d1 -= 5
                            if self.cool_down_time_d1 == 0:
                                self.cool_down_d1 = False
                        else:
                            self.player.health -= 15
                            if chek_music == 1:
                                self.damage.play()
                            self.cool_down_time_d1 = 900
                            self.cool_down_d1 = True