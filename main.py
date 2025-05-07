import pygame
import sys
import random
from units import Unit, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from enemies import Enemy

pygame.init()
pygame.mixer.init()

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
pygame.display.set_caption("Fire Emblem Heroes Clone")
clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 24)

# sound effects
hit_sound = pygame.mixer.Sound("Assets/retro-hurt-1-236672.mp3")

# Background
bg = pygame.image.load("Assets/TestMap.jpg").convert()
background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Context-menu state
attack_menu = False
end_menu    = False
menu_enemy  = None
attack_anim = None
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
    if (player_unit.x, player_unit.y)==(x,y): return True
    for e in enemy_units:
        if (e.x, e.y)==(x,y): return True
    return False

ATTACK_FRAMES = 8
ATTACK_OFFSET =TILE_SIZE // 6


# --- setup Marth ---
player_unit = Unit(5,5, color=(0,0,255), hp=10, attack=3)
m_img = pygame.image.load("Assets/Marth.png").convert_alpha()
player_unit.image = pygame.transform.scale(m_img, (TILE_SIZE,TILE_SIZE))
selected_unit = None
player_unit.path = []

# --- setup enemies ---
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

            # Attack Menu
            if attack_menu:
                if attack_btn.collidepoint(ev.pos) and not attack_anim:
                    dx = sign(menu_enemy.x - player_unit.x)
                    dy = sign(menu_enemy.y - player_unit.y)
                    attack_anim = {
                        "attacker": player_unit,
                        "target": menu_enemy,
                        "dx": dx,
                        "dy": dy,
                        "frame": 0,       
                    }
                    attack_menu = False
                
                elif cancel_btn.collidepoint(ev.pos):
                    attack_menu = False
                continue

            # End-turn menu
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

            # click on Marth
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
                    if dist<=selected_unit.max_moves and not is_occupied(gx,gy):
                        # build straight‐line path: horizontal then vertical
                        px, py = selected_unit.x, selected_unit.y
                        path = []
                        dx_total = gx - px
                        dy_total = gy - py
                        sx = sign(dx_total)
                        for _ in range(abs(dx_total)):
                            path.append((sx,0))
                        sy = sign(dy_total)
                        for _ in range(abs(dy_total)):
                            path.append((0,sy))
                        selected_unit.path = path


    if turn == "enemy":
        if enemy_index < len(enemy_units):
            en = enemy_units[enemy_index]
            if not en.has_attacked:
                if abs(en.x - player_unit.x) + abs(en.y - player_unit.y) <= en.attack_range:
                    if not attack_anim:
                        dx = sign(player_unit.x - en.x)
                        dy = sign(player_unit.y - en.y)
                        attack_anim = {
                            'attacker': en,
                            'target':   player_unit,
                            'dx':       dx,
                            'dy':       dy,
                            'frame':    0
                        }
                else:
                    while not en.animating and en.moves_used < en.max_moves and \
                          abs(en.x - player_unit.x) + abs(en.y - player_unit.y) > en.attack_range:
                        dx, dy = sign(player_unit.x - en.x), sign(player_unit.y - en.y)
                        if abs(player_unit.x - en.x) >= abs(player_unit.y - en.y):
                            if not is_occupied(en.x + dx, en.y):
                                en.move(dx, 0)
                        else:
                            if not is_occupied(en.x, en.y + dy):
                                en.move(0, dy)
                    # then schedule attack animation
                    if not en.animating and abs(en.x - player_unit.x) + abs(en.y - player_unit.y) <= en.attack_range and not en.has_attacked:
                        dx = sign(player_unit.x - en.x)
                        dy = sign(player_unit.y - en.y)
                        attack_anim = {
                            'attacker': en,
                            'target':   player_unit,
                            'dx':       dx,
                            'dy':       dy,
                            'frame':    0
                        }
            if not en.animating and not attack_anim:
                en.reset_moves()
                enemy_index += 1
                pygame.time.wait(300)
        else:
            turn = "player"
            player_unit.reset_moves()
            for e in enemy_units:
                e.reset_moves()
    
    if selected_unit is player_unit and not player_unit.animating and getattr(player_unit, 'path', []):
        dx,dy = player_unit.path.pop(0)
        # check occupancy before step
        if not is_occupied(player_unit.x+dx, player_unit.y+dy):
            player_unit.move(dx,dy)
        else:
            # blocked: clear path
            player_unit.path = []
    
    # Process attack animation
    if attack_anim:
        A = attack_anim
        atk = A['attacker']
        tgt = A['target']
        f   = A['frame']
        # calculate offset
        t = f / (ATTACK_FRAMES / 2)
        offset = ATTACK_OFFSET * (1 - abs(1 - t))
        atk.pixel_x = atk.x * TILE_SIZE + A['dx'] * offset
        atk.pixel_y = atk.y * TILE_SIZE + A['dy'] * offset
        A['frame'] += 1
        # mid‐animation damage
        if A['frame'] == ATTACK_FRAMES // 2:
            atk.attack_target(tgt)
            hit_sound.play()
            atk.has_attacked = True
            if tgt.hp <= 0 and tgt in enemy_units:
                enemy_units.remove(tgt)
        # end animation
        if A['frame'] >= ATTACK_FRAMES:
            atk.pixel_x = atk.x * TILE_SIZE
            atk.pixel_y = atk.y * TILE_SIZE
            # advance turn if player attacked
            if atk is player_unit:
                selected_unit.reset_moves()
                selected_unit = None
                turn = "enemy"
                enemy_index = 0
            attack_anim = None

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