import pygame

TILE_SIZE = 80
GRID_WIDTH = 6
GRID_HEIGHT = 8

class Unit:
    def __init__(self, x, y, color, hp=10, attack=3, max_moves=3, attack_range=1):
        self.x = x
        self.y = y
        self.start_x = x 
        self.start_y = y
        self.color = color
        self.hp = hp
        self.attack = attack
        self.max_moves = max_moves
        self.moves_used = 0
        self.attack_range = attack_range
        self.has_attacked = False

    def draw(self, surface, font):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, self.color, rect)
        # Draw HP text in the center of the tile
        hp_text = font.render(str(self.hp), True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(self.x * TILE_SIZE + TILE_SIZE // 2, 
                                             self.y * TILE_SIZE + TILE_SIZE // 2))
        surface.blit(hp_text, text_rect)

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            new_distance = abs(new_x - self.start_x) + abs(new_y - self.start_y)
            if new_distance <= self.max_moves:
                self.x = new_x
                self.y = new_y
                self.moves_used = new_distance

    def reset_moves(self):
        self.start_x = self.x
        self.start_y = self.y
        self.moves_used = 0
        self.has_attacked = False  # Reset the attack flag for a new turn

    def attack_target(self, target):
        target.hp -= self.attack
