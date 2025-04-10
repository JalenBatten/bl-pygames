import pygame
import sys
import random
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GRAY  = (100, 100, 100)
GREEN = (0, 255, 0)

FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 72)

GRAVITY = 0.5
JUMP_STRENGTH = -10

# Bullet class
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 5, 5)
        angle = math.atan2(target_y - y, target_x - x)
        speed = 8
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, surface, camera_x):
        screen_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, RED, screen_rect)

# Platform class
class Platform:
    def __init__(self, x, y, width, height=20):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, camera_x):
        screen_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, GRAY, screen_rect)

# Enemy class
class Enemy:
    def __init__(self, platform):
        self.rect = pygame.Rect(platform.rect.x + random.randint(0, platform.rect.width - 30), platform.rect.y - 30, 30, 30)
        self.speed = 2
        self.platform = platform
        self.direction = random.choice([-1, 1])
        self.health = 2

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right:
            self.direction *= -1

    def draw(self, surface, camera_x):
        screen_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, GREEN, screen_rect)
        # Draw health bar
        bar_width = self.rect.width
        health_ratio = self.health / 2
        pygame.draw.rect(surface, RED, (screen_rect.x, screen_rect.y - 10, bar_width, 5))
        pygame.draw.rect(surface, GREEN, (screen_rect.x, screen_rect.y - 10, bar_width * health_ratio, 5))

# Player class
class Player:
    def __init__(self, platform):
        self.width = 50
        self.height = 10
        self.rect = pygame.Rect(platform.rect.x + 100, platform.rect.top - self.height, self.width, self.height)
        self.speed = 5
        self.bullets = []
        self.vel_y = 0
        self.on_ground = False
        self.lives = 3
        self.score = 0

    def move(self, keys, platforms):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = JUMP_STRENGTH

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y >= 0:
                if self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def shoot(self, mouse_pos, camera_x):
        if len(self.bullets) < 5:
            world_mouse_x = mouse_pos[0] + camera_x
            world_mouse_y = mouse_pos[1]
            bullet = Bullet(self.rect.centerx, self.rect.centery, world_mouse_x, world_mouse_y)
            self.bullets.append(bullet)

    def update_bullets(self, enemies):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0 or bullet.rect.top > HEIGHT or bullet.rect.right < 0 or bullet.rect.left > 3000:
                self.bullets.remove(bullet)
                continue
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= 1
                    self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        self.score += 100
                    break

    def draw(self, surface, camera_x):
        screen_rect = pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, WHITE, screen_rect)
        for bullet in self.bullets:
            bullet.draw(surface, camera_x)

def draw_game_over(surface, score):
    surface.fill(BLACK)
    game_over_text = BIG_FONT.render("GAME OVER", True, RED)
    score_text = FONT.render(f"Final Score: {score}", True, WHITE)
    retry_text = FONT.render("Press R to Restart", True, WHITE)
    surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 300))
    surface.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, 350))
    pygame.display.flip()

def reset_game():
    global player, enemies, enemy_spawn_timer, running, game_over
    player = Player(platforms[0])
    enemies = []
    enemy_spawn_timer = 0
    running = True
    game_over = False

# Setup
platforms = [
    Platform(0, 500, 2000),
    Platform(400, 400, 100),
    Platform(700, 350, 100),
    Platform(1000, 300, 100),
    Platform(1300, 250, 100),
    Platform(1600, 200, 100),
]
player = Player(platforms[0])
enemies = []
enemy_spawn_timer = 0
ENEMY_SPAWN_DELAY = 2000  # ms
game_over = False

# Game loop
running = True
while True:
    dt = clock.tick(FPS)

    if not game_over:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.move(keys, platforms)

        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            mouse_pos = pygame.mouse.get_pos()
            player.shoot(mouse_pos, camera_x)

        player.update_bullets(enemies)

        # Camera logic
        camera_x = player.rect.centerx - WIDTH // 2
        camera_x = max(0, min(camera_x, platforms[0].rect.width - WIDTH))

        # Enemy spawning
        enemy_spawn_timer += dt
        if enemy_spawn_timer >= ENEMY_SPAWN_DELAY:
            spawn_platform = random.choice(platforms[1:])
            enemies.append(Enemy(spawn_platform))
            enemy_spawn_timer = 0

        for enemy in enemies:
            enemy.update()

        for platform in platforms:
            platform.draw(screen, camera_x)

        player.draw(screen, camera_x)

        for enemy in enemies:
            enemy.draw(screen, camera_x)

        if player.rect.top > HEIGHT + 100:
            player.lives -= 1
            if player.lives <= 0:
                game_over = True
            else:
                player.rect.x = 100
                player.rect.y = platforms[0].rect.top - player.height
                player.vel_y = 0
                player.on_ground = True
                player.bullets.clear()

        score_text = FONT.render(f"Score: {player.score}", True, WHITE)
        lives_text = FONT.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))

        pygame.display.flip()

    else:
        draw_game_over(screen, player.score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()