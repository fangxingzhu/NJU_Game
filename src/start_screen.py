import os
import math
import pygame
from src.config import Scene, font1_path
from src.ui import get_ui_font


class StartScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(font1_path, 60)
        self.subtitle_font = get_ui_font(24)
        self.prompt_font = get_ui_font(22)

        self.bg_paths = [
            "assets/images/gate_daytime.png",
            "assets/images/North_building_daytime.png",
            "assets/images/auditorium_daytime1.png",
            "assets/images/library_daytime.png",
        ]

        self.bg_images = []
        for path in self.bg_paths:
            if os.path.exists(path):
                self.bg_images.append(pygame.image.load(path).convert())

        self.current_bg_index = 0
        self.last_switch_time = 0          # 将在 update 中首次初始化
        self.switch_interval = 3000        # 3秒切一次
        self.logo_path = "assets/images/start_logo.png"

        self.logo_image = None
        if os.path.exists(self.logo_path):
            self.logo_image = pygame.image.load(self.logo_path).convert_alpha()

    def update(self, events):
        now = pygame.time.get_ticks()
        # 首次调用时初始化上次切换时间
        if self.last_switch_time == 0:
            self.last_switch_time = now

        if self.bg_images and now - self.last_switch_time > self.switch_interval:
            self.current_bg_index = (self.current_bg_index + 1) % len(self.bg_images)
            self.last_switch_time = now

        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return Scene.SAVE_SELECT

        return None

    def draw(self, screen):
        # 绘制背景（若存在）或纯色背景
        if self.bg_images:
            bg = self.bg_images[self.current_bg_index]
            bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))
            screen.blit(bg, (0, 0))
        else:
            screen.fill((24, 28, 42))

        # 半透明遮罩，压暗背景突出前景
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        # 绘制 Logo 或备用标题
        if self.logo_image:
            # 等比缩放，宽度设为 550，保持清晰且不拥挤
            logo_w = 550
            logo_h = int(self.logo_image.get_height() * (logo_w / self.logo_image.get_width()))
            logo = pygame.transform.scale(self.logo_image, (logo_w, logo_h))
            logo_x = (screen.get_width() - logo_w) // 2
            logo_y = 120
            screen.blit(logo, (logo_x, logo_y))
        else:
            title = self.title_font.render("鼓楼拾光", True, (255, 225, 120))
            screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))

        # 呼吸灯效果的提示文字
        alpha = 150 + int(105 * abs(math.sin(pygame.time.get_ticks() / 600)))
        prompt = self.prompt_font.render("按任意键开始探索", True, (255, 255, 255))
        prompt.set_alpha(alpha)
        screen.blit(prompt, (
            (screen.get_width() - prompt.get_width()) // 2,
            400
        ))