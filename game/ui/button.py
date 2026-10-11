import pygame
from game import colors


class Button:
    def __init__(self, rect, text, callback, font, *, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.enabled = enabled
        self.hovered = False

    def handle_event(self, event):
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True

        return False

    def draw(self, surface):
        if not self.enabled:
            fill = (48, 50, 60)
            text_color = (100, 105, 120)
        elif self.hovered:
            fill = colors.ACCENT_2
            text_color = colors.WHITE
        else:
            fill = colors.PANEL_ALT
            text_color = colors.TEXT

        pygame.draw.rect(surface, fill, self.rect, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255, 25), self.rect, 1, border_radius=12)

        text = self.font.render(self.text, True, text_color)
        surface.blit(text, text.get_rect(center=self.rect.center))
