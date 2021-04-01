import pygame
import os
import math
import random
from gamelogic import world
from gamelogic import achievements


class gamestate(object):
    def __init__(self):
        self.players = []
        self.enemies = []
        self.projectiles = []
        self.bosses = []


class player(object):
    jump_right = pygame.image.load(os.path.join("images", "jump.png"))
    jump_left = pygame.transform.flip(jump_right, True, False)
    head_right = pygame.image.load(os.path.join("images", "head.png"))
    head_left = pygame.transform.flip(head_right, True, False)
    body_right = [
        pygame.image.load(os.path.join("images", "body_" + format(x, "03d") + ".png"))
        for x in range(0, 17)
    ]
    body_left = [pygame.transform.flip(x, True, False) for x in body_right]
    bodyspeed = 2

    def __init__(self, x, y):
        self.id = random.getrandbits(64)
        self.x = int(x)
        self.y = int(y)
        self.width = 120
        self.height = 120
        self.head_pos = -20
        self.body_pos = -20
        self.hitbox = 60
        self.jumpCount = 0
        self.runCount = 0
        self.state = "normal"
        self.dir = 0
        self.x_vel = 2
        self.y_vel = 0
        self.ammo = 4
        self.reloadleft = 0
        self.shoottimer = 0
        self.hp = world.PLAYER_HP

    def move(self):
        if self.shoottimer:
            self.shoottimer -= 1
        if self.reloadleft:
            self.reloadleft -= 1
            if self.reloadleft == 0:
                if self.state == "reloading":
                    self.state = "normal"
                self.ammo = 4
        if self.runCount > len(self.body_right) * self.bodyspeed:
            self.runCount = 0
        if not self.dir == 0:
            self.runCount += 1
        self.x += self.dir * self.x_vel
        self.y -= self.y_vel
        self.y_vel -= 0.1
        self.x = min(world.WORLD_SIZE - self.width / 2, self.x)
        self.x = max(0 + self.width / 2, self.x)
        self.y = min(world.FLOOR_POS, self.y)
        if self.y == world.FLOOR_POS:
            self.y_vel = 0
            if self.state == "jumping":
                self.state = "normal"

    def mouseDir(self, camera_pos):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x += camera_pos  # window position to real position
        mouseDir = math.atan2(
            (mouse_x - (self.x)), (mouse_y - (self.y + self.head_pos))
        )
        if mouseDir < 0:
            mouseDir += math.pi * 2
        mouseDir -= math.pi / 2
        return mouseDir

    def draw(self, win, camera_pos, my_id):
        # Draw legs
        if self.state == "jumping":
            if self.dir == -1:
                win.blit(
                    pygame.transform.scale(self.jump_left, (self.width, self.height)),
                    (
                        self.x - camera_pos - self.width / 2 + self.body_pos,
                        self.y - self.height / 2,
                    ),
                )
            else:
                win.blit(
                    pygame.transform.scale(self.jump_right, (self.width, self.height)),
                    (
                        self.x - camera_pos - self.width / 2 - self.body_pos,
                        self.y - self.height / 2,
                    ),
                )
        else:
            if self.dir == -1:
                win.blit(
                    pygame.transform.scale(
                        self.body_left[self.runCount // self.bodyspeed - 1],
                        (self.width, self.height),
                    ),
                    (
                        self.x - camera_pos - self.width / 2 + self.body_pos,
                        self.y - self.height / 2,
                    ),
                )
            else:
                win.blit(
                    pygame.transform.scale(
                        self.body_right[self.runCount // self.bodyspeed - 1],
                        (self.width, self.height),
                    ),
                    (
                        self.x - camera_pos - self.width / 2 - self.body_pos,
                        self.y - self.height / 2,
                    ),
                )

        # Draw head
        if self.mouseDir(camera_pos) > math.pi / 2:
            rotated_head = pygame.transform.rotate(
                self.head_left, self.mouseDir(camera_pos) / math.pi * 180 - 180
            )
            win.blit(
                rotated_head,
                (
                    self.x - camera_pos - rotated_head.get_width() / 2,
                    self.y - rotated_head.get_height() / 2 + self.head_pos,
                ),
            )
        else:
            rotated_head = pygame.transform.rotate(
                self.head_right, self.mouseDir(camera_pos) / math.pi * 180
            )
            win.blit(
                rotated_head,
                (
                    self.x - camera_pos - rotated_head.get_width() / 2,
                    self.y - rotated_head.get_height() / 2 + self.head_pos,
                ),
            )


class boss(object):
    body_right = [
        pygame.image.load(os.path.join("images", "boss_" + str(x) + ".png"))
        for x in range(1, 9)
    ]
    body_left = [pygame.transform.flip(x, True, False) for x in body_right]

    def __init__(self, x, y):
        self.id = random.getrandbits(64)
        self.x = int(x)
        self.y = int(y)
        self.dir = -1
        self.width = 90
        self.height = 90
        self.hitbox = 90
        self.bodyCount = 0
        self.hp = 25
        self.shootdelay = 0

    def move(self):
        if self.bodyCount > 42:
            self.bodyCount = 0
        self.bodyCount += 1
        if self.shootdelay > 0:
            self.shootdelay -= 1

    def draw(self, win, camera_pos):
        if self.dir == -1:
            win.blit(
                self.body_left[self.bodyCount // 6],
                (self.x - camera_pos - self.width / 2, self.y - self.height / 2),
            )
        else:
            win.blit(
                self.body_right[self.bodyCount // 6],
                (self.x - camera_pos - self.width / 2, self.y - self.height / 2),
            )


class enemy(object):
    body_right = [
        pygame.image.load(os.path.join("images", "enemy_" + format(x, "03d") + ".png"))
        for x in range(0, 17)
    ]
    body_left = [pygame.transform.flip(x, True, False) for x in body_right]
    bodyspeed = 2

    def __init__(self, x, y):
        self.id = random.getrandbits(64)
        self.x = int(x)
        self.y = int(y)
        self.width = 140
        self.height = 120
        self.y_pos = random.randint(-40, 40)
        self.hitbox = 40
        self.bodyCount = 0
        self.dir = 0
        self.x_vel = 2
        self.y_vel = 0
        self.hp = 5
        self.shootdelay = 0

    def move(self):
        if random.randint(0, 100) == 0:
            self.dir = random.choice([-1, 0, 1])
        if not self.dir == 0:
            if self.bodyCount > len(self.body_right) * self.bodyspeed:
                self.bodyCount = 0
            self.bodyCount += 1
        if self.shootdelay > 0:
            self.shootdelay -= 1
        self.x += self.dir * self.x_vel
        self.y -= self.y_vel
        self.y_vel -= 0.04
        self.x = min(world.WORLD_SIZE - self.width, self.x)
        self.x = max(1000, self.x)  # Don't let the enemies attack starting players
        self.y = min(world.FLOOR_POS - self.y_pos, self.y)
        if self.y >= (world.FLOOR_POS - self.y_pos):
            self.y_vel = 0

    def draw(self, win, camera_pos):
        if self.dir == -1:
            win.blit(
                pygame.transform.scale(
                    self.body_left[self.bodyCount // self.bodyspeed - 1],
                    (self.width, self.height),
                ),
                (self.x - camera_pos - self.width / 2, self.y - self.height / 2),
            )
        else:
            win.blit(
                pygame.transform.scale(
                    self.body_right[self.bodyCount // self.bodyspeed - 1],
                    (self.width, self.height),
                ),
                (self.x - camera_pos - self.width / 2, self.y - self.height / 2),
            )


class projectile(object):
    projectile_good = [
        pygame.image.load(os.path.join("images", "projectile_good_" + str(x) + ".png"))
        for x in range(1, 13)
    ]
    projectile_good.append(projectile_good.reverse())
    projectile_bad = [
        pygame.image.load(os.path.join("images", "projectile_bad_" + str(x) + ".png"))
        for x in range(1, 13)
    ]

    def __init__(self, x, y, direction, friendly, playerid=None):
        self.id = random.getrandbits(64)
        self.playerid = playerid
        self.x = int(x)
        self.y = int(y)
        self.dir = direction
        self.friendly = friendly
        self.width = 30
        self.height = 30
        self.hitbox = 30
        self.rotateCount = 0
        self.vel = 4
        self.moveremaining = 500

    def draw(self, win, camera_pos):
        if self.friendly:
            win.blit(
                pygame.transform.scale(
                    self.projectile_good[self.rotateCount], (self.width, self.height)
                ),
                (self.x - camera_pos - self.width / 2, self.y - self.height / 2),
            )
        else:
            win.blit(
                pygame.transform.scale(
                    self.projectile_bad[self.rotateCount], (self.width, self.height)
                ),
                (self.x - camera_pos - self.width / 2, self.y - self.height / 2),
            )

    def move(self):
        self.rotateCount += 1
        if self.rotateCount >= 12:
            self.rotateCount = 0
        self.x += math.cos(self.dir) * self.vel
        self.y -= math.sin(self.dir) * self.vel
        self.moveremaining -= 1
