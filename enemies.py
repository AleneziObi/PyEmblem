from units import Unit

class Enemy(Unit):
    def __init__(self, x, y, color, hp=5, attack=2, max_moves=3, attack_range=1):
        super().__init__(x, y, color, hp, attack, max_moves, attack_range)

    def take_turn(self, player_unit):
        # If in attack range, attack the player.
        if abs(self.x - player_unit.x) + abs(self.y - player_unit.y) <= self.attack_range:
            self.attack_target(player_unit)
        else:
            dx = player_unit.x - self.x
            dy = player_unit.y - self.y

            # Decide which direction to move (prioritize the axis with the larger distance)
            if abs(dx) >= abs(dy):
                step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                self.move(step_x, 0)
            else:
                step_y = 1 if dy > 0 else -1 if dy < 0 else 0
                self.move(0, step_y)
        self.reset_moves()
