import pygame
from src.config import Scene, font1_path
from src.dialog import DialogEngine
from src.ui import draw_dialog_box

class BuildingScene:
    def __init__(self):
        self.building_data = None
        self.dialog_engine = None
        self.name_font = pygame.font.Font(font1_path, 36)

    def enter(self, building_data):
        self.building_data = building_data
        # 从建筑数据中获取对话内容，创建对话引擎
        dialog_content = building_data.get('dialog', '欢迎光临。')
        self.dialog_engine = DialogEngine(dialog_content)

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Scene.OVERWORLD
                if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                    if self.dialog_engine and not self.dialog_engine.is_finished():
                        self.dialog_engine.next()
                        # 如果对话刚好在这一句结束，直接返回大地图
                        if self.dialog_engine.is_finished():
                            return Scene.OVERWORLD
        return None

    def draw(self, screen):
        screen.fill((20, 20, 60))  # 内部背景
        if self.building_data:
            # 显示建筑名称（上方标题）
            name_surf = self.name_font.render(self.building_data['name'], True, (255,255,255))
            name_x = (screen.get_width() - name_surf.get_width()) // 2
            screen.blit(name_surf, (name_x, 100))

        # 显示当前对话
        if self.dialog_engine:
            msg = self.dialog_engine.get_current_message()
            if msg:
                draw_dialog_box(screen, msg)
            else:
                # 如果没有对话内容（初始即为空列表），显示一个默认提示
                draw_dialog_box(screen, "这里空无一人。")
