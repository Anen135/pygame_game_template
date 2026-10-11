import math
import pygame

from settings import WIDTH, HEIGHT
from game import colors
from game.scenes.base import Scene
from game.ui.button import Button


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.title_font = pygame.font.SysFont("segoeui", 62, bold=True)
        self.subtitle_font = pygame.font.SysFont("segoeui", 22)
        self.button_font = pygame.font.SysFont("segoeui", 25, bold=True)
        self.small_font = pygame.font.SysFont("segoeui", 18)
        self.time = 0.0

        bw, bh = 330, 62
        x = WIDTH // 2 - bw // 2
        y = 330
        gap = 78

        self.buttons = [
            Button((x, y, bw, bh), "Играть", self.start_game, self.button_font),
            Button((x, y + gap, bw, bh), "Громкость -", lambda: self.volume(-0.1), self.button_font),
            Button((x, y + gap * 2, bw, bh), "Громкость +", lambda: self.volume(0.1), self.button_font),
            Button((x, y + gap * 3, bw, bh), "Выход", self.app.quit, self.button_font),
        ]

    def start_game(self):
        self.app.audio.play("ui")
        from game.scenes.gameplay import GameplayScene
        self.app.change_scene(GameplayScene(self.app))

    def volume(self, delta):
        self.app.audio.change_volume(delta)
        self.app.audio.play("ui")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()
            elif event.key in (pygame.K_LEFT, pygame.K_MINUS):
                self.volume(-0.1)
            elif event.key in (pygame.K_RIGHT, pygame.K_EQUALS, pygame.K_PLUS):
                self.volume(0.1)

        for button in self.buttons:
            if button.handle_event(event):
                if button.text not in ("Играть", "Выход"):
                    self.app.audio.play("ui")

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill(colors.BG)

        # Decorative moving grid
        grid = 48
        scroll = int((self.time * 16) % grid)
        grid_color = (28, 31, 43)
        for x in range(-grid + scroll, WIDTH, grid):
            pygame.draw.line(surface, grid_color, (x, 0), (x, HEIGHT))
        for y in range(-grid + scroll, HEIGHT, grid):
            pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y))

        glow_center = (
            WIDTH // 2 + int(math.sin(self.time * 0.8) * 100),
            190
        )
        for radius, alpha in ((180, 10), (120, 16), (70, 28)):
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*colors.ACCENT, alpha), (radius, radius), radius)
            surface.blit(glow, glow.get_rect(center=glow_center))

        title = self.title_font.render("PYGAME STARTER", True, colors.TEXT)
        subtitle = self.subtitle_font.render(
            "Готовый каркас для своей 2D-игры",
            True,
            colors.MUTED
        )

        surface.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        surface.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 215)))

        for button in self.buttons:
            button.draw(surface)

        vol = self.small_font.render(
            f"Громкость: {round(self.app.audio.master_volume * 100)}%   •   Enter — старт   •   ESC — выход",
            True,
            colors.MUTED
        )
        surface.blit(vol, vol.get_rect(center=(WIDTH // 2, HEIGHT - 28)))
