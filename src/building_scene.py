import os
import pygame
import random

from src.config import Scene, font1_path, font2_path
from src.dialog import DialogEngine
from src.ui import draw_dialog_box

class BuildingScene:
    def __init__(self):
        self.building_data = None
        self.dialog_engine = None
        self.is_night = False# 新增：记录当前是否夜晚
        self.time_system = None
        self.mode = "dialog"
        self.yes_button = pygame.Rect(0, 0, 0, 0)
        self.no_button = pygame.Rect(0, 0, 0, 0)
        self.reply1_button = pygame.Rect(0, 0, 0, 0)
        self.reply2_button = pygame.Rect(0, 0, 0, 0)
        self.current_dialog_case = None
        self.player_data=None
        self.player_reply_text = None
        self.pending_guard_reply = None

    def enter(self, building_data, is_night=False, time_system=None, player_data=None):
        self.player_data = player_data
        self.building_data = building_data
        self.is_night = is_night
        self.time_system = time_system
        self.yes_button = pygame.Rect(0, 0, 0, 0)
        self.no_button = pygame.Rect(0, 0, 0, 0)
        self.reply1_button = pygame.Rect(0, 0, 0, 0)
        self.reply2_button = pygame.Rect(0, 0, 0, 0)
        self.current_dialog_case = None
        self.player_reply_text = None
        self.pending_guard_reply = None

        if building_data.get("dialog_mode") == "intro_choice":
            self.mode = "intro"
            intro_dialog = building_data.get("intro_dialog", ["欢迎光临。"])
            self.dialog_engine = DialogEngine(intro_dialog)
        else:
            self.mode = "dialog"
            dialog_content = building_data.get('dialog', '欢迎光临。')
            self.dialog_engine = DialogEngine(dialog_content)

    def update(self, events):
        if self.time_system:
            self.is_night = self.time_system.is_night()

        for event in events:
            if self.mode == "choice" and event.type == pygame.MOUSEBUTTONDOWN:
                if self.yes_button.collidepoint(event.pos):
                    if self.time_system and self.time_system.is_night():
                        cases = self.building_data.get("dialog_cases_night", [])
                    else:
                        cases = self.building_data.get("dialog_cases_day", [])

                    if cases:
                        self.current_dialog_case = random.choice(cases)
                        self.mode = "npc_dialog_first"
                        self.dialog_engine = DialogEngine([self.current_dialog_case["guard"]])
                    else:
                        self.mode = "npc_dialog_first"
                        self.dialog_engine = DialogEngine(["保安：欢迎来到南大。"])
                elif self.no_button.collidepoint(event.pos):
                    return Scene.OVERWORLD
                return None
            if self.mode == "reply_choice" and event.type == pygame.MOUSEBUTTONDOWN:
                if self.reply1_button.collidepoint(event.pos):
                    self.mode = "player_reply"
                    self.player_reply_text = self.current_dialog_case["options"][0]
                    self.pending_guard_reply = self.current_dialog_case["replies"][0]
                    self.dialog_engine = DialogEngine([f"你：{self.player_reply_text}"])

                elif self.reply2_button.collidepoint(event.pos):
                    self.mode = "player_reply"
                    self.player_reply_text = self.current_dialog_case["options"][1]
                    self.pending_guard_reply = self.current_dialog_case["replies"][1]
                    self.dialog_engine = DialogEngine([f"你：{self.player_reply_text}"])

                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return Scene.OVERWORLD

                if self.mode == "intro":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()

                        if self.dialog_engine and self.dialog_engine.is_finished():
                            self.mode = "choice"
                            self.dialog_engine = None
                    return None

            

                if self.mode == "npc_dialog_first":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()

                        if self.dialog_engine and self.dialog_engine.is_finished():
                            self.mode = "reply_choice"
                            self.dialog_engine = None
                    return None
                
                if self.mode == "player_reply":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()

                        if self.dialog_engine and self.dialog_engine.is_finished():
                            self.mode = "npc_dialog_final"
                            self.dialog_engine = DialogEngine([self.pending_guard_reply])
                    return None

                if self.mode == "npc_dialog_final":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()
                    return None

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

        if self.mode in ("npc_dialog_first", "npc_dialog_final"):
            guard_path = "assets/images/guard1024.png"
            if os.path.exists(guard_path):
                guard_img = pygame.image.load(guard_path).convert_alpha()
                guard_img = pygame.transform.scale(guard_img, (180, 180))
                screen.blit(guard_img, (40, screen.get_height() - 270))

        if self.mode == "player_reply":
            gender = "男"

            if self.player_data:
                gender = self.player_data.gender

            if gender == "女":
                player_path = "assets/images/girl_portrait256.png"
            else:
                player_path = "assets/images/boy_portrait256.png"

            if os.path.exists(player_path):
                player_img = pygame.image.load(player_path).convert_alpha()
                player_img = pygame.transform.scale(player_img, (160, 160))
                screen.blit(
                    player_img,
                    (
                        screen.get_width() - 220,
                        screen.get_height() - 270
                    )
                )

        if self.mode == "choice":
            self.draw_choice_ui(screen)
        if self.mode == "reply_choice":
            self.draw_reply_choice_ui(screen)
        
        

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

    def draw_choice_ui(self, screen):
        panel_width = 420
        panel_height = 190
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        pygame.draw.rect(screen, (24, 28, 42), panel_rect)
        pygame.draw.rect(screen, (245, 230, 160), panel_rect, 3)

        inner_rect = panel_rect.inflate(-8, -8)
        pygame.draw.rect(screen, (80, 88, 120), inner_rect, 1)

        title_font = pygame.font.Font(font2_path, 22)
        title_text = self.building_data.get(
            "choice_prompt",
            ""
        )
        title_surf = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(
            title_surf,
            (
                panel_rect.centerx - title_surf.get_width() // 2,
                panel_rect.y + 24
            )
        )

        self.yes_button = pygame.Rect(
            panel_rect.x + 90,
            panel_rect.y + 78,
            240,
            42
        )

        self.no_button = pygame.Rect(
            panel_rect.x + 90,
            panel_rect.y + 128,
            240,
            42
        )

        self.draw_choice_button(screen, self.yes_button, "开始对话")
        self.draw_choice_button(screen, self.no_button, "暂时离开")

    def draw_choice_button(self, screen, rect, text):
        hovered = rect.collidepoint(pygame.mouse.get_pos())

        bg_color = (88, 58, 120) if hovered else (60, 70, 110)
        border_color = (245, 230, 160) if hovered else (230, 230, 230)

        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, 2)

        font = pygame.font.Font(font2_path, 22)
        text_surf = font.render(text, True, (255, 255, 255))

        screen.blit(
            text_surf,
            (
                rect.centerx - text_surf.get_width() // 2,
                rect.centery - text_surf.get_height() // 2
            )
        )

    def draw_reply_choice_ui(self, screen):
        if not self.current_dialog_case:
            return

        options = self.current_dialog_case.get(
            "options",
            ["好的。", "知道了。"]
        )

        panel_width = 500
        panel_height = 170
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        pygame.draw.rect(screen, (24, 28, 42), panel_rect)
        pygame.draw.rect(screen, (245, 230, 160), panel_rect, 3)

        inner_rect = panel_rect.inflate(-8, -8)
        pygame.draw.rect(screen, (80, 88, 120), inner_rect, 1)

        self.reply1_button = pygame.Rect(panel_rect.x + 60, panel_rect.y + 42, 380, 42)
        self.reply2_button = pygame.Rect(panel_rect.x + 60, panel_rect.y + 98, 380, 42)

        self.draw_choice_button(screen, self.reply1_button, options[0])
        self.draw_choice_button(screen, self.reply2_button, options[1])
