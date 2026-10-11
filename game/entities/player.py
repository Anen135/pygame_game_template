import pygame

from settings import (
    WIDTH, HEIGHT, PLAYER_SPEED, PLAYER_MAX_HP,
    PLAYER_FIRE_COOLDOWN
)
from game import colors
from game.entities.bullet import Bullet


class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2()
        self.hp = PLAYER_MAX_HP
        self.fire_timer = 0.0
        self.invulnerability = 0.0

        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colors.ACCENT, (24, 24), 21)
        pygame.draw.circle(self.image, colors.WHITE, (24, 24), 9)
        pygame.draw.circle(self.image, colors.BG, (24, 24), 4)
        self.rect = self.image.get_rect(center=self.position)

    @property
    def alive(self):
        return self.hp > 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.velocity = direction * PLAYER_SPEED
        self.position += self.velocity * dt

        margin = 24
        self.position.x = max(margin, min(WIDTH - margin, self.position.x))
        self.position.y = max(margin, min(HEIGHT - margin, self.position.y))

        self.fire_timer = max(0.0, self.fire_timer - dt)
        self.invulnerability = max(0.0, self.invulnerability - dt)

        self.rect.center = round(self.position.x), round(self.position.y)

    def try_shoot(self, target):
        if self.fire_timer > 0 or not self.alive:
            return None

        direction = pygame.Vector2(target) - self.position
        if direction.length_squared() == 0:
            return None

        self.fire_timer = PLAYER_FIRE_COOLDOWN
        return Bullet(self.position, direction)

    def take_damage(self, amount):
        if self.invulnerability > 0 or not self.alive:
            return False

        self.hp = max(0, self.hp - amount)
        self.invulnerability = 0.45
        return True

    def draw(self, surface, offset=(0, 0)):
        image = self.image.copy()

        if self.invulnerability > 0:
            image.set_alpha(120 if int(self.invulnerability * 20) % 2 == 0 else 255)

        rect = image.get_rect(center=(
            self.rect.centerx + offset[0],
            self.rect.centery + offset[1]
        ))
        surface.blit(image, rect)

        mouse = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse - pygame.Vector2(rect.center)
        if direction.length_squared() > 0:
            direction = direction.normalize()
            barrel_start = pygame.Vector2(rect.center) + direction * 15
            barrel_end = pygame.Vector2(rect.center) + direction * 34
            pygame.draw.line(surface, colors.WHITE, barrel_start, barrel_end, 5)
            pygame.draw.circle(surface, colors.WARNING, barrel_end, 4)
