import pygame

# Menu button dimensions
MENU_W, MENU_H = 80, 30
# Attack and Cancel buttons share positions for both menus
attack_btn = pygame.Rect(0, 0, MENU_W, MENU_H)
cancel_btn = pygame.Rect(0, 0, MENU_W, MENU_H)


def handle_menu_events(event, attack_menu, end_menu, menu_enemy,
                       selected_unit, turn, enemy_index,
                       enemy_units, player_unit, TILE_SIZE):
    
    do_attack = False
    do_endturn = False
    # Only handle mouse clicks
    if event.type != pygame.MOUSEBUTTONDOWN:
        return attack_menu, end_menu, menu_enemy, selected_unit, turn, enemy_index, do_attack, do_endturn

    mx, my = event.pos
    gx, gy = mx // TILE_SIZE, my // TILE_SIZE

    # 1) Attack menu interaction
    if attack_menu:
        if attack_btn.collidepoint(mx, my):
            attack_menu = False
            do_attack = True
        elif cancel_btn.collidepoint(mx, my):
            attack_menu = False
        return attack_menu, end_menu, menu_enemy, selected_unit, turn, enemy_index, do_attack, do_endturn

    # 2) End-turn menu interaction
    if end_menu:
        if attack_btn.collidepoint(mx, my):
            end_menu = False
            do_endturn = True
        elif cancel_btn.collidepoint(mx, my):
            end_menu = False
        return attack_menu, end_menu, menu_enemy, selected_unit, turn, enemy_index, do_attack, do_endturn

    # 3) Click on player to open end-turn menu
    if turn == "player" and (gx, gy) == (player_unit.x, player_unit.y):
        if selected_unit is player_unit:
            end_menu = True
            attack_btn.topleft = (mx, my)
            cancel_btn.topleft = (mx, my + MENU_H + 5)
        else:
            selected_unit = player_unit
        return attack_menu, end_menu, menu_enemy, selected_unit, turn, enemy_index, do_attack, do_endturn

    # 4) Open attack menu on adjacent enemy click
    if turn == "player" and selected_unit:
        for e in enemy_units:
            if (gx, gy) == (e.x, e.y) and abs(e.x - player_unit.x) + abs(e.y - player_unit.y) <= player_unit.attack_range:
                menu_enemy = e
                attack_menu = True
                attack_btn.topleft = (mx, my)
                cancel_btn.topleft = (mx, my + MENU_H + 5)
                break
        return attack_menu, end_menu, menu_enemy, selected_unit, turn, enemy_index, do_attack, do_endturn

    return attack_menu, end_menu, menu_enemy, selected_unit, turn, enemy_index, do_attack, do_endturn


def draw_menus(surface, font, attack_menu, end_menu):
    """
    Draw the attack and end-turn menus if active.
    """
    if attack_menu:
        # Draw background box
        bbox = attack_btn.union(cancel_btn).inflate(4, 4)
        pygame.draw.rect(surface, (255,255,255), bbox)
        # Draw Attack button
        pygame.draw.rect(surface, (255,0,0), attack_btn)
        surface.blit(font.render("Attack", True, (255,255,255)),
                     (attack_btn.x + 5, attack_btn.y + 5))
        # Draw Cancel button
        pygame.draw.rect(surface, (0,0,0), cancel_btn)
        surface.blit(font.render("Cancel", True, (255,255,255)),
                     (cancel_btn.x + 5, cancel_btn.y + 5))
    if end_menu:
        bbox = attack_btn.union(cancel_btn).inflate(4, 4)
        pygame.draw.rect(surface, (255,255,255), bbox)
        pygame.draw.rect(surface, (255,0,0), attack_btn)
        surface.blit(font.render("End Turn", True, (255,255,255)),
                     (attack_btn.x + 5, attack_btn.y + 5))
        pygame.draw.rect(surface, (0,0,0), cancel_btn)
        surface.blit(font.render("Cancel", True, (255,255,255)),
                     (cancel_btn.x + 5, cancel_btn.y + 5))