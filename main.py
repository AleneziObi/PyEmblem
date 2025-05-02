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
        print("Game Over! The player has been defeated.")
        break

    if turn == "player":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                selected_unit = player_unit if (gx, gy) == (player_unit.x, player_unit.y) else None
            elif event.type == pygame.KEYDOWN and selected_unit:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    dx = (event.key == pygame.K_RIGHT) - (event.key == pygame.K_LEFT)
                    dy = (event.key == pygame.K_DOWN) - (event.key == pygame.K_UP)
                    selected_unit.move(dx, dy)
                elif event.key == pygame.K_a:
                    if not selected_unit.has_attacked:
                        for enemy in enemy_units[:]:
                            if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= player_unit.attack_range:
                                player_unit.attack_target(enemy)
                                selected_unit.has_attacked = True
                                if enemy.hp <= 0:
                                    enemy_units.remove(enemy)
                                break
                    # end turn on attack
                    selected_unit.reset_moves()
                    selected_unit = None
                    turn = "enemy"
                    enemy_index = 0
                elif event.key == pygame.K_w:
                    # wait: end turn
                    selected_unit.reset_moves()
                    selected_unit = None
                    turn = "enemy"
                    enemy_index = 0

    else:  # enemy turn
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if enemy_index < len(enemy_units):
            enemy = enemy_units[enemy_index]
            if not enemy.has_attacked:
                if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= enemy.attack_range:
                    enemy.attack_target(player_unit)
                    enemy.has_attacked = True
                else:
                    while enemy.moves_used < enemy.max_moves and (abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) > enemy.attack_range):
                        dx = sign(player_unit.x - enemy.x)
                        dy = sign(player_unit.y - enemy.y)
                        if abs(player_unit.x - enemy.x) >= abs(player_unit.y - enemy.y):
                            enemy.move(dx, 0)
                        else:
                            enemy.move(0, dy)
                    if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= enemy.attack_range and not enemy.has_attacked:
                        enemy.attack_target(player_unit)
                        enemy.has_attacked = True
            enemy.reset_moves()
            enemy_index += 1
            pygame.time.wait(300)
        else:
            turn = "player"
            player_unit.reset_moves()
            for e in enemy_units:
                e.reset_moves()

    # draw everything
    screen.blit(background, (0, 0))
    draw_grid(screen)
    if turn == "player" and selected_unit:
        highlight_movement_range(selected_unit, screen)
        highlight_attack_range(selected_unit, screen)
    for enemy in enemy_units:
        draw_unit_with_hp(screen, enemy, font)
    draw_unit_with_hp(screen, player_unit, font)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

