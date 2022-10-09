34#author: capybaraaa
#date: July 21, 2022
#version: 1.0

import pygame
import random
import time
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Design 4")
BACKGROUND = pygame.transform.scale(pygame.image.load('assets/background_image2.jpeg'), (WIDTH, HEIGHT))
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 75, 75
SPACESHIP_ASSET = pygame.transform.scale(pygame.image.load('assets/spaceship.png'),(SPACESHIP_WIDTH,SPACESHIP_HEIGHT))
RED_ENEMY = pygame.transform.scale(pygame.image.load('assets/red_enemy.png'),(SPACESHIP_WIDTH,SPACESHIP_HEIGHT))
RED_ENEMY2 = pygame.transform.scale(pygame.image.load('assets/red_enemy2.png'),(SPACESHIP_WIDTH,SPACESHIP_HEIGHT))
BLUE_ENEMY = pygame.transform.scale(pygame.image.load('assets/blue_enemy.png'),(SPACESHIP_WIDTH,SPACESHIP_HEIGHT))
BLUE_ENEMY2 = pygame.transform.scale(pygame.image.load('assets/blue_enemy2.png'),(SPACESHIP_WIDTH,SPACESHIP_HEIGHT))
PLAYER_BULLET = pygame.transform.scale(pygame.image.load('assets/bullet.png'),(30, 45))
ENEMY_BULLET = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('assets/enemy_bullet.png'),(30, 45)), 180)
FPS = 60
WHITE = (255, 255, 255)


class Ship:
    COOLDOWN = 5
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x+22, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x,y,health)
        self.ship_img = SPACESHIP_ASSET
        self.laser_img = PLAYER_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 10
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        self.score += 100
    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x,self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
class Enemy(Ship):
    COLOR_MAP = {"red": (RED_ENEMY, ENEMY_BULLET), "red2":(RED_ENEMY2, ENEMY_BULLET), "blue":(BLUE_ENEMY, ENEMY_BULLET), "blue2":(BLUE_ENEMY2, ENEMY_BULLET)}
    def __init__(self, x, y, color, health=100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img,(self.x,self.y))
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return not(self.y <= height and self.y >=0)
    def collision(self, obj):
        return collide(obj, self)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    run = True
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    won = False
    won_count = 0
    main_font = pygame.font.SysFont("arial", 50)
    lost_font = pygame.font.SysFont("arial", 60)
    enemies = []
    wave_length = 5
    player_vel = 5
    enemy_vel = 4
    laser_vel = 8
    level = 0
    lives = 5
    player = Player(365, 450)
    def draw_window():
        WIN.blit(BACKGROUND, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, WHITE)
        level_label = main_font.render(f"Level: {level}", 1, WHITE)
        score_label = main_font.render(f"Score: {player.score}", 1, WHITE)
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (10, 70))
        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)
        if lost:
            lost_label = lost_font.render(f"You Lost! Score: {player.score}", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH//2 - lost_label.get_width()//2, 350))
        if won:
            won_label = lost_font.render(f"You Won! Score: {player.score}", 1, (255, 255, 255))
            WIN.blit(won_label, (WIDTH // 2 - won_label.get_width() // 2, 350))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        draw_window()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1250, -100), random.choice(["red", "red2", "blue", "blue2"]))
                enemies.append(enemy)
        if level >= 12:
            won = True
            won_count += 1
        if won:
            if won_count > FPS *3:
                run = False
            else:
                continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0, 4*60) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(-laser_vel, enemies)
    main_menu()

def main_menu():
    title_font = pygame.font.SysFont("arial", 70)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Game Prototype by Capy", 1, WHITE)
        start_label = title_font.render("Click anywhere to begin", 1, WHITE)
        WIN.blit(title_label, (WIDTH//2 - title_label.get_width()//2, 450))
        WIN.blit(start_label, (WIDTH // 2 - start_label.get_width() // 2, 550))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                main()
    exit()


if __name__ == "__main__":
    main_menu()