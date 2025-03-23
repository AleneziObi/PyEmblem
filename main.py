import pygame
import sys
import random
from units import Unit, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from enemies import Enemy

pygame.init()

# Constants
FPS = 60
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT

# Colors
WHITE  = (255, 255, 255)
GRAY   = (200, 200, 200)
RED    = (255, 0, 0)      # For enemy units and movement range highlight
BLUE   = (0, 0, 255)      # For the player unit
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 0)      # For attack range highlight

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fire Emblem Clone - Turn-Based Combat")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

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

# Create the player unit (blue)
player_unit = Unit(5, 5, BLUE, hp=10, attack=3)
selected_unit = None  

# Create enemy units (red) at random positions
enemy_units = []
num_enemies = 3
while len(enemy_units) < num_enemies:
    ex = random.randint(0, GRID_WIDTH - 1)
    ey = random.randint(0, GRID_HEIGHT - 1)
    if ex == player_unit.x and ey == player_unit.y:
        continue
    enemy_units.append(Enemy(ex, ey, RED, hp=5, attack=2))

# Turn management variables
turn = "player"  # "player" or "enemy"
enemy_index = 0  # Which enemy is acting during the enemy turn

running = True
while running:
    # Check if the player has been defeated
    if player_unit.hp <= 0:
        print("Game Over! The player has been defeated.")
        running = False

    if turn == "player":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                grid_x = pos[0] // TILE_SIZE
                grid_y = pos[1] // TILE_SIZE
                if player_unit.x == grid_x and player_unit.y == grid_y:
                    selected_unit = player_unit
                else:
                    selected_unit = None
            elif event.type == pygame.KEYDOWN and selected_unit:
                if event.key == pygame.K_LEFT:
                    selected_unit.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    selected_unit.move(1, 0)
                elif event.key == pygame.K_UP:
                    selected_unit.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    selected_unit.move(0, 1)
                elif event.key == pygame.K_a:
                    # Attack the first enemy in range
                    for enemy in enemy_units[:]:
                        if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= player_unit.attack_range:
                            player_unit.attack_target(enemy)
                            print(f"Player attacked enemy at ({enemy.x}, {enemy.y}). Enemy HP is now {enemy.hp}.")
                            if enemy.hp <= 0:
                                print(f"Enemy at ({enemy.x}, {enemy.y}) defeated!")
                                enemy_units.remove(enemy)
                            break
                elif event.key == pygame.K_RETURN:
                    selected_unit.reset_moves()
                    selected_unit = None
                    turn = "enemy"
                    enemy_index = 0

    elif turn == "enemy":
        # Process events to allow closing the window during enemy turn
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if enemy_index < len(enemy_units):
            enemy = enemy_units[enemy_index]
            # If enemy is in attack range, attack the player.
            if abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) <= enemy.attack_range:
                enemy.attack_target(player_unit)
                print(f"Enemy at ({enemy.x}, {enemy.y}) attacked player. Player HP is now {player_unit.hp}.")
            else:
                # Use full movement range: move until within attack range or movement is exhausted.
                while enemy.moves_used < enemy.max_moves and (abs(enemy.x - player_unit.x) + abs(enemy.y - player_unit.y) > enemy.attack_range):
                    dx = sign(player_unit.x - enemy.x)
                    dy = sign(player_unit.y - enemy.y)
                    if abs(player_unit.x - enemy.x) >= abs(player_unit.y - enemy.y):
                        enemy.move(dx, 0)
                    else:
                        enemy.move(0, dy)
            enemy.reset_moves()
            enemy_index += 1
            pygame.time.wait(300)
        else:
            turn = "player"
            player_unit.reset_moves()
            for enemy in enemy_units:
                enemy.reset_moves()

    screen.fill(BLACK)
    draw_grid(screen)

    if turn == "player" and selected_unit:
        highlight_movement_range(selected_unit, screen)
        highlight_attack_range(selected_unit, screen)

    for enemy in enemy_units:
        enemy.draw(screen, font)
    player_unit.draw(screen, font)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()


