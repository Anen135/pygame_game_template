import random
import pygame

from settings import (
    WIDTH, HEIGHT, PLAYER_MAX_HP, BULLET_DAMAGE,
    ENEMY_CONTACT_DAMAGE, ENEMY_SPAWN_INTERVAL
)
from game import colors
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.scenes.base import Scene


class GameplayScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.font = pygame.font.SysFont("segoeui", 21, bold=True)
        self.big_font = pygame.font.SysFont("segoeui", 52, bold=True)
        self.small_font = pygame.font.SysFont("segoeui", 17)

        self.player = Player((WIDTH / 2, HEIGHT / 2))
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.spawn_timer = 0.45
        self.score = 0
        self.elapsed = 0.0
        self.paused = False
        self.game_over = False
        self.shake = 0.0

    def restart(self):
        self.app.change_scene(GameplayScene(self.app))

    def back_to_menu(self):
        self.app.audio.play("ui")
        from game.scenes.menu import MenuScene
        self.app.change_scene(MenuScene(self.app))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_over:
                    self.back_to_menu()
                else:
                    self.paused = not self.paused
                    self.app.audio.play("ui")
            elif event.key == pygame.K_r and self.game_over:
                self.restart()

        if self.paused or self.game_over:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            bullet = self.player.try_shoot(event.pos)
            if bullet:
                self.bullets.add(bullet)
                self.app.audio.play("shoot")

    def update(self, dt):
        if self.paused or self.game_over:
            return

        self.elapsed += dt
        self.shake = max(0.0, self.shake - dt * 16)

        self.player.update(dt)

        if pygame.mouse.get_pressed()[0]:
            bullet = self.player.try_shoot(pygame.mouse.get_pos())
            if bullet:
                self.bullets.add(bullet)
                self.app.audio.play("shoot")

        self.bullets.update(dt)
        self.enemies.update(dt)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = max(0.28, ENEMY_SPAWN_INTERVAL - self.elapsed * 0.002)
            self.enemies.add(Enemy(Enemy.random_spawn(), self.player))

        # Bullets vs enemies
        collisions = pygame.sprite.groupcollide(
            self.enemies,
            self.bullets,
            False,
            True
        )
        for enemy, bullets in collisions.items():
            damage = BULLET_DAMAGE * len(bullets)
            killed = enemy.take_damage(damage)
            self.app.audio.play("hit")
            if killed:
                self.score += 100

        # Player vs enemies
        touching = pygame.sprite.spritecollide(
            self.player,
            self.enemies,
            False,
            pygame.sprite.collide_circle
        )
        if touching and self.player.take_damage(ENEMY_CONTACT_DAMAGE):
            self.app.audio.play("hurt")
            self.shake = 8.0

            for enemy in touching:
                push = enemy.position - self.player.position
                if push.length_squared() > 0:
                    enemy.position += push.normalize() * 35

        if not self.player.alive:
            self.game_over = True

    def _camera_offset(self):
        if self.shake <= 0:
            return 0, 0
        amount = int(self.shake)
        return random.randint(-amount, amount), random.randint(-amount, amount)

    def draw(self, surface):
        surface.fill(colors.BG)

        # Background grid
        for x in range(0, WIDTH, 64):
            pygame.draw.line(surface, (25, 28, 39), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 64):
            pygame.draw.line(surface, (25, 28, 39), (0, y), (WIDTH, y))

        offset = self._camera_offset()

        for bullet in self.bullets:
            rect = bullet.rect.move(offset)
            surface.blit(bullet.image, rect)

        for enemy in self.enemies:
            rect = enemy.rect.move(offset)
            surface.blit(enemy.image, rect)

        self.player.draw(surface, offset)

        self._draw_hud(surface)

        if self.paused:
            self._draw_overlay(surface, "ПАУЗА", "ESC — продолжить")
        elif self.game_over:
            self._draw_overlay(
                surface,
                "ИГРА ОКОНЧЕНА",
                f"Счёт: {self.score}   •   R — заново   •   ESC — меню"
            )

    def _draw_hud(self, surface):
        panel = pygame.Rect(18, 18, 360, 92)
        pygame.draw.rect(surface, colors.PANEL, panel, border_radius=14)

        hp_label = self.small_font.render("HP", True, colors.MUTED)
        surface.blit(hp_label, (34, 33))

        hp_bg = pygame.Rect(70, 35, 285, 18)
        pygame.draw.rect(surface, (58, 61, 76), hp_bg, border_radius=9)

        ratio = self.player.hp / PLAYER_MAX_HP
        hp_fill = hp_bg.copy()
        hp_fill.width = int(hp_bg.width * ratio)
        if hp_fill.width > 0:
            pygame.draw.rect(
                surface,
                colors.GOOD if ratio > 0.35 else colors.DANGER,
                hp_fill,
                border_radius=9
            )

        score_text = self.font.render(f"Счёт: {self.score}", True, colors.TEXT)
        time_text = self.small_font.render(f"{self.elapsed:05.1f} сек.", True, colors.MUTED)
        surface.blit(score_text, (34, 67))
        surface.blit(time_text, (270, 71))

        hint = self.small_font.render(
            "WASD — движение   •   ЛКМ — огонь   •   ESC — пауза",
            True,
            colors.MUTED
        )
        surface.blit(hint, (WIDTH - hint.get_width() - 20, 24))

    def _draw_overlay(self, surface, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))

        card = pygame.Rect(0, 0, 620, 220)
        card.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(surface, colors.PANEL, card, border_radius=22)
        pygame.draw.rect(surface, colors.PANEL_ALT, card, 2, border_radius=22)

        title_img = self.big_font.render(title, True, colors.TEXT)
        sub_img = self.font.render(subtitle, True, colors.MUTED)
        surface.blit(title_img, title_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 32)))
        surface.blit(sub_img, sub_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 45)))
