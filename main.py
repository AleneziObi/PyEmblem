import pygame
import sys
import random
from units import Unit, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
import animations 
import menu
from enemies import Enemy
from collections import deque

import traceback

pygame.init()
pygame.mixer.init()

heal_sound = pygame.mixer.Sound("Assets/677080__silverillusionist__healing-soft-ripple.wav")

PLAYER_MUSIC = "Assets/006. Offense [Battle - Player Turn].mp3"
ENEMY_MUSIC  = "Assets/005. Defense [Battle - Enemy Turn].mp3"

# Start with player music
pygame.mixer.music.load(PLAYER_MUSIC)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
last_turn = "player"



FPS = 60
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY  = (200,200,200)
RED   = (255,0,0)    # highlights & menu buttons
GREEN = (0,255,0)    # attack range highlight

# Coordinates of tiles that heal & grant defense
FORTIFY_TILES = {(2, 2), (5, 2), (0, 3), (3, 3), (2,4), (0,5), (3, 5), (5, 4)}


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fire Emblem Heroes Clone")
clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 24)

# Background
bg = pygame.image.load("Assets/TestMap.jpg").convert()
background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

heal_icon = pygame.image.load("Assets/Heal_FE16.png").convert_alpha()
ICON_SIZE = TILE_SIZE // 3
heal_icon = pygame.transform.scale(heal_icon, (ICON_SIZE, ICON_SIZE))

heal_effect = []

# Context-menu state
attack_menu = False
end_menu    = False
menu_enemy  = None
attack_anim = None

#Draw the map grid lines
def draw_grid(s):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            pygame.draw.rect(s, GRAY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

# Highlight the move range
def highlight_move(u, s):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if abs(x - u.start_x) + abs(y - u.start_y) <= u.max_moves:
                pygame.draw.rect(s, RED, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

# Highlight attack range
def highlight_attack(u, s):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if abs(x - u.x) + abs(y - u.y) <= u.attack_range and (x, y) != (u.x, u.y):
                pygame.draw.rect(s, GREEN, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

# Sign function for movement
def sign(v): return (v > 0) - ( v < 0 )

# in bound check
def in_bounds(x, y):
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

def draw_unit(s, u):
    # sprite at pixel coords
    s.blit(u.image, (u.pixel_x, u.pixel_y))
    # hp box
    bw, bh = TILE_SIZE // 4, TILE_SIZE // 4
    bx, by = u.pixel_x, u.pixel_y + TILE_SIZE - bh
    pygame.draw.rect(s, WHITE, (bx, by, bw, bh))
    txt = font.render(str(u.hp), True, BLACK)
    s.blit(txt, (bx + 2, by + 1))

# Check if a tile is occupied by an enemy or the player
def is_occupied(x, y):
    if (player_unit.x, player_unit.y) == (x, y): return True

    for e in enemy_units:
        if (e.x, e.y) == (x, y): return True

    return False


# BFS pathfinder from (sx,sy) to (tx,ty), returns list of (x,y) steps (excluding start)
def find_path(sx, sy, tx, ty):
    queue = deque([ (sx, sy) ])
    came_from = { (sx, sy): None }
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    while queue:
        x, y = queue.popleft()
        if (x, y) == (tx, ty):
            # reconstruct path
            path = []
            cur = (tx, ty)
            while cur != (sx, sy):
                path.append(cur)
                cur = came_from[cur]
            return list(reversed(path))
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in came_from and not is_occupied(nx, ny):
                came_from[(nx, ny)] = (x, y)
                queue.append((nx, ny))
    return []  # no path found


# --- setup Marth ---
player_unit = Unit(5, 5, color=(0,0,255), hp=10, attack=3)
m_img = pygame.image.load("Assets/Marth.png").convert_alpha()
player_unit.image = pygame.transform.scale(m_img, (TILE_SIZE,TILE_SIZE))
selected_unit = None
player_unit.path = []

# --- setup enemies ---
enemy_units = []
occupied = {(player_unit.x, player_unit.y)}
while len(enemy_units)<3:
    ex, ey = random.randint(0,GRID_WIDTH-1), random.randint(0,GRID_HEIGHT-1)
    if (ex,ey) in occupied: continue
    e = Enemy(ex, ey, color=(255,0,0), hp=5, attack=2)
    enemy_units.append(e)
    occupied.add((ex,ey))

# turn state
turn = "player"
enemy_index = 0

# Main loop
running = True
while running:
    try:
        if player_unit.hp <= 0:
            print("Game Over! Marth has fallen.")
            break

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            # Delegate to menu handler
            (attack_menu, end_menu, menu_enemy, selected_unit,
                turn, enemy_index, do_attack, do_endturn) = menu.handle_menu_events(
                ev, attack_menu, end_menu, menu_enemy,
                selected_unit, turn, enemy_index,
                enemy_units, player_unit, TILE_SIZE
            )
            if do_attack:
                attack_anim = animations.schedule_attack(player_unit, menu_enemy)

            if do_endturn:
                selected_unit.reset_moves()
                selected_unit = None
                turn = "enemy"
                enemy_index = 0

            # Movement click
            if (ev.type == pygame.MOUSEBUTTONDOWN and turn == "player" and selected_unit and
                not attack_menu and not end_menu and attack_anim is None):
                mx, my = ev.pos
                gx, gy = mx//TILE_SIZE, my//TILE_SIZE
                dist = abs(gx - selected_unit.start_x) + abs(gy - selected_unit.start_y)

                if dist <= selected_unit.max_moves and not is_occupied(gx, gy):
                    px, py = selected_unit.x, selected_unit.y
                    path = []
                    dx_tot = gx - px
                    sx = sign(dx_tot)

                    for _ in range(abs(dx_tot)):
                        path.append((sx, 0))

                    dy_tot = gy - py
                    sy = sign(dy_tot)

                    for _ in range(abs(dy_tot)):
                        path.append((0, sy))

                    selected_unit.path = path

        # Enemy turn
        if turn == "enemy" and attack_anim is None:
            if enemy_index < len(enemy_units):
                en = enemy_units[enemy_index]
                if not en.has_attacked:
                    # if adjacent, schedule attack
                    if abs(en.x - player_unit.x) + abs(en.y - player_unit.y) <= en.attack_range:
                        attack_anim = animations.schedule_attack(en, player_unit)
                    else:
                        # 1) build list of free adjacent tiles around player
                        directions = [(1,0),(-1,0),(0,1),(0,-1)]
                        adj_goals = []
                        for dx, dy in directions:
                            gx, gy = player_unit.x + dx, player_unit.y + dy
                            if in_bounds(gx, gy) and not is_occupied(gx, gy):
                                adj_goals.append((gx, gy))

                        # 2) pick a goal tile for *this* enemy
                        #    cycling through so they fan out
                        if adj_goals:
                            goal = adj_goals[enemy_index % len(adj_goals)]
                            # 3) find a path via BFS
                            path = find_path(en.x, en.y, goal[0], goal[1])
                            # 4) move along it up to max_moves
                            for step in path[: en.max_moves]:
                                dx, dy = step[0] - en.x, step[1] - en.y
                                en.move(dx, dy)
                                pygame.time.wait(25)
                            # 5) after moving, schedule an attack if now adjacent
                            if abs(en.x - player_unit.x) + abs(en.y - player_unit.y) <= en.attack_range:
                                attack_anim = animations.schedule_attack(en, player_unit)
                # finish turn for this enemy once it's neither animating nor has a pending attack_anim
                if not en.animating and attack_anim is None:
                    en.reset_moves()
                    enemy_index += 1

            else:
                turn = "player"
                player_unit.reset_moves()
                # Heal player on fortify tiles
                if (player_unit.x, player_unit.y) in FORTIFY_TILES:
                    player_unit.hp = min(player_unit.max_hp, player_unit.hp + 1)
                    heal_sound.play()
                    heal_effect.append((player_unit, pygame.time.get_ticks() + 3000))

                    
                # Heal enemies on fortify tiles
                for e in enemy_units:
                    e.reset_moves()
                    if (e.x, e.y) in FORTIFY_TILES:
                        e.hp = min(e.max_hp, e.hp + 1)
                        heal_sound.play()
                        heal_effect.append((e, pygame.time.get_ticks() + 3000))
        
        animations.process_movement_path(player_unit, is_occupied)

        if turn != last_turn:
            last_turn = turn
            if turn == "player":
                pygame.mixer.music.load(PLAYER_MUSIC)
            else:
                pygame.mixer.music.load(ENEMY_MUSIC)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        
        # Process attack animation
        if attack_anim:
            still = animations.process_attack_animation(attack_anim, enemy_units, player_unit)
            if not still:
                tgt = attack_anim["target"]
                if (tgt.x, tgt.y) in FORTIFY_TILES:
                    # soak 1 point
                    tgt.hp = min(tgt.max_hp, tgt.hp + 1)

                # if the player attacked, end their turn here:
                if attack_anim["attacker"] is player_unit:
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

        if turn == "player" and selected_unit:
            highlight_move(selected_unit, screen)
            highlight_attack(selected_unit, screen)

        for e in enemy_units:
            draw_unit(screen, e)
        draw_unit(screen, player_unit)

        now = pygame.time.get_ticks()
        for effect in heal_effect[:]:
            unit, expire = effect
            if now < expire:
                # draw icon at bottom‐right of this unit
                icon_x = unit.pixel_x + TILE_SIZE - ICON_SIZE
                icon_y = unit.pixel_y + TILE_SIZE - ICON_SIZE
                screen.blit(heal_icon, (icon_x, icon_y))
            else:
                heal_effect.remove(effect)

        menu.draw_menus(screen, font, attack_menu, end_menu)

        pygame.display.flip()
        clock.tick(FPS)

    except Exception as e:
        print("Uncaught exception:", e)
        traceback.print_exc()
        running = False

pygame.quit()
sys.exit()