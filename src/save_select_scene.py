import pygame

from src.ui import get_ui_font
import src.config as config

class SaveSelectScene:
    def __init__(self, save_manager):
        self.save_manager = save_manager
        self.slots = []
        self.slot_rects = []
        self.delete_rects = []
        self.refresh()
        self.mode = "load"  # "load" 或 "save"
        self.auto_save_enabled = config.AUTO_SAVE_ENABLED  # 导入 config
        self.auto_save_rect = None  # 勾选框位置
        self.back_rect = None

    def set_mode(self, mode, auto_save_enabled):
        self.mode = mode
        self.auto_save_enabled = auto_save_enabled

    def refresh(self):
        self.slots = self.save_manager.list_slots()

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 检测存档槽点击
                for index, rect in enumerate(self.slot_rects):
                    slot = index + 1
                    if rect.collidepoint(event.pos):
                        if self.mode == "load":
                            if self.slots[index]:
                                return ("load_save", slot)
                            else:
                                return ("new_save", slot)
                        else:  # save 模式
                            return ("save_game", slot)

                # 检测删除按钮
                for index, rect in enumerate(self.delete_rects):
                    slot = index + 1
                    if self.slots[index] and rect.collidepoint(event.pos):
                        self.save_manager.delete(slot)
                        self.refresh()

                # 检测自动存档勾选框
                if self.auto_save_rect and self.auto_save_rect.collidepoint(event.pos):
                    self.auto_save_enabled = not self.auto_save_enabled
                    import src.config as config
                    config.AUTO_SAVE_ENABLED = self.auto_save_enabled

                # 检测返回按钮（注意：必须在这个鼠标事件块内）
                if self.back_rect and self.back_rect.collidepoint(event.pos):
                    return ("back_to_menu",)
        return None

    def draw(self, screen):
        screen.fill((18, 20, 28))
        mode_title = "选择存档" if self.mode == "load" else "保存游戏"
        title = get_ui_font(40).render(mode_title, True, (255, 255, 255))
        screen.blit(title, ((screen.get_width() - title.get_width()) // 2, 58))

        self.slot_rects = []
        self.delete_rects = []
        for index in range(self.save_manager.SLOT_COUNT):
            slot = index + 1
            save_data = self.slots[index]
            y = 140 + index * 130
            slot_rect = pygame.Rect(120, y, 520, 92)
            delete_rect = pygame.Rect(660, y + 23, 96, 46)
            self.slot_rects.append(slot_rect)
            self.delete_rects.append(delete_rect)
            self.draw_slot(screen, slot, save_data, slot_rect, delete_rect)

        # 绘制自动存档勾选框（紧接在三个存档槽下方）
        self.auto_save_rect = pygame.Rect(120, 500, 24, 24)  # 坐标可根据实际微调
        pygame.draw.rect(screen, (255, 255, 255), self.auto_save_rect, 2)
        if self.auto_save_enabled:
            # 画勾
            pygame.draw.line(screen, (255, 255, 255), (self.auto_save_rect.x + 4, self.auto_save_rect.y + 12),
                             (self.auto_save_rect.x + 10, self.auto_save_rect.y + 20), 3)
            pygame.draw.line(screen, (255, 255, 255), (self.auto_save_rect.x + 10, self.auto_save_rect.y + 20),
                             (self.auto_save_rect.x + 20, self.auto_save_rect.y + 4), 3)
        label = get_ui_font(20).render("开启自动存档", True, (230, 230, 230))
        screen.blit(label, (self.auto_save_rect.x + 30, self.auto_save_rect.y))

        # 在 draw 方法末尾，绘制返回按钮
        back_width, back_height = 160, 46
        back_x = (screen.get_width() - back_width) // 2
        back_y = self.auto_save_rect.y + 40  # 放在勾选框下方
        self.back_rect = pygame.Rect(back_x, back_y, back_width, back_height)
        pygame.draw.rect(screen, (70, 90, 130), self.back_rect)
        pygame.draw.rect(screen, (230, 230, 230), self.back_rect, 2)
        back_text = get_ui_font(24).render("返回", True, (255, 255, 255))
        screen.blit(back_text, (self.back_rect.x + (back_width - back_text.get_width()) // 2,
                                self.back_rect.y + (back_height - back_text.get_height()) // 2))

    def draw_slot(self, screen, slot, save_data, slot_rect, delete_rect):
        hovered = slot_rect.collidepoint(pygame.mouse.get_pos())
        border_color = (255, 205, 90) if hovered else (230, 230, 230)
        pygame.draw.rect(screen, (46, 52, 68), slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, 2)

        title_text = f"存档 {slot}"
        title = get_ui_font(26).render(title_text, True, (255, 255, 255))
        screen.blit(title, (slot_rect.x + 22, slot_rect.y + 14))

        if save_data:
            player = save_data.get("player", {})
            saved_at = save_data.get("saved_at", "")
            detail_text = f"{player.get('name', '未命名')} / {player.get('gender', '')} / {saved_at}"
            action_text = "继续游戏"
        else:
            detail_text = "空存档"
            action_text = "新建存档"

        detail = get_ui_font(18).render(detail_text, True, (210, 210, 210))
        action = get_ui_font(20).render(action_text, True, (255, 205, 90))
        screen.blit(detail, (slot_rect.x + 22, slot_rect.y + 52))
        screen.blit(action, (slot_rect.right - action.get_width() - 22, slot_rect.y + 52))

        if save_data:
            self.draw_delete_button(screen, delete_rect)

    def draw_delete_button(self, screen, rect):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        border_color = (255, 205, 90) if hovered else (230, 230, 230)
        pygame.draw.rect(screen, (84, 44, 50), rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        text = get_ui_font(20).render("删除", True, (255, 255, 255))
        screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2, rect.y + (rect.height - text.get_height()) // 2))
