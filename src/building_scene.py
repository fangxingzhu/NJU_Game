import os
import pygame

from src import time_system
from src.config import Scene, font1_path, font2_path
from src.dialog import DialogEngine
from src.ui import draw_dialog_box

class BuildingScene:
    def __init__(self):
        self.building_data = None
        self.dialog_engine = None
        self.is_night = False# 新增：记录当前是否夜晚
        self.time_system = None

    def enter(self, building_data, is_night=False, time_system=None):   # 新增 is_night 参数
        self.building_data = building_data
        self.is_night = is_night
        self.time_system = time_system
        dialog_content = building_data.get('dialog', '欢迎光临。')
        self.dialog_engine = DialogEngine(dialog_content)

    def update(self, events):
        # 实时同步时间状态
        if self.time_system:
            self.is_night = self.time_system.is_night()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Q 键退出
                    return Scene.OVERWORLD
                if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                    if self.dialog_engine and not self.dialog_engine.is_finished():
                        self.dialog_engine.next()
                        if self.dialog_engine.is_finished():
                            # 对话结束后不再自动退出，停留在内部
                            pass
        return None


    def draw(self, screen):
        bg_drawn = False
        if self.building_data:
            # 根据时间选择背景图的 key
            if self.is_night:
                bg_key = 'inside_night_bg'
            else:
                bg_key = 'inside_bg'

            bg_path = self.building_data.get(bg_key, '')
            # 如果没有夜晚图，回退到白天图
            if not bg_path:
                bg_path = self.building_data.get('inside_bg', '')

            if bg_path and os.path.exists(bg_path):
                try:
                    bg_image = pygame.image.load(bg_path).convert()
                    bg_image = pygame.transform.scale(bg_image, (screen.get_width(), screen.get_height()))
                    screen.blit(bg_image, (0, 0))
                    bg_drawn = True
                except pygame.error:
                    pass

        if not bg_drawn:
            screen.fill((20, 20, 60))   # 保底纯色背景

        # 绘制建筑名称（居中）
        if self.building_data:
            name_font = pygame.font.Font(font1_path, 36)
            name_surf = name_font.render(self.building_data['name'], True, (255,255,255))
            name_x = (screen.get_width() - name_surf.get_width()) // 2
            screen.blit(name_surf, (name_x, 100))

        # 绘制对话框
        if self.dialog_engine:
            msg = self.dialog_engine.get_current_message()
            if msg:
                draw_dialog_box(screen, msg)
            else:
                if self.dialog_engine.is_finished():
                    draw_dialog_box(screen, "对话已结束，按 Q 离开")
                else:
                    draw_dialog_box(screen, "这里空无一人。")

        # 绘制“按 Q 离开”提示（右下角，带半透明背景）
        tip_text = "按 Q 离开建筑"
        tip_font = pygame.font.Font(font2_path, 20)
        tip_surf = tip_font.render(tip_text, True, (255, 255, 255))  # 白色文字
        tip_padding = 14
        tip_bg_width = tip_surf.get_width() + tip_padding * 2
        tip_bg_height = tip_surf.get_height() + tip_padding
        tip_bg_rect = pygame.Rect(0, 0, tip_bg_width, tip_bg_height)
        tip_bg_rect.bottomright = (screen.get_width() - 20, screen.get_height() - 20)  # 右下角

        from src.ui import draw_time_ui  # 如果顶部还没导入
        draw_time_ui(screen, self.time_system)
        # 半透明背景
        tip_bg = pygame.Surface((tip_bg_width, tip_bg_height), pygame.SRCALPHA)
        tip_bg.fill((0, 0, 0, 160))
        screen.blit(tip_bg, tip_bg_rect.topleft)

        # 文字居中于背景
        tip_x = tip_bg_rect.x + tip_padding
        tip_y = tip_bg_rect.y + (tip_bg_height - tip_surf.get_height()) // 2
        screen.blit(tip_surf, (tip_x, tip_y))