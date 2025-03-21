import pygame
import sys

# Initialize Pygame
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
pygame.display.set_caption("Fire Emblem Clone - Movement Range Highlight")
clock = pygame.time.Clock()

# Setup font for displaying moves left
font = pygame.font.SysFont(None, 24)

# Define a Unit class with a movement range based on its starting position each turn
class Unit:
    def __init__(self, x, y, color=RED):
        self.x = x
        self.y = y
        self.start_x = x  # Starting position for the current turn
        self.start_y = y
        self.color = color
        self.max_moves = 3  # Maximum movement range per turn
        self.moves_used = 0  # Manhattan distance from the starting position

    def draw(self, surface):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        # Check grid boundaries
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            # Calculate Manhattan distance from the starting position
            new_distance = abs(new_x - self.start_x) + abs(new_y - self.start_y)
            if new_distance <= self.max_moves:
                self.x = new_x
                self.y = new_y
                self.moves_used = new_distance

    def reset_moves(self):
        # Commit the new position as the starting position for the next turn
        self.start_x = self.x
        self.start_y = self.y
        self.moves_used = 0

# Function to draw the grid map
def draw_grid(surface):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)

# Function to highlight the movement range from the unit's starting position
def highlight_movement_range(unit, surface):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # If the tile is within the max movement range (Manhattan distance)
            if abs(x - unit.start_x) + abs(y - unit.start_y) <= unit.max_moves:
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, GREEN, rect, 3)

# Create a player unit
player_unit = Unit(5, 5)
selected_unit = None  

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
            # Check if the click is on the player unit
            if player_unit.x == grid_x and player_unit.y == grid_y:
                selected_unit = player_unit
            else:
                selected_unit = None

        # Move the selected unit with arrow keys if it's selected
        elif event.type == pygame.KEYDOWN and selected_unit:
            if event.key == pygame.K_LEFT:
                selected_unit.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                selected_unit.move(1, 0)
            elif event.key == pygame.K_UP:
                selected_unit.move(0, -1)
            elif event.key == pygame.K_DOWN:
                selected_unit.move(0, 1)
            # When Enter is pressed, commit the new position and deselect the unit
            elif event.key == pygame.K_RETURN:
                selected_unit.reset_moves()
                selected_unit = None
            # Reset movement (simulate a new turn) with the "R" key while still selected
            elif event.key == pygame.K_r:
                selected_unit.reset_moves()

    # Clear screen
    screen.fill(BLACK)

    # Draw grid
    draw_grid(screen)

    # If a unit is selected, highlight the movement range based on its starting position
    if selected_unit:
        highlight_movement_range(selected_unit, screen)

    # Draw the player unit
    player_unit.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()


