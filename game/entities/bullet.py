import pygame
from settings import BULLET_SPEED
from game import colors


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(direction)
        if self.velocity.length_squared() == 0:
            self.velocity = pygame.Vector2(1, 0)
        self.velocity = self.velocity.normalize() * BULLET_SPEED

        self.radius = 5
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colors.WARNING, (8, 8), self.radius)
        pygame.draw.circle(self.image, colors.WHITE, (8, 8), 2)
        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = round(self.position.x), round(self.position.y)

        screen = pygame.display.get_surface()
        if screen and not screen.get_rect().inflate(120, 120).colliderect(self.rect):
            self.kill()
