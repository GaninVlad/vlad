import os
import sqlite3
import sys
from sys import exit
from pygame.locals import *
import random
import pygame

screen_width = 480
screen_height = 800


class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, initial_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = initial_position
        self.speed = 10

    def move(self):
        self.rect.top -= self.speed


class Player(pygame.sprite.Sprite):
    def __init__(self, kosmolet_imgs, raketa_player, initial_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = []
        for i in range(len(raketa_player)):
            self.image.append(kosmolet_imgs.subsurface(raketa_player[i]).convert_alpha())
        self.rect = raketa_player[0]
        self.rect.topleft = initial_position
        self.speed = 8
        self.bullets = pygame.sprite.Group()
        self.img_index = 0
        self.is_hit = False

    def shoot(self, bullet_imgs):
        bullet = Bullet(bullet_imgs, self.rect.midtop)
        self.bullets.add(bullet)

    def moveUp(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed

    def moveDown(self):
        if self.rect.top >= screen_height - self.rect.height:
            self.rect.top = screen_height - self.rect.height
        else:
            self.rect.top += self.speed

    def moveLeft(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        else:
            self.rect.left -= self.speed

    def moveRight(self):
        if self.rect.left >= screen_width - self.rect.width:
            self.rect.left = screen_width - self.rect.width
        else:
            self.rect.left += self.speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self, opponent_resource, opponent_down_resources, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = opponent_resource
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = opponent_down_resources
        self.speed = 2
        self.down_index = 0

    def move(self):
        self.rect.top += self.speed


pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Galaga')

vystrel = pygame.mixer.Sound('image/sound/bullet.wav')
player_zvuk = pygame.mixer.Sound('image/sound/opponent1_down.wav')
gameover_zvuk = pygame.mixer.Sound('image/sound/game_over.wav')
vystrel.set_volume(0.3)
player_zvuk.set_volume(0.3)
gameover_zvuk.set_volume(0.3)
pygame.mixer.music.load('image/sound/game_music.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

# loading background image
phon = pygame.image.load('image/image/background.png').convert()
gameover_phon = pygame.image.load('image/image/gameover.png')
filename = 'image/image/aircraft_shooter.png'
enemy_img = 'image/image/enemy_img.png'
kosmolet_img = pygame.image.load(filename)

kosmolet_player = [pygame.Rect(0, 99, 102, 126), pygame.Rect(165, 360, 102, 126), pygame.Rect(165, 234, 102, 126),
                   pygame.Rect(330, 624, 102, 126), pygame.Rect(330, 498, 102, 126), pygame.Rect(432, 624, 102, 126)]
kosmolet_player_pos = [200, 600]
player = Player(kosmolet_img, kosmolet_player, kosmolet_player_pos)

kosmolet_bullet = pygame.Rect(1004, 987, 9, 21)
bullet_img = kosmolet_img.subsurface(kosmolet_bullet)

enemy = pygame.Rect(534, 612, 57, 43)
enemy_imgs = kosmolet_img.subsurface(enemy)
enemy_down_imgs = [kosmolet_img.subsurface(pygame.Rect(267, 347, 57, 43)),
                   kosmolet_img.subsurface(pygame.Rect(873, 697, 57, 43)),
                   kosmolet_img.subsurface(pygame.Rect(267, 296, 57, 43)),
                   kosmolet_img.subsurface(pygame.Rect(930, 697, 57, 43))]

Enemy1 = pygame.sprite.Group()

Enemy_down = pygame.sprite.Group()

vystrel_dist = 0
Enemy_dist = 0

player_index = 16

score = 0

clock = pygame.time.Clock()
paused = False


def load_image(name, colorkey=-1):
    fullname = os.path.join('image/image', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


FPS = 50


def start_screen():
    intro_text = ["Rules:",
                  "Go up: W",
                  "Go down: S",
                  "Go left: A",
                  "Go right: D",
                  "Pause: Esc"]
    fon = pygame.transform.scale(load_image('galaga_fon.png'), (screen_width, screen_height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 0
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('yellow'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()


def game():
    kosmolet_player = [pygame.Rect(0, 99, 102, 126), pygame.Rect(165, 360, 102, 126), pygame.Rect(165, 234, 102, 126),
                       pygame.Rect(330, 624, 102, 126), pygame.Rect(330, 498, 102, 126),
                       pygame.Rect(432, 624, 102, 126)]
    kosmolet_player_pos = [200, 600]
    player = Player(kosmolet_img, kosmolet_player, kosmolet_player_pos)
    global player_index, score, vystrel_dist, Enemy_dist, paused
    run = True
    while run:
        clock.tick(60)
        if not player.is_hit:
            if vystrel_dist % 15 == 0:
                vystrel.play()
                player.shoot(bullet_img)
            vystrel_dist += 1
            if vystrel_dist >= 15:
                vystrel_dist = 0

        if vystrel_dist % 50 == 0:
            Enemy1_pos = [random.randint(0, screen_width - enemy.width), 0]
            Enemys1 = Enemy(enemy_imgs, enemy_down_imgs, Enemy1_pos)
            Enemy1.add(Enemys1)
        Enemy_dist += 1
        if Enemy_dist >= 100:
            Enemy_dist = 0

        for bullet in player.bullets:
            bullet.move()
            if bullet.rect.bottom < 0:
                player.bullets.remove(bullet)

        for i in Enemy1:
            i.move()
            if pygame.sprite.collide_circle(i, player):
                Enemy_down.add(i)
                Enemy1.remove(i)
                player.is_hit = True
                gameover_zvuk.play()
                break
            if i.rect.top > screen_height:
                Enemy1.remove(i)

        Enemy1_DOWN = pygame.sprite.groupcollide(Enemy1, player.bullets, 1, 1)
        for i in Enemy1_DOWN:
            Enemy_down.add(i)

        screen.fill(0)
        screen.blit(phon, (0, 0))

        if not player.is_hit:
            screen.blit(player.image[player.img_index], player.rect)
            player.img_index = vystrel_dist // 8
        else:
            player.img_index = player_index // 8
            screen.blit(player.image[player.img_index], player.rect)
            player_index += 1
            if player_index > 47:
                run = False
                screen.blit(gameover_phon, (0, 0))
                font = pygame.font.Font(None, 60)
                txt2 = font.render('Press LMB to restart', True, (255, 255, 0))
                txt = font.render('Score: ' + str(score), True, (255, 255, 0))
                a = txt2.get_rect()
                txt_kosmolet = txt.get_rect()
                txt_kosmolet.centery = 70
                screen.blit(gameover_phon, (0, 0))
                screen.blit(txt, txt_kosmolet)
                screen.blit(txt2, a)
                Enemy1.empty()

        for i in Enemy_down:
            if i.down_index == 0:
                player_zvuk.play()
            if i.down_index > 7:
                Enemy_down.remove(i)
                score += 1000
                continue
            screen.blit(i.down_imgs[i.down_index // 2], i.rect)
            i.down_index += 1

        player.bullets.draw(screen)
        Enemy1.draw(screen)

        score_font = pygame.font.Font(None, 36)
        score_txt = score_font.render(str(score), True, (255, 255, 0))
        kosmolet_txt = score_txt.get_rect()
        kosmolet_txt.topleft = [10, 10]
        screen.blit(score_txt, kosmolet_txt)
        pygame.display.update()
        key_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if not player.is_hit:
            if key_pressed[K_w] or key_pressed[K_UP]:
                player.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                player.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                player.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                player.moveRight()


game()
con = sqlite3.connect("project.db")
cur = con.cursor()
result = cur.execute(f"SELECT record FROM Record").fetchall()
if score > result[0][-1]:
    cur.execute('DELETE FROM Record')
    res = cur.execute(f"INSERT INTO Record(record) VALUES('{score}')").fetchall()
con.commit()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.display.set_mode((480, 800))
            player_index = 16
            player.is_hit = False
            player = Player(kosmolet_img, kosmolet_player, kosmolet_player_pos)
            score = 0
            Enemy1.empty()
            game()
    pygame.display.flip()
    clock.tick(60)
    pygame.display.update()