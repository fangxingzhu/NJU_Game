import pygame
from src.ui import get_ui_font


class GameMenu:
    def __init__(self):
        self.mode = "menu"
        self.buttons = []

    def open(self):
        self.mode = "menu"

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.mode == "status":
                    self.mode = "menu"
                    return None
                return "continue"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, action in self.buttons:
                    if rect.collidepoint(event.pos):
                        if action == "status":
                            self.mode = "status"
                            return None
                        if action == "back":
                            self.mode = "menu"
                            return None
                        return action
        return None

    def draw(self, screen, player_data, current_slot, time_system):
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        screen.blit(overlay, (0, 0))

        self.buttons = []
        if self.mode == "status":
            self.draw_status(screen, player_data, current_slot, time_system)  # ✅ 传入 time_system
        else:
            self.draw_menu(screen)

    def draw_menu(self, screen):
        panel = pygame.Rect(250, 120, 300, 430)
        pygame.draw.rect(screen, (34, 38, 52), panel)
        pygame.draw.rect(screen, (230, 230, 230), panel, 2)

        title = get_ui_font(32).render("游戏菜单", True, (255, 255, 255))
        screen.blit(title, (panel.x + (panel.width - title.get_width()) // 2, panel.y + 28))

        items = [
            ("继续游戏", "continue"),
            ("当前状态", "status"),
            ("存档", "save"),
            ("读档", "load"),
            ("退出游戏", "exit")
        ]
        for index, (text, action) in enumerate(items):
            rect = pygame.Rect(panel.x + 55, panel.y + 92 + index * 66, 190, 46)
            self.buttons.append((rect, action))
            self.draw_button(screen, rect, text, True)

    def draw_status(self, screen, player_data, current_slot, time_system):
        # 1. 构建所有显示行
        lines = [
            f"存档：{current_slot if current_slot else '未保存'}",
            f"姓名：{player_data.name if player_data else '未创建'}",
            f"性别：{player_data.gender if player_data else '-'}",
            f"位置：({int(player_data.x)}, {int(player_data.y)})" if player_data else "位置：-",
            f"朝向：{player_data.direction if player_data else '-'}"
        ]
        if time_system:
            time_str = time_system.get_time_string()
            day_str = f"第{time_system.day}天"
            week_str = time_system.get_weekday()
            lines.append(f"时间：{time_str}  {day_str}  {week_str}")

        # 2. 确定布局参数
        line_count = len(lines)
        line_height = 36  # 行间距
        title_bottom = 18 + 32  # 标题 y(18) + 标题字号大概高度
        first_line_y = 70  # 第一行文本的起始 y 坐标（相对于面板）
        button_height = 46
        button_margin = 20  # 按钮距离最后一行文本的间距

        # 3. 计算面板高度（一次性算对，不再变动）
        content_height = first_line_y + line_count * line_height
        panel_height = content_height + button_margin + button_height + 20  # 底部留白 20
        panel = pygame.Rect(170, 80, 460, panel_height)

        # 4. 绘制面板背景和边框（只画一次！）
        pygame.draw.rect(screen, (34, 38, 52), panel)
        pygame.draw.rect(screen, (230, 230, 230), panel, 2)

        # 5. 绘制标题
        title = get_ui_font(32).render("当前状态", True, (255, 255, 255))
        screen.blit(title, (panel.x + 36, panel.y + 18))

        # 6. 逐行绘制文字
        for i, line in enumerate(lines):
            text = get_ui_font(22).render(line, True, (230, 230, 230))
            y = panel.y + first_line_y + i * line_height
            screen.blit(text, (panel.x + 44, y))

        # 7. 绘制返回按钮（紧贴文字下方，绝对不重叠）
        btn_rect = pygame.Rect(panel.x + 150, panel.y + content_height + button_margin, 160, 46)
        self.buttons.append((btn_rect, "back"))
        self.draw_button(screen, btn_rect, "返回", True)

    def draw_button(self, screen, rect, text, enabled):
        hovered = enabled and rect.collidepoint(pygame.mouse.get_pos())
        border_color = (255, 205, 90) if hovered else (230, 230, 230)
        pygame.draw.rect(screen, (70, 90, 130), rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        text_surf = get_ui_font(22).render(text, True, (255, 255, 255))
        screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + (rect.height - text_surf.get_height()) // 2))