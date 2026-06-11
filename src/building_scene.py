import os
import pygame
import random
import time
from src.config import Scene, font1_path, font2_path
from src.dialog import DialogEngine
from src.ui import draw_dialog_box


class BuildingScene:
    def __init__(self):
        self.building_data = None
        self.dialog_engine = None
        self.is_night = False          # 记录当前是否夜晚
        self.time_system = None
        self.mode = "dialog"           # 当前模式：dialog, intro, choice, npc_dialog_first, reply_choice, player_reply, npc_dialog_final
        self.yes_button = pygame.Rect(0, 0, 0, 0)
        self.no_button = pygame.Rect(0, 0, 0, 0)
        self.reply1_button = pygame.Rect(0, 0, 0, 0)
        self.reply2_button = pygame.Rect(0, 0, 0, 0)
        self.quiz_option_buttons = []
        self.current_dialog_case = None
        self.player_data = None
        self.player_reply_text = None
        self.pending_npc_reply = None   # 存储 NPC 的最终回复（可能是字符串或列表）
        self.quiz_index = 0
        self.quiz_questions = []
        self.quiz_feedback = None
        self.background_cache = {}
        self.portrait_cache = {}
        self.name_font = pygame.font.Font(font1_path, 36)
        self.tip_font = pygame.font.Font(font2_path, 20)
        self.choice_font = pygame.font.Font(font2_path, 22)

    def get_scaled_image(self, cache, path, size, alpha=False):
        key = (path, size)
        if key not in cache:
            if not path or not os.path.exists(path):
                cache[key] = None
            else:
                try:
                    image = pygame.image.load(path)
                    image = image.convert_alpha() if alpha else image.convert()
                    cache[key] = pygame.transform.scale(image, size)
                except pygame.error:
                    cache[key] = None
        return cache[key]

    def wrap_text(self, text, font, max_width):
        lines = []
        current = ""
        for char in text:
            test_line = current + char
            if current and font.size(test_line)[0] > max_width:
                lines.append(current)
                current = char
            else:
                current = test_line
        if current:
            lines.append(current)
        return lines

    def enter(self, building_data, is_night=False, time_system=None, player_data=None):
        self.player_data = player_data
        self.building_data = building_data
        self.is_night = is_night
        self.time_system = time_system

        # 重置所有状态
        self.yes_button = pygame.Rect(0, 0, 0, 0)
        self.no_button = pygame.Rect(0, 0, 0, 0)
        self.reply1_button = pygame.Rect(0, 0, 0, 0)
        self.reply2_button = pygame.Rect(0, 0, 0, 0)
        self.quiz_option_buttons = []
        self.current_dialog_case = None
        self.player_reply_text = None
        self.pending_npc_reply = None
        self.quiz_index = 0
        self.quiz_questions = []
        self.quiz_feedback = None

        # 根据建筑配置决定进入哪种模式
        if building_data.get("dialog_mode") == "quiz":
            self.mode = "quiz_intro"
            all_questions = building_data.get("quiz_questions", [])
            question_count = min(5, len(all_questions))
            self.quiz_questions = random.Random(time.time_ns()).sample(all_questions, question_count)
            intro_dialog = building_data.get("quiz_intro", building_data.get('dialog', ["欢迎来到问答活动。"]))
            self.dialog_engine = DialogEngine(intro_dialog)
        elif building_data.get("dialog_mode") == "intro_choice":
            self.mode = "intro"
            intro_dialog = building_data.get("intro_dialog", ["欢迎光临。"])
            self.dialog_engine = DialogEngine(intro_dialog)
        else:
            self.mode = "dialog"
            dialog_content = building_data.get('dialog', '欢迎光临。')
            self.dialog_engine = DialogEngine(dialog_content)

    def update(self, events):
        # 实时同步时间状态
        if self.time_system:
            self.is_night = self.time_system.is_night()

        for event in events:
            if self.mode == "quiz_intro" and event.type == pygame.MOUSEBUTTONDOWN:
                if self.yes_button.collidepoint(event.pos):
                    self.start_quiz_question()
                elif self.no_button.collidepoint(event.pos):
                    return Scene.OVERWORLD
                return None

            if self.mode == "quiz_question" and event.type == pygame.MOUSEBUTTONDOWN:
                for index, rect in enumerate(self.quiz_option_buttons):
                    if rect.collidepoint(event.pos):
                        self.submit_quiz_answer(index)
                        break
                return None

            # 处理选择界面（choice）的鼠标点击
            if self.mode == "choice" and event.type == pygame.MOUSEBUTTONDOWN:
                if self.yes_button.collidepoint(event.pos):
                    # 根据昼夜选择对话案例列表
                    if self.time_system and self.time_system.is_night():
                        cases = self.building_data.get("dialog_cases_night", [])
                    else:
                        cases = self.building_data.get("dialog_cases_day", [])
                    if cases:
                        self.current_dialog_case = random.choice(cases)
                        # 获取 NPC 说的内容（可能是字符串或列表）
                        npc_content = self.current_dialog_case.get("npc", "欢迎来到南大。")
                        if isinstance(npc_content, list):
                            self.dialog_engine = DialogEngine(npc_content)
                        else:
                            self.dialog_engine = DialogEngine([npc_content])
                        self.mode = "npc_dialog_first"
                    else:
                        # 没有案例就显示默认对话
                        self.dialog_engine = DialogEngine(["欢迎来到南大。"])
                        self.mode = "npc_dialog_first"
                elif self.no_button.collidepoint(event.pos):
                    return Scene.OVERWORLD
                return None  # 点击按钮后不继续处理其他事件

            # 处理回复选项（reply_choice）的鼠标点击
            if self.mode == "reply_choice" and event.type == pygame.MOUSEBUTTONDOWN:
                if self.reply1_button.collidepoint(event.pos):
                    option_data = self.current_dialog_case["options"][0]
                    if isinstance(option_data, dict):
                        self.player_reply_text = option_data["text"]
                    else:
                        self.player_reply_text = option_data
                    self.pending_npc_reply = self.current_dialog_case["replies"][0]
                    self.dialog_engine = DialogEngine([f"你：{self.player_reply_text}"])
                    self.mode = "player_reply"
                elif self.reply2_button.collidepoint(event.pos):
                    option_data = self.current_dialog_case["options"][1]
                    if isinstance(option_data, dict):
                        self.player_reply_text = option_data["text"]
                    else:
                        self.player_reply_text = option_data
                    self.pending_npc_reply = self.current_dialog_case["replies"][1]
                    self.dialog_engine = DialogEngine([f"你：{self.player_reply_text}"])
                    self.mode = "player_reply"
                return None

            # 键盘事件处理
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:        # 按 Q 退出建筑
                    return Scene.OVERWORLD

                if event.key == pygame.K_SPACE or event.key == pygame.K_e:
                    if self.mode == "quiz_result":
                        if self.quiz_index < len(self.quiz_questions):
                            self.start_quiz_question()
                            return None
                        return Scene.OVERWORLD

                    # 不同模式下的对话推进逻辑
                    if self.mode == "intro":
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()
                        if self.dialog_engine and self.dialog_engine.is_finished():
                            self.mode = "choice"
                            self.dialog_engine = None
                        return None

                    if self.mode == "npc_dialog_first":
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()
                        if self.dialog_engine and self.dialog_engine.is_finished():
                            self.mode = "reply_choice"
                            self.dialog_engine = None
                        return None

                    if self.mode == "player_reply":
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()
                        if self.dialog_engine and self.dialog_engine.is_finished():
                            # 显示 NPC 的最终回复
                            reply_content = self.pending_npc_reply
                            if isinstance(reply_content, list):
                                self.dialog_engine = DialogEngine(reply_content)
                            else:
                                self.dialog_engine = DialogEngine([reply_content])
                            self.mode = "npc_dialog_final"
                        return None

                    if self.mode == "npc_dialog_final":
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()
                        return None

                    # 普通对话模式（dialog）
                    if self.mode == "dialog":
                        if self.dialog_engine and not self.dialog_engine.is_finished():
                            self.dialog_engine.next()
                        return None
        return None

    def start_quiz_question(self):
        if not self.quiz_questions:
            self.quiz_feedback = self.building_data.get("quiz_empty_text", "题库暂未配置。")
            self.mode = "quiz_result"
            return

        self.current_dialog_case = self.quiz_questions[self.quiz_index]
        self.quiz_index += 1
        self.dialog_engine = None
        self.quiz_feedback = None
        self.mode = "quiz_question"

    def submit_quiz_answer(self, selected_index):
        if not self.current_dialog_case:
            return

        answer_index = self.current_dialog_case.get("answer", 0)
        if selected_index == answer_index:
            self.quiz_feedback = self.current_dialog_case.get("correct_reply", "回答正确！")
        else:
            self.quiz_feedback = self.current_dialog_case.get("wrong_reply", "回答错误，再接再厉。")
        self.mode = "quiz_result"

    def draw(self, screen):
        # 绘制建筑内部背景
        bg_drawn = False
        if self.building_data:
            if self.is_night:
                bg_key = 'inside_night_bg'
            else:
                bg_key = 'inside_bg'
            bg_path = self.building_data.get(bg_key, '')
            if not bg_path:
                bg_path = self.building_data.get('inside_bg', '')
            if bg_path:
                bg_image = self.get_scaled_image(
                    self.background_cache,
                    bg_path,
                    (screen.get_width(), screen.get_height())
                )
                if bg_image:
                    screen.blit(bg_image, (0, 0))
                    bg_drawn = True
        if not bg_drawn:
            screen.fill((20, 20, 60))

        # 绘制建筑名称
        if self.building_data:
            name_surf = self.name_font.render(self.building_data['name'], True, (255, 255, 255))
            name_x = (screen.get_width() - name_surf.get_width()) // 2
            screen.blit(name_surf, (name_x, 100))

        # 绘制 NPC 立绘（仅在对话阶段显示）
        if self.mode in ("npc_dialog_first", "npc_dialog_final") \
                and not (self.dialog_engine and self.dialog_engine.is_finished()):
            npc_image_path = self.building_data.get("npc_image", "")
            npc_img = None
            if npc_image_path:
                npc_img = self.get_scaled_image(
                    self.portrait_cache,
                    npc_image_path,
                    (180, 180),
                    alpha=True
                )
            if npc_img:
                screen.blit(npc_img, (40, screen.get_height() - 270))

        # 绘制玩家立绘（仅在玩家说话时显示）
        if self.mode == "player_reply":
            gender = "男"
            if self.player_data:
                gender = self.player_data.gender
            if gender == "女":
                player_path = "assets/images/girl_portrait256.png"
            else:
                player_path = "assets/images/boy_portrait256.png"
            player_img = self.get_scaled_image(
                self.portrait_cache,
                player_path,
                (160, 160),
                alpha=True
            )
            if player_img:
                screen.blit(player_img, (screen.get_width() - 220, screen.get_height() - 270))

        # 绘制选择界面
        if self.mode == "quiz_intro":
            self.draw_quiz_intro_ui(screen)
        if self.mode == "quiz_question":
            self.draw_reply_choice_ui(screen)
        if self.mode == "choice":
            self.draw_choice_ui(screen)
        if self.mode == "reply_choice":
            self.draw_reply_choice_ui(screen)

        # 绘制对话框（底部）
        if self.mode == "quiz_result" and self.quiz_feedback:
            draw_dialog_box(screen, self.quiz_feedback)
        elif self.dialog_engine:
            msg = self.dialog_engine.get_current_message()
            if msg:
                draw_dialog_box(screen, msg)
            else:
                if self.dialog_engine.is_finished() and self.mode == "npc_dialog_final":
                    draw_dialog_box(screen, "对话已结束")
                else:
                    draw_dialog_box(screen, "这里空无一人。")

        # 绘制“按 Q 离开”提示
        tip_text = "按 Q 离开建筑"
        tip_surf = self.tip_font.render(tip_text, True, (255, 255, 255))
        tip_padding = 14
        tip_bg_width = tip_surf.get_width() + tip_padding * 2
        tip_bg_height = tip_surf.get_height() + tip_padding
        tip_bg_rect = pygame.Rect(0, 0, tip_bg_width, tip_bg_height)
        tip_bg_rect.bottomright = (screen.get_width() - 20, screen.get_height() - 20)
        tip_bg = pygame.Surface((tip_bg_width, tip_bg_height), pygame.SRCALPHA)
        tip_bg.fill((0, 0, 0, 160))
        screen.blit(tip_bg, tip_bg_rect.topleft)
        tip_x = tip_bg_rect.x + tip_padding
        tip_y = tip_bg_rect.y + (tip_bg_height - tip_surf.get_height()) // 2
        screen.blit(tip_surf, (tip_x, tip_y))

    def draw_quiz_intro_ui(self, screen):
        panel_width = 420
        panel_height = 190
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (42, 24, 28), panel_rect)
        pygame.draw.rect(screen, (245, 210, 160), panel_rect, 3)
        inner_rect = panel_rect.inflate(-8, -8)
        pygame.draw.rect(screen, (130, 64, 64), inner_rect, 1)

        title_text = self.building_data.get("choice_prompt", "红色教育问答")
        title_surf = self.choice_font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 24))

        self.yes_button = pygame.Rect(panel_rect.x + 90, panel_rect.y + 78, 240, 42)
        self.no_button = pygame.Rect(panel_rect.x + 90, panel_rect.y + 128, 240, 42)
        self.draw_choice_button(screen, self.yes_button, self.building_data.get("choice_yes", "开始答题"))
        self.draw_choice_button(screen, self.no_button, self.building_data.get("choice_no", "暂时离开"))

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

        title_text = self.building_data.get("choice_prompt", "")
        title_surf = self.choice_font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surf, (panel_rect.centerx - title_surf.get_width() // 2, panel_rect.y + 24))

        self.yes_button = pygame.Rect(panel_rect.x + 90, panel_rect.y + 78, 240, 42)
        self.no_button = pygame.Rect(panel_rect.x + 90, panel_rect.y + 128, 240, 42)
        self.draw_choice_button(screen, self.yes_button, self.building_data.get("choice_yes", "开始对话"))
        self.draw_choice_button(screen, self.no_button, self.building_data.get("choice_no", "暂时离开"))

    def draw_reply_choice_ui(self, screen):
        if not self.current_dialog_case:
            return
        options = self.current_dialog_case.get("options", ["好的。", "知道了。"])
        # 如果选项是字典，则提取文本用于显示
        option_texts = []
        for opt in options:
            if isinstance(opt, dict):
                option_texts.append(opt.get("text", ""))
            else:
                option_texts.append(opt)

        is_quiz = self.mode == "quiz_question"
        question_text = self.current_dialog_case.get("question", "") if is_quiz else ""
        question_lines = self.wrap_text(question_text, self.choice_font, 520) if question_text else []
        panel_width = 640 if question_text else 500
        panel_height = 86 + len(question_lines) * 30 + len(option_texts) * 54 if question_text else 170
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (24, 28, 42), panel_rect)
        pygame.draw.rect(screen, (245, 230, 160), panel_rect, 3)
        inner_rect = panel_rect.inflate(-8, -8)
        pygame.draw.rect(screen, (80, 88, 120), inner_rect, 1)

        if question_lines:
            for index, line in enumerate(question_lines):
                question_surf = self.choice_font.render(line, True, (255, 255, 255))
                screen.blit(question_surf, (panel_rect.centerx - question_surf.get_width() // 2, panel_rect.y + 26 + index * 30))

        button_y = panel_rect.y + (46 + len(question_lines) * 30 if question_text else 42)
        if is_quiz:
            self.quiz_option_buttons = []
            for index, text in enumerate(option_texts):
                rect = pygame.Rect(panel_rect.x + 60, button_y + index * 54, panel_width - 120, 42)
                self.quiz_option_buttons.append(rect)
                self.draw_choice_button(screen, rect, text)
        else:
            self.reply1_button = pygame.Rect(panel_rect.x + 60, button_y, panel_width - 120, 42)
            self.reply2_button = pygame.Rect(panel_rect.x + 60, button_y + 56, panel_width - 120, 42)
            self.draw_choice_button(screen, self.reply1_button, option_texts[0])
            self.draw_choice_button(screen, self.reply2_button, option_texts[1])

    def draw_choice_button(self, screen, rect, text):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        bg_color = (88, 58, 120) if hovered else (60, 70, 110)
        border_color = (245, 230, 160) if hovered else (230, 230, 230)
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        text_surf = self.choice_font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))
