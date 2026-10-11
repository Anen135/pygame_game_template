import pygame

from settings import WIDTH, HEIGHT, FPS, TITLE
from game.audio import AudioManager
from game.scenes.menu import MenuScene


class GameApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = AudioManager()
        self.scene = MenuScene(self)

    def change_scene(self, scene):
        self.scene = scene

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
