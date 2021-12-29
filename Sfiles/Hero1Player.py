import pygame
from CBullet import Bullet
from hero1e import Hero1AtackE
from map_preparation_settings import level1_map


class Player_hero1(pygame.sprite.Sprite):
    def __init__(self, pos, player_settings):
        super().__init__()
        self.block_moving = False

        HEIGHT = pygame.display.Info().current_h
        WIDTH = pygame.display.Info().current_w
        self.name = player_settings['name']
        self.power = player_settings['attack power']
        self.maxHp = player_settings['maxHp']
        self.hp = player_settings['maxHp']
        self.started_pos = pos

        self.bullets = pygame.sprite.Group()
        self.attacksE = pygame.sprite.Group()

        self.K_x = False
        self.attacksEBool = 300
        self.current_sprite = 0

        self.Q_ACTIVE = False
        self.Q_ACTIVE_TIMER = 600
        self.q_side = 'q_right_animation'
        self.Q_SLEEPER = self.Q_ACTIVE_TIMER * 3

        re_size = (HEIGHT / len(level1_map)) / 64
        self.width = round(player_settings['width'] * re_size) - 1
        self.height = round(player_settings['height'] * re_size) - 1
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.images = {}
        for el in player_settings['animations'].keys():
            self.images[el] = []
            for i in range(1, 15):
                image = pygame.transform.scale(
                    pygame.image.load(f'{player_settings["animations"][el]}{i}.png').convert_alpha(),
                    (self.width, self.height))
                self.images[el].append(image)

        self.image.blit(pygame.transform.scale(player_settings['imagePreview'], (self.width, self.height)), (0, 0))
        self.rect = self.image.get_rect(topleft=pos)
        self.direction = pygame.math.Vector2(0, 0)
        self.control_speed = round(7 * WIDTH / 1440)
        self.speed = round(7 * WIDTH / 1440)
        self.gravity = 0.8 * HEIGHT / 900
        self.jump_speed = -18 * HEIGHT / 900
        self.jump_bool = True
        self.shoot_bool = 1
        self.interface_mode = False

        self.server_player = None
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def get_input(self):
        self.Q_SLEEPER += 1
        self.current_sprite += 0.25
        keys = pygame.key.get_pressed()

        if keys[pygame.K_x]:
            self.K_x = True
        else:
            self.K_x = False

        if self.Q_ACTIVE:
            self.Q_ACTIVE_TIMER += 1
            self.image.fill((0, 0, 0, 0))
            self.image.blit(self.images[self.q_side][int(self.current_sprite)], (0, 0))
            if self.Q_ACTIVE_TIMER >= 600:
                self.Q_ACTIVE = False
                self.image.fill((0, 0, 0, 0))
                self.image.blit(self.images['right_walk'][int(self.current_sprite)], (0, 0))
                self.speed = self.control_speed
                self.power /= 1.5
                if self.server_player:
                    self.server_player.Q = False
                    self.server_player.power /= 1.5

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.q_side = 'q_right_animation'
            if not self.Q_ACTIVE:
                self.image.fill((0, 0, 0, 0))
                self.image.blit(self.images['right_walk'][int(self.current_sprite)], (0, 0))
            if self.server_player:
                self.server_player.direction_x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.q_side = 'q_left_animation'
            if not self.Q_ACTIVE:
                self.image.fill((0, 0, 0, 0))
                self.image.blit(self.images['left_walk'][int(self.current_sprite)], (0, 0))
            if self.server_player:
                self.server_player.direction_x = -1
        else:
            self.direction.x = 0
            if self.server_player:
                self.server_player.direction_x = 0

        if keys[pygame.K_SPACE]:
            if self.jump_bool:
                self.jump()
        if not self.direction.y:
            self.jump_bool = True

        if self.server_player:
            if self.server_player.simpleAttack:
                self.server_player.simpleAttack = False

        if pygame.mouse.get_pressed()[0]:
            if self.shoot_bool >= 1:
                self.bullets.add(self.create_bullet())
                if self.server_player:
                    self.server_player.simpleAttack = True
                    self.server_player.mouse_pos_x, self.server_player.mouse_pos_y = pygame.mouse.get_pos()

        if keys[pygame.K_e]:
            if self.attacksEBool >= 300:
                self.attacksE.add(Hero1AtackE(self.rect.midbottom))
                self.attacksEBool = 0
                if self.server_player:
                    self.server_player.E = True
        if keys[pygame.K_q]:
            if self.Q_SLEEPER >= 1800:
                self.Q_ACTIVE = True
                self.Q_ACTIVE_TIMER = 0
                self.current_sprite = 0
                self.Q_SLEEPER = 0
                self.speed *= 1.3
                self.power *= 1.5
                if self.hp <= self.maxHp - 10:
                    self.hp += 10
                else:
                    self.hp = self.maxHp
                if self.server_player:
                    self.server_player.Q = True
                    self.server_player.power *= 1.5
                    if self.server_player.hp <= self.server_player.maxHp - 10:
                        self.server_player.hp += 10
                    else:
                        self.server_player.hp = self.server_player.maxHp

        if self.current_sprite >= 13:
            self.current_sprite = 0

    def create_bullet(self):
        self.shoot_bool = 0
        return Bullet((self.rect.centerx + 10, self.rect.centery - self.height / 4))

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.jump_bool = False
        self.direction.y = self.jump_speed

    def update(self):
        if not self.interface_mode:
            self.shoot_bool += 0.1
            self.attacksEBool += 1
        if not self.block_moving:
            self.get_input()

    def initialize_server_player(self, server_player):
        self.server_player = server_player
        self.server_player.hp = self.hp
        self.server_player.maxHp = self.maxHp
        self.server_player.power = self.power

    def update_server(self):
        self.server_player.x = (self.rect.x / self.WIDTH) * 1920
        self.server_player.y = (self.rect.y / self.HEIGHT) * 1080
