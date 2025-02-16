import pygame
import sys

pygame.init()

# Constants
TILE_SIZE = 40
GRID_WIDTH = 16
GRID_HEIGHT = 12
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Setup display and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fire Emblem Clone - Turn-Based")
clock = pygame.time.Clock()

# Define a Unit class
class Unit:
    def __init__(self, x, y, color=RED):
        self.x = x
        self.y = y
        self.color = color
        self.move_range = 3  # Example movement range

    def draw(self, surface):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)

# Function to draw the grid map
def draw_grid(surface):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)

# Function to highlight the selected unit
def highlight_unit(unit, surface):
    rect = pygame.Rect(unit.x * TILE_SIZE, unit.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(surface, GREEN, rect, 3)

# Create a player unit
player_unit = Unit(5, 5)
selected_unit = None  # No unit is selected at the start

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Use mouse click for unit selection
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            grid_x = pos[0] // TILE_SIZE
            grid_y = pos[1] // TILE_SIZE
            # Check if the player unit was clicked
            if player_unit.x == grid_x and player_unit.y == grid_y:
                selected_unit = player_unit
            else:
                # Deselect if clicked elsewhere
                selected_unit = None

        # Move the selected unit with arrow keys
        elif event.type == pygame.KEYDOWN and selected_unit:
            if event.key == pygame.K_LEFT:
                selected_unit.x = max(0, selected_unit.x - 1)
            elif event.key == pygame.K_RIGHT:
                selected_unit.x = min(GRID_WIDTH - 1, selected_unit.x + 1)
            elif event.key == pygame.K_UP:
                selected_unit.y = max(0, selected_unit.y - 1)
            elif event.key == pygame.K_DOWN:
                selected_unit.y = min(GRID_HEIGHT - 1, selected_unit.y + 1)

    # Clear screen
    screen.fill(BLACK)

    # Draw grid and units
    draw_grid(screen)
    player_unit.draw(screen)
    if selected_unit:
        highlight_unit(selected_unit, screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

