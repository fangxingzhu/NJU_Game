import os
import pygame


class MusicManager:
    def __init__(self):
        self.enabled = True
        self.current_music = None
        self.volume = 0.45

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
        except pygame.error:
            print("音乐系统初始化失败")
            self.enabled = False

    def play(self, path, loop=True):
        if not self.enabled:
            return

        if not os.path.exists(path):
            print(f"找不到音乐文件：{path}")
            return

        if self.current_music == path:
            return

        self.current_music = path
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1 if loop else 0)

    def toggle(self):
        self.enabled = not self.enabled

        if self.enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def is_enabled(self):
        return self.enabled