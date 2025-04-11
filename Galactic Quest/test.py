import pygame
import math
import sys
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer - Game Over Menu")
WHITE, BLUE, RED = (255, 255, 255), (0, 0, 255), (255, 0, 0)
DARK_BLUE, GREEN, BLACK = (30, 30, 60), (0, 255, 0), (0, 0, 0)
FPS = 60
font = pygame.font.SysFont("Arial", 30)

clock = pygame.time.Clock()

def spawn_power_up():
    # Only spawn power-up on the long platform
    x = random.randint(long_platform.left + 10, long_platform.right - 30)
    y = long_platform.top - 20  # Make sure it's just above the platform
    power_up_rect = pygame.Rect(x, y, 20, 20)
    return power_up_rect

def reset_game():
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT - 150,
        "player_vel_y": 0,
        "player_health": 10,
        "bullets": [],
        "score": 0,
        "enemies": [
            {"rect": pygame.Rect(100, 390, 40, 40), "health": 3, "shooting": False, "last_shot": 0},
            {"rect": pygame.Rect(1500, 240, 40, 40), "health": 2, "shooting": True, "last_shot": 0},
            {"rect": pygame.Rect(2500, 310, 40, 40), "health": 1, "shooting": False, "last_shot": 0},
            {"rect": pygame.Rect(3500, 150, 40, 40), "health": 3, "shooting": True, "last_shot": 0},
            {"rect": pygame.Rect(4500, HEIGHT - 100, 40, 40), "health": 2, "shooting": False, "last_shot": 0},
        ],
        "power_up": spawn_power_up(),
        "game_over": False,
        "player_shoot_speed": 500,  # Time interval in milliseconds
        "player_last_damage_time": 0,
    }

platform_w, platform_h = 100, 10
long_platform = pygame.Rect(0, HEIGHT - 50, 5000, platform_h)
platforms = [
    pygame.Rect(100, 400, platform_w, platform_h),
    pygame.Rect(300, 350, platform_w, platform_h),
    pygame.Rect(500, 300, platform_w, platform_h),
    pygame.Rect(700, 250, platform_w, platform_h),
    pygame.Rect(900, 200, platform_w, platform_h),
    pygame.Rect(1500, 250, platform_w, platform_h),
    pygame.Rect(2000, 150, platform_w, platform_h),
    pygame.Rect(2500, 300, platform_w, platform_h),
    pygame.Rect(3000, 250, platform_w, platform_h),
    pygame.Rect(3500, 150, platform_w, platform_h),
    pygame.Rect(4000, 200, platform_w, platform_h)
]

def draw_button(text, x, y, w, h, hover, screen):
    color = (200, 50, 50) if hover else (150, 0, 0)
    pygame.draw.rect(screen, color, (x, y, w, h))
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2)
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + w//2 - label.get_width()//2, y + h//2 - label.get_height()//2))

def game_over_screen():
    while True:
        screen.fill((20, 20, 30))
        mx, my = pygame.mouse.get_pos()
        try_again_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50)
        quit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)

        draw_button("Try Again", try_again_rect.x, try_again_rect.y, 200, 50, try_again_rect.collidepoint(mx, my), screen)
        draw_button("Quit", quit_rect.x, quit_rect.y, 200, 50, quit_rect.collidepoint(mx, my), screen)

        over_text = font.render("Game Over", True, RED)
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if try_again_rect.collidepoint(mx, my):
                    return reset_game()
                elif quit_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

state = reset_game()

player_w, player_h = 50, 50
player_vel = 5
player_jump = -15
gravity = 0.8
camera_smoothness = 0.1
bullet_speed = 10
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
enemy_vel = 2
enemy_gravity = 0.5

running = True
last_shot_player = 0

knockback_strength = 17
damage_cooldown = 1000  # 1 second in milliseconds

while running:
    clock.tick(FPS)
    if state["game_over"]:
        state = game_over_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if not state["game_over"]:
        if keys[pygame.K_a]:
            state["player_x"] -= player_vel
        if keys[pygame.K_d]:
            state["player_x"] += player_vel

        # Jumping with W key
        if keys[pygame.K_w]:
            # Only allow jump if on ground
            if state["player_vel_y"] == 0:  # Ensure player is on the ground before jumping
                state["player_vel_y"] = player_jump  # Apply jump velocity

    # Apply gravity to the player
    state["player_vel_y"] += gravity  # Gravity pulls the player down

    # Update player's vertical position
    state["player_y"] += state["player_vel_y"]

    player_rect = pygame.Rect(state["player_x"], state["player_y"], player_w, player_h)

    # Handle collision with platforms
    on_ground = False
    for p in platforms + [long_platform]:
        if player_rect.colliderect(p) and state["player_vel_y"] > 0:
            state["player_y"] = p.top - player_h  # Player lands on top of platform
            state["player_vel_y"] = 0  # Reset vertical velocity to zero when landing
            on_ground = True

    # Prevent the player from falling below the ground
    if player_rect.colliderect(long_platform) and state["player_vel_y"] > 0:
        state["player_y"] = long_platform.top - player_h  # Snap to the platform top
        state["player_vel_y"] = 0  # Stop falling

    # Optional: If the player is still in the air and has a negative velocity (jumping/falling)
    if state["player_y"] > HEIGHT - player_h:
        state["player_y"] = HEIGHT - player_h  # Stop at the bottom of the screen
        state["player_vel_y"] = 0  # Reset velocity if hitting the floor

    target_x = state["player_x"] + player_w // 2 - WIDTH // 2
    target_y = state["player_y"] + player_h // 2 - HEIGHT // 2
    camera.x += (target_x - camera.x) * camera_smoothness
    camera.y += (target_y - camera.y) * camera_smoothness
    camera.x = max(0, min(camera.x, 5000 - WIDTH))
    camera.y = max(0, min(camera.y, HEIGHT - HEIGHT))
    cam_x, cam_y = int(camera.x), int(camera.y)

    mx, my = pygame.mouse.get_pos()
    mx += cam_x
    my += cam_y

    current_time = pygame.time.get_ticks()
    if not state["game_over"] and pygame.mouse.get_pressed()[0] and current_time - last_shot_player > state["player_shoot_speed"]:
        bx = state["player_x"] + player_w // 2
        by = state["player_y"] + player_h // 2
        angle = math.atan2(my - by, mx - bx)
        vx = bullet_speed * math.cos(angle)
        vy = bullet_speed * math.sin(angle)
        state["bullets"].append([bx, by, vx, vy])
        last_shot_player = current_time

    for b in state["bullets"][:]:
        b[0] += b[2]
        b[1] += b[3]
        if b[0] < 0 or b[0] > long_platform.width or b[1] < 0 or b[1] > HEIGHT:
            state["bullets"].remove(b)

    # Bullet Collision with Enemies
    for b in state["bullets"][:]:
        if isinstance(b[3], dict) and b[3].get("source") == "enemy":
            if player_rect.colliderect(pygame.Rect(b[0], b[1], 5, 5)):
                state["player_health"] -= 2
                state["bullets"].remove(b)
                if state["player_health"] <= 0:
                    state["game_over"] = True
                break

    # Bullet collision with enemies and health deduction
    for b in state["bullets"][:]:
        for e in state["enemies"]:
            if b[0] > e["rect"].left and b[0] < e["rect"].right and b[1] > e["rect"].top and b[1] < e["rect"].bottom:
                e["health"] -= 1
                state["bullets"].remove(b)
                if e["health"] <= 0:
                    state["enemies"].remove(e)
                    state["score"] += 1
                break

    for e in state["enemies"]:
        if e["shooting"]:
            current_time = pygame.time.get_ticks()
            if current_time - e["last_shot"] > 1000:
                ex, ey = e["rect"].center
                angle = math.atan2(state["player_y"] - ey, state["player_x"] - ex)
                vx = bullet_speed * math.cos(angle)
                vy = bullet_speed * math.sin(angle)
                state["bullets"].append([ex, ey, vx, vy, {"source": "enemy"}])
                e["last_shot"] = current_time

    for e in state["enemies"]:
        if e["rect"].colliderect(player_rect):
            if state["player_health"] > 0 and (pygame.time.get_ticks() - state["player_last_damage_time"] > damage_cooldown):
                state["player_health"] -= 2
                state["player_last_damage_time"] = pygame.time.get_ticks()

                if state["player_x"] < e["rect"].x:
                    state["player_x"] -= knockback_strength
                else:
                    state["player_x"] += knockback_strength

            if state["player_health"] <= 0:
                state["game_over"] = True

    for e in state["enemies"]:
        e["rect"].y += enemy_gravity
        for p in platforms + [long_platform]:
            if e["rect"].colliderect(p):
                e["rect"].bottom = p.top
                break
        e["rect"].x += enemy_vel
        if e["rect"].left < 0 or e["rect"].right > long_platform.width:
            enemy_vel *= -1

    screen.fill(DARK_BLUE)
    for p in platforms + [long_platform]:
        pygame.draw.rect(screen, BLUE, p.move(-cam_x, -cam_y))
    pygame.draw.rect(screen, RED, player_rect.move(-cam_x, -cam_y))

    for e in state["enemies"]:
        pygame.draw.rect(screen, GREEN, e["rect"].move(-cam_x, -cam_y))

    for b in state["bullets"]:
        pygame.draw.circle(screen, WHITE, (int(b[0] - cam_x), int(b[1] - cam_y)), 5)

    score_text = font.render(f"Score: {state['score']}", True, WHITE)
    screen.blit(score_text, (10, 10))

    for i in range(10):
        heart_x = 10 + i * 30
        heart_y = 50
        if i < state["player_health"]:
            pygame.draw.circle(screen, RED, (heart_x, heart_y), 10)
        else:
            pygame.draw.circle(screen, (100, 0, 0), (heart_x, heart_y), 10, 2)

    pygame.draw.rect(screen, (255, 215, 0), state["power_up"].move(-cam_x, -cam_y))

    pygame.display.flip()