import pygame
from src.config import Scene, font1_path


class StartScreen:
    def __init__(self):
        self.font = pygame.font.Font(font1_path, 60)
        self.prompt_font = pygame.font.Font(font1_path, 24)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return Scene.OVERWORLD  # 按空格进入大地图
        return None  # 不切换场景

    def draw(self, screen):
        screen.fill((0, 0, 0))  # 黑色背景
        title = self.font.render("NJU_RPG", True, (255, 255, 255))
        prompt = self.prompt_font.render("按空格键开始游戏", True, (200, 200, 200))
        #标题完全居中
        title_x = (screen.get_width() - title.get_width()) // 2
        title_y = ((screen.get_height() - title.get_height()) // 2 ) - 50
        screen.blit(title, (title_x, title_y))
        #提示词稍微置于标题下方
        prompt_x = (screen.get_width() - prompt.get_width()) // 2
        prompt_y = title_y + title.get_height() + 30
        screen.blit(prompt, (prompt_x, prompt_y))
