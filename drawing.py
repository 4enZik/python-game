import pygame
from settings import *
from ray_casting import ray_casting
from map import mini_map
from collections import deque
from random import randrange
import sys

class Drawing:
    def __init__(self, sc, sc_map, player,clock):
        self.sc = sc
        self.sc_map = sc_map
        self.player = player
        self.clock = clock
        self.font = pygame.font.SysFont('Arial', 36, bold = True)
        self.font_win_lose = pygame.font.Font('font/font.ttf', 100)
        self.textures = {1: pygame.image.load('img/1.png').convert(),
                         2: pygame.image.load('img/2.png').convert(),
                         3: pygame.image.load('img/3.png').convert(),
                         4: pygame.image.load('img/4.png').convert(),
                         'S': pygame.image.load('img/sky.png').convert()
                        }
        #end
        self.end_trigger = True
        #win tap
        self.win_trigger = True
        #lose tap
        self.lose_trigger = True
        #pause
        self.pause_trigger = True
        #menu
        self.menu_trigger = True
        self.menu_picture = pygame.image.load('img/bg.jpg').convert()
        #weapone parameters
        self.weapon_base_sprite = pygame.image.load('sprites/weapons/shotgun/base/0.png').convert_alpha()
        self.weapon_shot_animation = deque([pygame.image.load(f'sprites/weapons/shotgun/shot/{i}.png').convert_alpha()
                                            for i in range(20)])
        self.weapon_rect = self.weapon_base_sprite.get_rect()
        self.weapon_pos = (HALF_WIDTH - self.weapon_rect.width // 2, HEIGHT - self.weapon_rect.height)
        self.shot_length = len(self.weapon_shot_animation)
        self.shot_length_count = 0
        self.shot_animation_speed = 3
        self.shot_animation_count = 0
        self.shot_animation_trigger = True
        self.shot_sound = pygame.mixer.Sound('sound/shotgun.wav')
        #sfx parameters
        self.sfx = deque([pygame.image.load(f'sprites/weapons/shotgun/sfx/{i}.png').convert_alpha() for i in range(9)])
        self.sfx_length_count = 0
        self.sfx_length = len(self.sfx)

    def background(self, angle):
        sky_offset = -10 * math.degrees(angle) % WIDTH
        self.sc.blit(self.textures['S'], (sky_offset, 0))
        self.sc.blit(self.textures['S'], (sky_offset - WIDTH, 0))
        self.sc.blit(self.textures['S'], (sky_offset + WIDTH, 0))
        pygame.draw.rect(self.sc, DARKGRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    def world(self, world_objects):
        for obj in sorted(world_objects, key=lambda n: n[0], reverse=True):
            if obj[0]:
                _, object, object_pos = obj
                self.sc.blit(object, object_pos)

    def fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.font.render(display_fps, 0, RED)
        self.sc.blit(render, FPS_POS)

    def mini_map(self, player):
        self.sc_map.fill(BLACK)
        map_x, map_y = player.x // MAP_SCALE, player.y // MAP_SCALE
        pygame.draw.line(self.sc_map, YELLOW, (map_x, map_y), (map_x + 12 * math.cos(player.angle),
                                                 map_y + 12 * math.sin(player.angle)))
        pygame.draw.circle(self.sc_map, RED, (int(map_x), int(map_y)), 5)
        for x, y in mini_map:
            pygame.draw.rect(self.sc_map, SANDY, (x, y, MAP_TILE, MAP_TILE))
        self.sc.blit(self.sc_map, MAP_POS)

    def player_weapon(self, shots, chek_music):
        if self.player.shot:
            if not self.shot_length_count:
                if chek_music == 1:
                    self.shot_sound.play()
            self.shot_projection = min(shots)[1] // 2
            self.bullet_sfx()
            shot_sprite = self.weapon_shot_animation[0]
            self.sc.blit(shot_sprite, self.weapon_pos)
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.weapon_shot_animation.rotate(-1)
                self.shot_animation_count = 0
                self.shot_length_count += 1
                self.shot_animation_trigger = False
            if self.shot_length_count == self.shot_length:
                self.player.shot = False
                self.shot_length_count = 0
                self.sfx_length_count = 0
                self.shot_animation_trigger = True
        else:
            self.sc.blit(self.weapon_base_sprite, self.weapon_pos)

    def player_health(self,player):
        health_font = pygame.font.Font('font/font.ttf', 40)
        render = health_font.render(str(player.health), 1, pygame.Color('red'))
        self.sc.blit(render,HEALTH_POS)

    def bullet_sfx(self):
        if self.sfx_length_count < self.sfx_length:
            sfx = pygame.transform.scale(self.sfx[0], (self.shot_projection, self.shot_projection))
            sfx_rect = sfx.get_rect()
            self.sc.blit(sfx, (HALF_WIDTH - sfx_rect.w // 2, HALF_HEIGHT - sfx_rect.h //2))
            self.sfx_length_count += 1
            self.sfx.rotate(-1)

    def win(self):
        self.win_trigger = True
        x = 0
        #YOU WIN
        rect = pygame.Rect(0,0,750,150)
        rect.center = HALF_WIDTH, HALF_HEIGHT - 220

        #BUTTONS
        button_font = pygame.font.Font('font/font.ttf', 72)
        next_lvl = button_font.render('NEXT LVL', 1, pygame.Color('lightgray'))
        button_next_lvl = pygame.Rect(0, 0, 400, 150)
        button_next_lvl.center = HALF_WIDTH - 300, HALF_HEIGHT
        exit = button_font.render('EXIT', 1, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 400, 150)
        button_exit.center = HALF_WIDTH - 300, HALF_HEIGHT + 200

        while self.win_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.sc.blit(self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            render = self.font_win_lose.render('YOU WIN!!!', 1, (randrange(40, 120), 0, 0))
            pygame.draw.rect(self.sc, BLACK, rect, border_radius=40)
            self.sc.blit(render, (rect.centerx - 300, rect.centery - 100))

            pygame.draw.rect(self.sc, BLACK, button_next_lvl, border_radius=25, width=10)
            self.sc.blit(next_lvl, (button_next_lvl.centerx - 185, button_next_lvl.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25, width=10)
            self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25)
                self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))
                if mouse_click[0]:
                    self.win_trigger = False
                    pygame.quit()
                    sys.exit()


            elif button_next_lvl.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_next_lvl, border_radius=25)
                self.sc.blit(next_lvl, (button_next_lvl.centerx - 185, button_next_lvl.centery - 70))
                if mouse_click[0]:
                    self.win_trigger = False
                    return 1
            pygame.display.flip()
            self.clock.tick(20)

    def lose(self):
        self.lose_trigger = True
        x = 0

        #YOU LOSE
        rect = pygame.Rect(0, 0, 750, 150)
        rect.center = HALF_WIDTH, HALF_HEIGHT - 220

        # BUTTONS
        button_font = pygame.font.Font('font/font.ttf', 72)
        restart = button_font.render('RESTART', 1, pygame.Color('lightgray'))
        button_restart = pygame.Rect(0, 0, 400, 150)
        button_restart.center = HALF_WIDTH - 300, HALF_HEIGHT
        exit = button_font.render('EXIT', 1, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 400, 150)
        button_exit.center = HALF_WIDTH - 300, HALF_HEIGHT + 200

        while self.lose_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.sc.blit(self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            render = self.font_win_lose.render('YOU LOSE!!!', 1, (randrange(40, 120), 0, 0))
            pygame.draw.rect(self.sc, BLACK, rect, border_radius=40)
            self.sc.blit(render, (rect.centerx - 310, rect.centery - 100))

            pygame.draw.rect(self.sc, BLACK, button_restart, border_radius=25, width=10)
            self.sc.blit(restart, (button_restart.centerx - 185, button_restart.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25, width=10)
            self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25)
                self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))
                if mouse_click[0]:
                    self.lose_trigger = False
                    pygame.quit()
                    sys.exit()

            elif button_restart.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_restart, border_radius=25)
                self.sc.blit(restart, (button_restart.centerx - 185, button_restart.centery - 70))
                if mouse_click[0]:
                    self.lose_trigger = False
                    return 1

            pygame.display.flip()
            self.clock.tick(20)

    def menu(self):
        self.menu_trigger = True
        x = 0
        button_font = pygame.font.Font('font/font.ttf', 72)
        label_font = pygame.font.Font('font/font1.otf', 400)
        start = button_font.render('START', 1, pygame.Color('lightgray'))
        button_start = pygame.Rect(0, 0, 400, 150)
        button_start.center = HALF_WIDTH, HALF_HEIGHT
        exit = button_font.render('EXIT', 1, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 400, 150)
        button_exit.center = HALF_WIDTH, HALF_HEIGHT + 200

        button_sound_font = pygame.font.Font('font/font.ttf', 16)
        sound_on = button_sound_font.render('ON', 1, pygame.Color('lightgray'))
        button_sound_on = pygame.Rect(0, 0, 70, 70)
        button_sound_on.center = HALF_WIDTH + 430, HALF_HEIGHT - 120

        sound_off = button_sound_font.render('OFF', 1, pygame.Color('lightgray'))
        button_sound_off = pygame.Rect(0, 0, 70, 70)
        button_sound_off.center = HALF_WIDTH + 510, HALF_HEIGHT - 120

        while self.menu_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.sc.blit(self.menu_picture, (0,0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            pygame.draw.rect(self.sc, BLACK, button_start, border_radius=25, width=10)
            self.sc.blit(start, (button_start.centerx - 130, button_start.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25, width=10)
            self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_sound_on, border_radius = 25, width = 5)
            self.sc.blit(sound_on,(button_sound_on.centerx- 12, button_sound_on.centery- 15))

            pygame.draw.rect(self.sc, BLACK, button_sound_off, border_radius=25, width=5)
            self.sc.blit(sound_off, (button_sound_off.centerx- 15, button_sound_off.centery- 15))

            color = randrange(40)
            label = label_font.render('DOOMPy', 1, (color, color, color))
            self.sc.blit(label, (15, -30))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if button_start.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_start, border_radius=25)
                self.sc.blit(start, (button_start.centerx - 130, button_start.centery - 70))
                if mouse_click[0]:
                    self.menu_trigger = False

            elif button_sound_on.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_sound_on, border_radius=25)
                self.sc.blit(sound_on, (button_sound_on.centerx - 12, button_sound_on.centery - 15))
                if mouse_click[0]:
                    return 1

            elif button_sound_off.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_sound_off, border_radius=25)
                self.sc.blit(sound_off, (button_sound_off.centerx - 15, button_sound_off.centery - 15))
                if mouse_click[0]:
                    return 0

            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25)
                self.sc.blit(exit, (button_exit.centerx - 85, button_exit.centery - 70))
                if mouse_click[0]:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(20)
        return 10

    def pause(self):
        self.pause_trigger = True
        pygame.mixer.music.pause()
        x = 0
        button_font = pygame.font.Font('font/font.ttf', 72)
        label_font = pygame.font.Font('font/font1.otf', 400)
        continue_game = button_font.render('CONTINUE', 1, pygame.Color('lightgray'))
        button_continue = pygame.Rect(0, 0, 500, 150)
        button_continue.center = HALF_WIDTH, HALF_HEIGHT
        exit = button_font.render('MENU', 1, pygame.Color('lightgray'))
        button_exit = pygame.Rect(0, 0, 400, 150)
        button_exit.center = HALF_WIDTH, HALF_HEIGHT + 200

        button_sound_font = pygame.font.Font('font/font.ttf', 16)
        sound_on = button_sound_font.render('ON', 1, pygame.Color('lightgray'))
        button_sound_on = pygame.Rect(0, 0, 70, 70)
        button_sound_on.center = HALF_WIDTH + 430, HALF_HEIGHT - 120

        sound_off = button_sound_font.render('OFF', 1, pygame.Color('lightgray'))
        button_sound_off = pygame.Rect(0, 0, 70, 70)
        button_sound_off.center = HALF_WIDTH + 510, HALF_HEIGHT - 120

        while self.pause_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.sc.blit(self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            pygame.draw.rect(self.sc, BLACK, button_continue, border_radius=25, width=10)
            self.sc.blit(continue_game, (button_continue.centerx - 190, button_continue.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25, width=10)
            self.sc.blit(exit, (button_exit.centerx - 95, button_exit.centery - 70))

            pygame.draw.rect(self.sc, BLACK, button_sound_on, border_radius=25, width=5)
            self.sc.blit(sound_on, (button_sound_on.centerx - 12, button_sound_on.centery - 15))

            pygame.draw.rect(self.sc, BLACK, button_sound_off, border_radius=25, width=5)
            self.sc.blit(sound_off, (button_sound_off.centerx - 15, button_sound_off.centery - 15))

            color = randrange(40)
            label = label_font.render('PAUSE', 1, (color, color, color))
            self.sc.blit(label, (140, -30))

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            if button_continue.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_continue, border_radius=25)
                self.sc.blit(continue_game, (button_continue.centerx - 190, button_continue.centery - 70))
                if mouse_click[0]:
                    pygame.mouse.set_visible(False)
                    pygame.mixer.music.unpause()
                    self.pause_trigger = False

            elif button_sound_on.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_sound_on, border_radius=25)
                self.sc.blit(sound_on, (button_sound_on.centerx - 12, button_sound_on.centery - 15))
                if mouse_click[0]:
                    return 1

            elif button_sound_off.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_sound_off, border_radius=25)
                self.sc.blit(sound_off, (button_sound_off.centerx - 15, button_sound_off.centery - 15))
                if mouse_click[0]:
                    return 0


            elif button_exit.collidepoint(mouse_pos):
                pygame.draw.rect(self.sc, BLACK, button_exit, border_radius=25)
                self.sc.blit(exit, (button_exit.centerx - 95, button_exit.centery - 70))
                if mouse_click[0]:
                    self.pause_trigger = False
                    return 2

            pygame.display.flip()
            self.clock.tick(20)
        return 10

    def end(self):
        self.end_trigger = True
        x = 0
        rect = pygame.Rect(0, 0, 750, 150)
        rect.center = HALF_WIDTH, HALF_HEIGHT
        while self.end_trigger:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.sc.blit(self.menu_picture, (0, 0), (x % WIDTH, HALF_HEIGHT, WIDTH, HEIGHT))
            x += 1

            render = self.font_win_lose.render('IT\'s END!!!', 1, (randrange(40, 120), 0, 0))
            pygame.draw.rect(self.sc, BLACK, rect, border_radius=40)
            self.sc.blit(render, (rect.centerx - 300, rect.centery - 100))

            pygame.display.flip()
            self.clock.tick(20)