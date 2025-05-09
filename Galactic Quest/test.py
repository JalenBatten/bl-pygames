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

cover_image = pygame.image.load('gameCover.jpg').convert()
cover_image = pygame.transform.scale(cover_image, (800, 600))

def show_cover_screen():
    print("cover screen is loading")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        screen.blit(cover_image, (0, 0))
        pygame.display.update()

show_cover_screen()

font = pygame.font.SysFont("Arial", 30)
clock = pygame.time.Clock()

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

boss_arena_x = 6000
boss_arena_y = HEIGHT - 150
boss_arena = pygame.Rect(boss_arena_x, HEIGHT - 50, 1000, 10)

# Load player sprite image
player_sprite = pygame.image.load('player_sprite.png').convert_alpha()
player_sprite = pygame.transform.scale(player_sprite, (80, 80))

# Load enemy sprite image
enemy_sprite = pygame.image.load('enemy_sprite.png').convert_alpha()
enemy_sprite = pygame.transform.scale(enemy_sprite, (80, 80))

def spawn_power_up():
    x = random.randint(long_platform.left + 10, long_platform.right - 30)
    y = long_platform.top - 20
    kind = random.choice(["health", "speed"])
    return {"rect": pygame.Rect(x, y, 20, 20), "type": kind}

def reset_game():
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT - 150,
        "player_vel_y": 0,
        "player_health": 10,
        "bullets": [],
        "score": 0,
        "enemies": [
            {"rect": pygame.Rect(100, 390, 60, 60), "health": 3, "shooting": False, "last_shot": 0},
            {"rect": pygame.Rect(1500, 240, 60, 60), "health": 2, "shooting": True, "last_shot": 0},
            {"rect": pygame.Rect(2500, 310, 60, 60), "health": 1, "shooting": False, "last_shot": 0},
            {"rect": pygame.Rect(3500, 150, 60, 60), "health": 3, "shooting": True, "last_shot": 0},
            {"rect": pygame.Rect(4500, HEIGHT - 100, 60, 60), "health": 2, "shooting": False, "last_shot": 0},
        ],
        "power_ups": [spawn_power_up(), spawn_power_up()],
        "game_over": False,
        "player_shoot_speed": 500,
        "player_last_damage_time": 0,
        "in_boss_arena": False,
        "boss_arena_entered": False
    }

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

player_w, player_h = 80, 80
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
damage_cooldown = 1000

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
        if keys[pygame.K_w] and state["player_vel_y"] == 0:
            state["player_vel_y"] = player_jump

    state["player_vel_y"] += gravity
    state["player_y"] += state["player_vel_y"]
    player_rect = pygame.Rect(state["player_x"], state["player_y"], player_w, player_h)

    all_platforms = platforms + [long_platform]
    if state["in_boss_arena"]:
        all_platforms.append(boss_arena)

    on_ground = False
    for p in all_platforms:
        if player_rect.colliderect(p) and state["player_vel_y"] > 0:
            state["player_y"] = p.top - player_h
            state["player_vel_y"] = 0
            on_ground = True

    if state["player_y"] > HEIGHT - player_h:
        state["player_y"] = HEIGHT - player_h
        state["player_vel_y"] = 0

    target_x = state["player_x"] + player_w // 2 - WIDTH // 2
    target_y = state["player_y"] + player_h // 2 - HEIGHT // 2
    camera.x += (target_x - camera.x) * camera_smoothness
    camera.y += (target_y - camera.y) * camera_smoothness
    camera.x = max(0, min(camera.x, 7000 - WIDTH))
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
        state["bullets"].append([bx, by, vx, vy, "player"])
        last_shot_player = current_time

    for b in state["bullets"][:]:
        b[0] += b[2]
        b[1] += b[3]
        if b[0] < 0 or b[0] > long_platform.width or b[1] < 0 or b[1] > HEIGHT:
            state["bullets"].remove(b)

    for b in state["bullets"][:]:
        if b[4] == "enemy":
            bullet_rect = pygame.Rect(b[0], b[1], 5, 5)
            if player_rect.colliderect(bullet_rect):
                state["player_health"] -= 2
                state["bullets"].remove(b)
                if state["player_health"] <= 0:
                    state["game_over"] = True

    for b in state["bullets"][:]:
        if b[4] == "player":
            for e in state["enemies"]:
                if pygame.Rect(e["rect"]).collidepoint(b[0], b[1]):
                    e["health"] -= 1
                    state["bullets"].remove(b)
                    if e["health"] <= 0:
                        state["enemies"].remove(e)
                        state["score"] += 1
                    break

    for e in state["enemies"]:
        if e["shooting"]:
            current_time = pygame.time.get_ticks()
        if (e["rect"].x + e["rect"].width > cam_x and e["rect"].x < cam_x + WIDTH and
            e["rect"].y + e["rect"].height > cam_y and e["rect"].y < cam_y + HEIGHT):
            if current_time - e["last_shot"] > 2500:
                ex, ey = e["rect"].center
                angle = math.atan2(state["player_y"] - ey, state["player_x"] - ex)
                vx = bullet_speed * math.cos(angle)
                vy = bullet_speed * math.sin(angle)
                state["bullets"].append([ex, ey, vx, vy, "enemy"])
                e["last_shot"] = current_time

    for e in state["enemies"]:
        e["rect"].y += enemy_gravity
        on_platform = False
        for p in all_platforms:
            if e["rect"].colliderect(p):
                e["rect"].bottom = p.top
                on_platform = True
                break
        if on_platform:
            future_rect = e["rect"].copy()
            future_rect.x += enemy_vel
            future_rect.y += 1
            supported = False
            for p in all_platforms:
                if future_rect.colliderect(p):
                    supported = True
                    break
            if not supported:
                enemy_vel *= -1
        e["rect"].x += enemy_vel
        if e["rect"].left < 0 or e["rect"].right > long_platform.width:
            enemy_vel *= -1

    for power in state["power_ups"]:
        if player_rect.colliderect(power["rect"]):
            if power["type"] == "health":
                state["player_health"] = min(10, state["player_health"] + 2)
            elif power["type"] == "speed":
                state["player_shoot_speed"] = max(100, state["player_shoot_speed"] - 100)
            state["power_ups"].remove(power)
            state["power_ups"].append(spawn_power_up())

    if not state["enemies"] and not state["boss_arena_entered"]:
        state["player_x"] = boss_arena_x + 100
        state["player_y"] = boss_arena_y
        camera.x = boss_arena_x
        state["in_boss_arena"] = True
        state["boss_arena_entered"] = True

    screen.fill(DARK_BLUE)
    for p in all_platforms:
        pygame.draw.rect(screen, BLUE, p.move(-cam_x, -cam_y))
    if state["in_boss_arena"]:
        pygame.draw.rect(screen, BLUE, boss_arena.move(-cam_x, -cam_y))

    screen.blit(player_sprite, player_rect.move(-cam_x, -cam_y))

    for e in state["enemies"]:
        screen.blit(enemy_sprite, e["rect"].move(-cam_x, -cam_y))

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

    for power in state["power_ups"]:
        color = (255, 215, 0) if power["type"] == "health" else (0, 255, 255)
        pygame.draw.rect(screen, color, power["rect"].move(-cam_x, -cam_y))

    pygame.display.flip()