import pygame
from units import TILE_SIZE

pygame.mixer.init()

# Animation constants
ATTACK_FRAMES = 8
ATTACK_OFFSET = TILE_SIZE // 6

hit_sound = pygame.mixer.Sound("Assets/retro-hurt-1-236672.mp3")

def sign(v):
    """Return the sign of v: -1, 0, or 1."""
    return (v > 0) - (v < 0)


def schedule_attack(attacker, target):
 
    dx = sign(target.x - attacker.x)
    dy = sign(target.y - attacker.y)
    return {
        "attacker": attacker,
        "target":   target,
        "dx":       dx,
        "dy":       dy,
        "frame":    0
    }


def process_attack_animation(anim, enemy_units, player_unit):
    
    if not anim:
        return False
    A = anim
    atk = A["attacker"]
    tgt = A["target"]
    f   = A["frame"]

    # Ease‐in/out offset calculation
    t = f / (ATTACK_FRAMES / 2)
    offset = ATTACK_OFFSET * (1 - abs(1 - t))

    # Apply pixel offset
    atk.pixel_x = atk.x * TILE_SIZE + A["dx"] * offset
    atk.pixel_y = atk.y * TILE_SIZE + A["dy"] * offset

    # Advance frame counter
    A["frame"] += 1

    # Mid-animation: apply damage and play sound
    if A["frame"] == ATTACK_FRAMES // 2:
        atk.attack_target(tgt)
        hit_sound.play()
        atk.has_attacked = True
        # Remove dead enemies
        if tgt.hp <= 0 and tgt in enemy_units:
            enemy_units.remove(tgt)

    # End animation
    if A["frame"] >= ATTACK_FRAMES:
        # Snap back to grid-aligned position
        atk.pixel_x = atk.x * TILE_SIZE
        atk.pixel_y = atk.y * TILE_SIZE
        return False

    return True


def process_movement_path(unit, is_occupied):
    
    path = getattr(unit, 'path', None)
    if path and not unit.animating:
        dx, dy = path.pop(0)
        # Only move if destination is free
        if not is_occupied(unit.x + dx, unit.y + dy):
            unit.move(dx, dy)
        else:
            # Blocked: cancel remaining path
            unit.path = []