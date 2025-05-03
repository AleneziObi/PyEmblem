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
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (200, 200, 200)
RED    = (255, 0, 0)      # movement range highlight
GREEN  = (0, 255, 0)      # attack range highlight

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fire Emblem Clone - Turn-Based Combat")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Load and scale background
background = pygame.image.load("Assets/TestMap.jpg").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

attack_menu = False
menu_enemy = None
MENU_WIDTH, MENU_HEIGHT = 80, 30
attack_btn = pygame.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
cancel_btn = pygame.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
end_turn_btn = pygame.Rect(10, SCREEN_HEIGHT - 40, 100, 30)

def draw_grid(surface):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)

def highlight_movement_range(unit, surface):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if abs(x - unit.start_x) + abs(y - unit.start_y) <= unit.max_moves:
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, RED, rect, 3)

def highlight_attack_range(unit, surface):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if abs(x - unit.x) + abs(y - unit.y) <= unit.attack_range:
                if not (x == unit.x and y == unit.y):
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, GREEN, rect, 3)

def sign(x):
    return (x > 0) - (x < 0)

def draw_unit_with_hp(surface, unit, font):
    # Blit unit.image at its grid pos and draw HP in a white box bottom-left
    # sprite
    surface.blit(unit.image, (unit.x * TILE_SIZE, unit.y * TILE_SIZE))
    # white box dimensions
    box_w, box_h = TILE_SIZE // 4, TILE_SIZE // 4
    box_x = unit.x * TILE_SIZE
    box_y = unit.y * TILE_SIZE + TILE_SIZE - box_h
    # draw box
    pygame.draw.rect(surface, WHITE, (box_x, box_y, box_w, box_h))
    # render HP text in black
    hp_text = font.render(str(unit.hp), True, BLACK)
    surface.blit(hp_text, (box_x + 2, box_y + 1))

# --- Setup player ---
player_unit = Unit(5, 5, BLUE:=(0,0,255), hp=10, attack=3)
# load Marth sprite
player_image = pygame.image.load("Assets/Marth.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))
player_unit.image = player_image

selected_unit = None

# --- Setup enemies ---
enemy_units = []
num_enemies = 3
while len(enemy_units) < num_enemies:
    ex = random.randint(0, GRID_WIDTH - 1)
    ey = random.randint(0, GRID_HEIGHT - 1)
    if ex == player_unit.x and ey == player_unit.y:
        continue
    # each Enemy loads "Thief.png" internally and scales it
    enemy_units.append(Enemy(ex, ey, RED:=(255,0,0), hp=5, attack=2))

# Turn variables
turn = "player"
enemy_index = 0

running = True
while running:
    if player_unit.hp <= 0:
        print("Game Over! Marth has fallen.")
        running = False
        break

    # Quit check
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse controls only
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            gx, gy = mx // TILE_SIZE, my // TILE_SIZE

            # 1) If attack menu open, handle its buttons
            if attack_menu:
                if attack_btn.collidepoint(event.pos):
                    player_unit.attack_target(menu_enemy)
                    player_unit.has_attacked = True
                    attack_menu = False
                    selected_unit.reset_moves()
                    selected_unit = None
                    turn = "enemy"
                    enemy_index = 0
                elif cancel_btn.collidepoint(event.pos):
                    attack_menu = False
                continue

            # 2) End Turn button
            if selected_unit and end_turn_btn.collidepoint(event.pos):
                selected_unit.reset_moves()
                selected_unit = None
                turn = "enemy"
                enemy_index = 0
                continue

            # 3) Player turn interactions
            if turn == "player":
                # a) Select Marth
                if (gx, gy) == (player_unit.x, player_unit.y):
                    selected_unit = player_unit
                    continue

                # b) If selected and clicked adjacent enemy, open attack menu
                if selected_unit:
                    for e in enemy_units:
                        if (e.x, e.y) == (gx, gy)\
                           and abs(e.x - player_unit.x) + abs(e.y - player_unit.y) <= player_unit.attack_range:
                            menu_enemy = e
                            attack_menu = True
                            attack_btn.topleft = (mx, my)
                            cancel_btn.topleft = (mx, my + MENU_HEIGHT + 5)
                            break
                    else:
                        # c) Movement: if within range, teleport Marth there
                        dist = abs(gx - selected_unit.start_x) + abs(gy - selected_unit.start_y)
                        if dist <= selected_unit.max_moves:
                            selected_unit.x, selected_unit.y = gx, gy
                            selected_unit.moves_used = dist

    # 4) Enemy turn
    if turn == "enemy":
        if enemy_index < len(enemy_units):
            enemy = enemy_units[enemy_index]
            if not enemy.has_attacked:
                # Attack if adjacent
                if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= enemy.attack_range:
                    enemy.attack_target(player_unit)
                    enemy.has_attacked = True
                else:
                    # Move full range toward player
                    while enemy.moves_used < enemy.max_moves and \
                          (abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) > enemy.attack_range):
                        dx = sign(player_unit.x - enemy.x)
                        dy = sign(player_unit.y - enemy.y)
                        if abs(player_unit.x - enemy.x) >= abs(player_unit.y - enemy.y):
                            enemy.move(dx, 0)
                        else:
                            enemy.move(0, dy)
                    # Then attack if now in range
                    if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= enemy.attack_range \
                       and not enemy.has_attacked:
                        enemy.attack_target(player_unit)
                        enemy.has_attacked = True
            enemy.reset_moves()
            enemy_index += 1
            pygame.time.wait(300)
        else:
            # All enemies done → back to player
            turn = "player"
            player_unit.reset_moves()
            for e in enemy_units:
                e.reset_moves()

    # --- Drawing ---
    screen.blit(background, (0, 0))
    draw_grid(screen)

    # Show movement & attack highlights if Marth is selected
    if turn == "player" and selected_unit:
        highlight_movement_range(selected_unit, screen)
        highlight_attack_range(selected_unit, screen)

    # Draw End Turn button
    pygame.draw.rect(screen, WHITE, end_turn_btn)
    screen.blit(font.render("End Turn", True, BLACK),
                (end_turn_btn.x + 5, end_turn_btn.y + 5))
    
    # Draw units with HP boxes
    for enemy in enemy_units:
        draw_unit_with_hp(screen, enemy, font)
    draw_unit_with_hp(screen, player_unit, font)

    # Draw attack menu if open
    if attack_menu:
        bbox = attack_btn.union(cancel_btn).inflate(4, 4)
        pygame.draw.rect(screen, WHITE, bbox)
        pygame.draw.rect(screen, RED, attack_btn)
        screen.blit(font.render("Attack", True, WHITE),
                    (attack_btn.x + 5, attack_btn.y + 5))
        pygame.draw.rect(screen, BLACK, cancel_btn)
        screen.blit(font.render("Cancel", True, WHITE),
                    (cancel_btn.x + 5, cancel_btn.y + 5))


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()