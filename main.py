from map import user_map
from sprite_objects import Sprites
from ray_casting import ray_casting_walls
from drawing import Drawing
from interaction import Interaction
from player import Player
import pygame
from settings import WIDTH, HEIGHT, MINIMAP_RES
from lvl_desine import *

import sys

def initialization(choice, chek_music):
    pygame.init()
    if choice == 1:
        user_map(LVL1)
        chek_lvl = 1
    elif choice == 2:
        user_map(LVL2)
        chek_lvl = 2
    elif choice == 3:
        user_map(LVL3)
        chek_lvl = 3
    else:
        user_map(LVL4)
        chek_lvl = 4

    sc = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('DOOMPy')
    sc_map = pygame.Surface(MINIMAP_RES)
    sprites = Sprites(chek_lvl)
    clock = pygame.time.Clock()                              # Normal of FPS
    player = Player(sprites)
    drawing = Drawing(sc, sc_map, player, clock)
    interaction = Interaction(player, sprites, drawing)

    GAME(sprites, player, drawing, interaction, clock, choice, chek_lvl, chek_music)

def GAME(sprites, player, drawing, interaction, clock, choice, chek_lvl, chek_music):
    pygame.mouse.set_visible(True)
    go = True

    music = chek_music
    while go:
        k = drawing.menu()
        if k == 10:
            go = False
        elif k == 1:
            music = chek_music = 1
        elif k == 0:
            music = chek_music = 0

    interaction.play_music(music)
    pygame.mouse.set_visible(False)
    while True:
        go2 = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.mouse.set_visible(True)
            while go2:
                c = drawing.pause()
                if c == 10:
                    go2 = False
                    interaction.play_music(music)
                elif c == 0:
                    music = chek_music = 0
                    pygame.mixer.music.stop()
                elif c == 1:
                    music = chek_music = 1
                elif c == 2:
                    pygame.mixer.quit()
                    initialization(choice, chek_music)

        player.movement()

        drawing.background(player.angle)
        walls, wall_shot = ray_casting_walls(player, drawing.textures)
        drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
        drawing.player_health(player)
        drawing.fps(clock)
        drawing.mini_map(player)
        drawing.player_weapon([wall_shot, sprites.sprite_shot],chek_music)

        interaction.interaction_objects(chek_music)
        interaction.npc_action()
        interaction.clear_world()
        interaction.npc_damage(chek_music)

        if interaction.chek_win(chek_music):
            if chek_lvl == 4:
                drawing.end()
            pygame.mixer.quit()
            initialization((choice + 1), chek_music)
        if interaction.chek_lose(chek_music):
            pygame.mixer.quit()
            initialization(choice, chek_music)

        pygame.display.flip()                               #Update display on all iteration
        clock.tick()

initialization(1, 1)
