from pathlib import Path
import pygame
from settings import MASTER_VOLUME


class AudioManager:
    def __init__(self):
        self.enabled = True
        self.master_volume = MASTER_VOLUME
        self.sounds = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            self.enabled = False
            return

        sound_dir = Path(__file__).resolve().parent.parent / "assets" / "sounds"
        for name in ("shoot", "hit", "hurt", "ui"):
            path = sound_dir / f"{name}.wav"
            if path.exists():
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error:
                    pass

        self._apply_volume()

    def _apply_volume(self):
        for sound in self.sounds.values():
            sound.set_volume(self.master_volume)

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def set_volume(self, value):
        self.master_volume = max(0.0, min(1.0, value))
        self._apply_volume()

    def change_volume(self, delta):
        self.set_volume(self.master_volume + delta)
