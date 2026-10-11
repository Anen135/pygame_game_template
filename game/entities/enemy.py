import random
import pygame

from settings import WIDTH, HEIGHT, ENEMY_MIN_SPEED, ENEMY_MAX_SPEED
from game import colors


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.target = target
        self.speed = random.uniform(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)
        self.hp = 50
        self.radius = random.randint(18, 25)

        size = self.radius * 2 + 8
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2

        pygame.draw.circle(self.image, colors.DANGER, (center, center), self.radius)
        pygame.draw.circle(self.image, colors.BG, (center - 7, center - 4), 4)
        pygame.draw.circle(self.image, colors.BG, (center + 7, center - 4), 4)
        pygame.draw.arc(
            self.image,
            colors.BG,
            pygame.Rect(center - 10, center + 1, 20, 12),
            0.2, 2.95, 3
        )

        self.rect = self.image.get_rect(center=self.position)

    @staticmethod
    def random_spawn():
        side = random.randrange(4)
        pad = 50

        if side == 0:
            return random.randrange(WIDTH), -pad
        if side == 1:
            return WIDTH + pad, random.randrange(HEIGHT)
        if side == 2:
            return random.randrange(WIDTH), HEIGHT + pad
        return -pad, random.randrange(HEIGHT)

    def update(self, dt):
        if not self.target.alive:
            return

        direction = self.target.position - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed * dt

        self.rect.center = round(self.position.x), round(self.position.y)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            return True
        return False
