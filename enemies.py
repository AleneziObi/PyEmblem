from units import Unit, TILE_SIZE
import pygame

class Enemy(Unit):
    def __init__(self, x, y, color, hp=5, attack=2, max_moves=3, attack_range=1):
        super().__init__(x, y, color, hp, attack, max_moves, attack_range)
        self.image = pygame.image.load("Assets/Theif.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 80))
    
    def draw(self, surface, font):
        # Draw the enemy image instead of a colored rectangle.
        surface.blit(self.image, (self.x * TILE_SIZE, self.y * TILE_SIZE))
       
        hp_text = font.render(str(self.hp), True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(self.x * TILE_SIZE + TILE_SIZE // 2,
                                              self.y * TILE_SIZE + TILE_SIZE // 2))
        surface.blit(hp_text, text_rect)
