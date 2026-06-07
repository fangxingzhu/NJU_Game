import pygame

from src.ui import get_ui_font


class SaveSelectScene:
    def __init__(self, save_manager):
        self.save_manager = save_manager
        self.slots = []
        self.slot_rects = []
        self.delete_rects = []
        self.refresh()

    def refresh(self):
        self.slots = self.save_manager.list_slots()

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, rect in enumerate(self.slot_rects):
                    slot = index + 1
                    if rect.collidepoint(event.pos):
                        if self.slots[index]:
                            return ("load_save", slot)
                        return ("new_save", slot)

                for index, rect in enumerate(self.delete_rects):
                    slot = index + 1
                    if self.slots[index] and rect.collidepoint(event.pos):
                        self.save_manager.delete(slot)
                        self.refresh()
        return None

    def draw(self, screen):
        screen.fill((18, 20, 28))
        title = get_ui_font(40).render("选择存档", True, (255, 255, 255))
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
