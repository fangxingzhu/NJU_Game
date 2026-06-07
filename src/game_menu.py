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

    def draw(self, screen, player_data, current_slot):
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        screen.blit(overlay, (0, 0))

        self.buttons = []
        if self.mode == "status":
            self.draw_status(screen, player_data, current_slot)
        else:
            self.draw_menu(screen)

    def draw_menu(self, screen):
        panel = pygame.Rect(250, 120, 300, 360)
        pygame.draw.rect(screen, (34, 38, 52), panel)
        pygame.draw.rect(screen, (230, 230, 230), panel, 2)

        title = get_ui_font(32).render("游戏菜单", True, (255, 255, 255))
        screen.blit(title, (panel.x + (panel.width - title.get_width()) // 2, panel.y + 28))

        items = [
            ("继续游戏", "continue"),
            ("当前状态", "status"),
            ("查看存档", "saves"),
            ("退出游戏", "exit")
        ]
        for index, (text, action) in enumerate(items):
            rect = pygame.Rect(panel.x + 55, panel.y + 92 + index * 66, 190, 46)
            self.buttons.append((rect, action))
            self.draw_button(screen, rect, text, True)

    def draw_status(self, screen, player_data, current_slot):
        panel = pygame.Rect(170, 110, 460, 380)
        pygame.draw.rect(screen, (34, 38, 52), panel)
        pygame.draw.rect(screen, (230, 230, 230), panel, 2)

        title = get_ui_font(32).render("当前状态", True, (255, 255, 255))
        screen.blit(title, (panel.x + 36, panel.y + 30))

        lines = [
            f"存档：{current_slot if current_slot else '未保存'}",
            f"姓名：{player_data.name if player_data else '未创建'}",
            f"性别：{player_data.gender if player_data else '-'}",
            f"位置：({int(player_data.x)}, {int(player_data.y)})" if player_data else "位置：-",
            f"朝向：{player_data.direction if player_data else '-'}"
        ]
        for index, line in enumerate(lines):
            text = get_ui_font(22).render(line, True, (230, 230, 230))
            screen.blit(text, (panel.x + 44, panel.y + 92 + index * 42))

        rect = pygame.Rect(panel.x + 150, panel.y + 306, 160, 46)
        self.buttons.append((rect, "back"))
        self.draw_button(screen, rect, "返回", True)

    def draw_button(self, screen, rect, text, enabled):
        hovered = enabled and rect.collidepoint(pygame.mouse.get_pos())
        border_color = (255, 205, 90) if hovered else (230, 230, 230)
        pygame.draw.rect(screen, (70, 90, 130), rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        text_surf = get_ui_font(22).render(text, True, (255, 255, 255))
        screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + (rect.height - text_surf.get_height()) // 2))
