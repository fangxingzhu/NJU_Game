import pygame

from src.config import Scene, font1_path
from src.ui import get_ui_font


class StartScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(font1_path, 60)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return Scene.SELECT  # 按空格进入大地图
        return None  # 不切换场景

    def draw(self, screen):
        screen.fill((0, 0, 0))
        title = self.title_font.render("NJU_RPG", True, (255, 255, 255))
        title_x = (screen.get_width() - title.get_width()) // 2
        screen.blit(title, (title_x, 180))

        prompt = get_ui_font(24).render("按任意键进入存档界面", True, (220, 220, 220))
        prompt_x = (screen.get_width() - prompt.get_width()) // 2
        screen.blit(prompt, (prompt_x, 330))
