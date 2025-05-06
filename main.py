import pygame
import sys
import random
from units import Unit, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from enemies import Enemy

pygame.init()

FPS = 60
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY  = (200,200,200)
RED   = (255,0,0)    # highlights & menu buttons
GREEN = (0,255,0)    # attack range highlight

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fire Emblem Clone - Mouse Controls")
clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 24)

# Background
bg = pygame.image.load("Assets/TestMap.jpg").convert()
background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Context-menu state
attack_menu = False
end_menu    = False
menu_enemy  = None
MENU_W, MENU_H = 80, 30
attack_btn   = pygame.Rect(0,0,MENU_W,MENU_H)
cancel_btn   = pygame.Rect(0,0,MENU_W,MENU_H)

def draw_grid(s):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            pygame.draw.rect(s, GRAY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def highlight_move(u, s):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if abs(x-u.start_x)+abs(y-u.start_y) <= u.max_moves:
                pygame.draw.rect(s, RED, (x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE),3)

def highlight_attack(u, s):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if abs(x-u.x)+abs(y-u.y) <= u.attack_range and (x,y)!=(u.x,u.y):
                pygame.draw.rect(s, GREEN, (x*TILE_SIZE,y*TILE_SIZE,TILE_SIZE,TILE_SIZE),3)

def sign(v): return (v>0)-(v<0)

def draw_unit(s, u):
    # sprite at pixel coords
    s.blit(u.image, (u.pixel_x, u.pixel_y))
    # hp box
    bw, bh = TILE_SIZE//4, TILE_SIZE//4
    bx, by = u.pixel_x, u.pixel_y+TILE_SIZE-bh
    pygame.draw.rect(s, WHITE, (bx,by,bw,bh))
    txt = font.render(str(u.hp), True, BLACK)
    s.blit(txt, (bx+2, by+1))

def is_occupied(x, y):
    # Don’t allow moving into the player’s tile
    if (player_unit.x, player_unit.y) == (x, y):
        return True
    # Don’t allow moving into any enemy tile
    for e in enemy_units:
        if (e.x, e.y) == (x, y):
            return True
    return False


# --- setup Marth ---
player_unit = Unit(5,5, color=(0,0,255), hp=10, attack=3)
m_img = pygame.image.load("Assets/Marth.png").convert_alpha()
player_unit.image = pygame.transform.scale(m_img, (TILE_SIZE,TILE_SIZE))
selected_unit = None

# --- setup enemies (no overlap) ---
enemy_units = []
occupied = {(player_unit.x, player_unit.y)}
while len(enemy_units)<3:
    ex,ey = random.randint(0,GRID_WIDTH-1), random.randint(0,GRID_HEIGHT-1)
    if (ex,ey) in occupied: continue
    e = Enemy(ex, ey, color=(255,0,0), hp=5, attack=2)
    enemy_units.append(e)
    occupied.add((ex,ey))

# turn state
turn = "player"
enemy_index = 0

running = True
while running:
    # game over
    if player_unit.hp<=0:
        print("Game Over! Marth has fallen.")
        break

    # input
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            running=False

        elif ev.type==pygame.MOUSEBUTTONDOWN:
            mx,my = ev.pos
            gx,gy = mx//TILE_SIZE, my//TILE_SIZE

            # 1) attack menu?
            if attack_menu:
                if attack_btn.collidepoint(ev.pos):
                    player_unit.attack_target(menu_enemy)
                    player_unit.has_attacked=True
                    if menu_enemy.hp<=0:
                        enemy_units.remove(menu_enemy)
                    attack_menu=False
                    selected_unit.reset_moves()
                    selected_unit=None
                    turn="enemy"
                    enemy_index=0
                elif cancel_btn.collidepoint(ev.pos):
                    attack_menu=False
                continue

            # 2) end-turn menu?
            if end_menu:
                if attack_btn.collidepoint(ev.pos):
                    selected_unit.reset_moves()
                    selected_unit=None
                    end_menu=False
                    turn="enemy"
                    enemy_index=0
                elif cancel_btn.collidepoint(ev.pos):
                    end_menu=False
                continue

            # 3) click on Marth?
            if turn=="player" and (gx,gy)==(player_unit.x,player_unit.y):
                if selected_unit is player_unit:
                    end_menu=True
                    attack_btn.topleft=(mx,my)
                    cancel_btn.topleft=(mx,my+MENU_H+5)
                else:
                    selected_unit=player_unit
                continue

            # 4) attack or move
            if turn=="player" and selected_unit:
                # attack?
                for e in enemy_units:
                    if (e.x,e.y)==(gx,gy) and abs(e.x-player_unit.x)+abs(e.y-player_unit.y)<=player_unit.attack_range:
                        menu_enemy=e
                        attack_menu=True
                        attack_btn.topleft=(mx,my)
                        cancel_btn.topleft=(mx,my+MENU_H+5)
                        break
                else:
                    # move one tile if in range
                    # movement: animate one step if in range AND target is free
                    dist = abs(gx-selected_unit.start_x)+abs(gy-selected_unit.start_y)
                    if dist <= selected_unit.max_moves and not is_occupied(gx, gy):
                        dx, dy = sign(gx-selected_unit.x), sign(gy-selected_unit.y)
                        selected_unit.move(dx, dy)


    # enemy turn
    if turn=="enemy":
        if enemy_index < len(enemy_units):
            en = enemy_units[enemy_index]
            if not en.has_attacked:
                if abs(en.x-player_unit.x)+abs(en.y-player_unit.y)<=en.attack_range:
                    en.attack_target(player_unit)
                    en.has_attacked=True
                else:
                    # move full range
                    while (not en.animating and
                           en.moves_used<en.max_moves and
                           abs(en.x-player_unit.x)+abs(en.y-player_unit.y)>en.attack_range):
                        dx,dy = sign(player_unit.x-en.x), sign(player_unit.y-en.y)
                        # prefer horizontal
                        if abs(player_unit.x - en.x) >= abs(player_unit.y - en.y):
                            if not is_occupied(en.x + dx, en.y):
                                en.move(dx, 0)
                        else:
                            if not is_occupied(en.x, en.y + dy):
                                en.move(0, dy)
                    # then attack
                    if (not en.animating and
                        abs(en.x-player_unit.x)+abs(en.y-player_unit.y)<=en.attack_range and 
                        not en.has_attacked):
                        en.attack_target(player_unit)
                        en.has_attacked=True
            if not en.animating:
                en.reset_moves()
                enemy_index+=1
                pygame.time.wait(300)
        else:
            turn="player"
            player_unit.reset_moves()
            for e in enemy_units: 
                e.reset_moves()

    # animations
    player_unit.update_animation()
    for e in enemy_units:
        e.update_animation()

    # draw
    screen.blit(background,(0,0))
    draw_grid(screen)
    if turn=="player" and selected_unit:
        highlight_move(selected_unit, screen)
        highlight_attack(selected_unit, screen)
    for e in enemy_units:
        draw_unit(screen, e)
    draw_unit(screen, player_unit)

    # menus
    if attack_menu:
        bb = attack_btn.union(cancel_btn).inflate(4,4)
        pygame.draw.rect(screen,WHITE,bb)
        pygame.draw.rect(screen,RED,attack_btn)
        screen.blit(font.render("Attack",True,WHITE),(attack_btn.x+5,attack_btn.y+5))
        pygame.draw.rect(screen,BLACK,cancel_btn)
        screen.blit(font.render("Cancel",True,WHITE),(cancel_btn.x+5,cancel_btn.y+5))
    if end_menu:
        bb = attack_btn.union(cancel_btn).inflate(4,4)
        pygame.draw.rect(screen,WHITE,bb)
        pygame.draw.rect(screen,RED,attack_btn)
        screen.blit(font.render("End Turn",True,WHITE),(attack_btn.x+5,attack_btn.y+5))
        pygame.draw.rect(screen,BLACK,cancel_btn)
        screen.blit(font.render("Cancel",True,WHITE),(cancel_btn.x+5,cancel_btn.y+5))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
