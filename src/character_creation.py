import os
import platform
import subprocess

import pygame

from src.config import Scene
from src.player_data import PlayerData
from src.ui import get_ui_font


class CharacterCreationScene:
    def __init__(self):
        self.name = ""
        self.gender = "男"
        self.name_error = ""
        self.created_player_data = None
        self.name_rect = pygame.Rect(0, 0, 320, 48)
        self.male_rect = pygame.Rect(0, 0, 130, 46)
        self.female_rect = pygame.Rect(0, 0, 130, 46)
        self.confirm_rect = pygame.Rect(0, 0, 220, 52)
        self.portrait_cache = {}
        self.dormitories = ["南园14舍", "南园1舍", "南园2舍", "南园3舍", "南园4舍"]
        self.dormitory_index = 0
        self.left_arrow_rect = pygame.Rect(0, 0, 30, 30)
        self.right_arrow_rect = pygame.Rect(0, 0, 30, 30)

    def get_portrait(self, portrait_file):
        if portrait_file not in self.portrait_cache:
            portrait_path = os.path.join("assets", "images", portrait_file)
            if not os.path.exists(portrait_path):
                self.portrait_cache[portrait_file] = None
            else:
                try:
                    self.portrait_cache[portrait_file] = pygame.image.load(portrait_path).convert_alpha()
                except pygame.error:
                    self.portrait_cache[portrait_file] = None
        return self.portrait_cache[portrait_file]

    def reset(self):
        self.name = ""
        self.gender = "男"
        self.name_error = ""
        self.created_player_data = None
        self.dormitory_index = 0

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Scene.START
                if event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pygame.K_RETURN and self.can_confirm():
                    self.created_player_data = PlayerData(self.name.strip(), self.gender)
                    self.created_player_data.dormitory = self.dormitories[self.dormitory_index]
                    return Scene.OVERWORLD
            if event.type == pygame.MOUSEWHEEL:
                # 滚轮向上 y > 0 表示向左切换，向下 y < 0 向右切换
                if event.y > 0:
                    self.dormitory_index = (self.dormitory_index - 1) % len(self.dormitories)
                elif event.y < 0:
                    self.dormitory_index = (self.dormitory_index + 1) % len(self.dormitories)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.name_rect.collidepoint(event.pos):
                    self.open_name_dialog()
                elif self.male_rect.collidepoint(event.pos):
                    self.gender = "男"
                elif self.female_rect.collidepoint(event.pos):
                    self.gender = "女"
                elif self.confirm_rect.collidepoint(event.pos) and self.can_confirm():
                    self.created_player_data = PlayerData(self.name.strip(), self.gender)
                    self.created_player_data.dormitory = self.dormitories[self.dormitory_index]
                    return Scene.OVERWORLD
                # 宿舍选择箭头
                if self.left_arrow_rect.collidepoint(event.pos):
                    self.dormitory_index = (self.dormitory_index - 1) % len(self.dormitories)
                elif self.right_arrow_rect.collidepoint(event.pos):
                    self.dormitory_index = (self.dormitory_index + 1) % len(self.dormitories)
        return None

    def name_length(self, text):
        length = 0
        for char in text.strip():
            length += 2 if ord(char) > 127 else 1
        return length

    def can_confirm(self):
        return bool(self.name.strip()) and self.name_length(self.name) <= 16

    def open_name_dialog(self):
        system = platform.system()
        if system == "Windows":
            value = self.open_windows_name_dialog()
        elif system == "Darwin":
            value = self.open_macos_name_dialog()
        else:
            value = self.open_tk_name_dialog()

        if value is None:
            return

        value = value.strip()
        if not value:
            return

        if self.name_length(value) > 16:
            self.name_error = "姓名最多 8 个中文或 16 个英文字符"
            return

        self.name = value
        self.name_error = ""

    def open_windows_name_dialog(self):
        command = (
            "Add-Type -AssemblyName Microsoft.VisualBasic; "
            "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$value=[Microsoft.VisualBasic.Interaction]::InputBox("
            "'请输入姓名：','输入姓名',$env:NJU_GAME_INITIAL_NAME); "
            "[Console]::Write($value)"
        )
        env = os.environ.copy()
        env["NJU_GAME_INITIAL_NAME"] = self.name
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                creationflags=creationflags
            )
        except (OSError, subprocess.SubprocessError):
            self.name_error = "无法打开姓名输入窗口"
            return None

        if result.returncode != 0:
            self.name_error = "姓名输入窗口返回错误"
            return None
        return result.stdout

    def open_macos_name_dialog(self):
        initial_name = self.escape_applescript_text(self.name)
        script = (
            'text returned of (display dialog "请输入姓名：" '
            f'default answer "{initial_name}" '
            'with title "输入姓名" buttons {"取消", "确认"} default button "确认")'
        )

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
        except (OSError, subprocess.SubprocessError):
            self.name_error = "无法打开 macOS 姓名输入窗口"
            return None

        if result.returncode != 0:
            return None
        return result.stdout

    def escape_applescript_text(self, text):
        return text.replace("\\", "\\\\").replace('"', '\\"')

    def open_tk_name_dialog(self):
        try:
            import tkinter as tk
            from tkinter import simpledialog
        except ImportError:
            self.name_error = "当前系统缺少姓名输入窗口支持"
            return None

        root = tk.Tk()
        root.withdraw()
        try:
            return simpledialog.askstring("输入姓名", "请输入姓名：", initialvalue=self.name, parent=root)
        finally:
            root.destroy()

    def draw(self, screen):
        self.draw_portrait_background(screen)
        self.draw_form(screen)

    def draw_portrait_background(self, screen):
        # 背景色（男女不同）
        if self.gender == "男":
            bg_color = (40, 84, 104)
            portrait_file = "boy_portrait256.png"
            border_color = (92, 178, 196)  # 边框颜色
        else:
            bg_color = (104, 58, 92)
            portrait_file = "girl_portrait256.png"
            border_color = (214, 136, 180)

        screen.fill(bg_color)

        # 绘制立绘图片（如果存在）
        portrait_img = self.get_portrait(portrait_file)
        portrait_drawn = False
        if portrait_img:
            try:
                img_width, img_height = portrait_img.get_size()  # 256x256

                # 图片大小保持不变（256x256），直接放在矩形区域中央
                # 原先矩形区域是 (70, 92, 260, 420)
                portrait_x = 70 + (260 - img_width) // 2
                portrait_y = 92 + (420 - img_height) // 2

                # 先画一个半透明背景板（可选，让立绘更突出）
                bg_plate = pygame.Surface((img_width + 16, img_height + 16), pygame.SRCALPHA)
                bg_plate.fill((0, 0, 0, 100))  # 半透明黑
                screen.blit(bg_plate, (portrait_x - 8, portrait_y - 8))

                # 画立绘
                screen.blit(portrait_img, (portrait_x, portrait_y))
                portrait_drawn = True

                # 画矩形边框（紧贴立绘，稍留间距）
                border_rect = pygame.Rect(portrait_x - 4, portrait_y - 4,
                                          img_width + 8, img_height + 8)
                pygame.draw.rect(screen, border_color, border_rect, 3)

            except pygame.error:
                pass

        # 如果图片加载失败，显示占位矩形（保留原逻辑）
        if not portrait_drawn:
            placeholder_color = border_color
            pygame.draw.rect(screen, placeholder_color, (70, 92, 260, 420))

        # 外边框（整个屏幕的装饰框，保留）
        pygame.draw.rect(screen, (24, 24, 30), (0, 0, screen.get_width(), screen.get_height()), 8)

    def draw_form(self, screen):
        panel_x = 430
        title = get_ui_font(38).render("创建角色", True, (255, 255, 255))
        screen.blit(title, (panel_x, 76))

        label = get_ui_font(22).render("姓名", True, (230, 230, 230))
        screen.blit(label, (panel_x, 160))
        self.name_rect.topleft = (panel_x, 194)
        pygame.draw.rect(screen, (245, 245, 245), self.name_rect)
        pygame.draw.rect(screen, (30, 30, 30), self.name_rect, 2)

        display_name = self.name if self.name else "点击输入姓名"
        text_color = (20, 20, 20) if self.name else (135, 135, 135)
        name_surf = get_ui_font(24).render(display_name, True, text_color)
        screen.blit(name_surf, (self.name_rect.x + 14, self.name_rect.y + 11))

        rule = get_ui_font(16).render("最多 8 个中文或 16 个英文字符", True, (210, 210, 210))
        screen.blit(rule, (panel_x, 250))
        if self.name_error:
            error = get_ui_font(16).render(self.name_error, True, (255, 160, 120))
            screen.blit(error, (panel_x, 272))

        gender_label = get_ui_font(22).render("性别", True, (230, 230, 230))
        screen.blit(gender_label, (panel_x, 300))
        self.male_rect.topleft = (panel_x, 334)
        self.female_rect.topleft = (panel_x + 150, 334)
        self.draw_choice(screen, self.male_rect, "男", self.gender == "男")
        self.draw_choice(screen, self.female_rect, "女", self.gender == "女")

        # 宿舍选择
        dorm_label = get_ui_font(22).render("宿舍", True, (230, 230, 230))
        screen.blit(dorm_label, (panel_x, 390))

        # 宿舍选择容器背景
        container_rect = pygame.Rect(panel_x, 420, 320, 50)
        pygame.draw.rect(screen, (46, 52, 68), container_rect)
        pygame.draw.rect(screen, (230, 230, 230), container_rect, 2)

        # 左箭头按钮
        self.left_arrow_rect = pygame.Rect(panel_x + 10, 430, 40, 30)
        pygame.draw.rect(screen, (70, 90, 130), self.left_arrow_rect)
        pygame.draw.rect(screen, (230, 230, 230), self.left_arrow_rect, 2)
        left_arrow_surf = get_ui_font(24).render("◀", True, (255, 255, 255))
        screen.blit(left_arrow_surf, (self.left_arrow_rect.centerx - left_arrow_surf.get_width() // 2,
                                      self.left_arrow_rect.centery - left_arrow_surf.get_height() // 2))

        # 右箭头按钮
        self.right_arrow_rect = pygame.Rect(panel_x + 270, 430, 40, 30)
        pygame.draw.rect(screen, (70, 90, 130), self.right_arrow_rect)
        pygame.draw.rect(screen, (230, 230, 230), self.right_arrow_rect, 2)
        right_arrow_surf = get_ui_font(24).render("▶", True, (255, 255, 255))
        screen.blit(right_arrow_surf, (self.right_arrow_rect.centerx - right_arrow_surf.get_width() // 2,
                                       self.right_arrow_rect.centery - right_arrow_surf.get_height() // 2))

        # 当前宿舍名称（居中显示在容器内）
        dorm_text = self.dormitories[self.dormitory_index]
        dorm_surf = get_ui_font(24).render(dorm_text, True, (255, 255, 255))
        dorm_x = container_rect.centerx - dorm_surf.get_width() // 2
        dorm_y = container_rect.centery - dorm_surf.get_height() // 2
        screen.blit(dorm_surf, (dorm_x, dorm_y))

        self.confirm_rect.topleft = (panel_x, 500)
        self.draw_confirm(screen)

    def draw_choice(self, screen, rect, text, selected):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        bg_color = (235, 235, 235) if selected else (70, 70, 78)
        text_color = (20, 20, 20) if selected else (235, 235, 235)
        border_color = (255, 205, 90) if hovered else (255, 255, 255)
        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, border_color, rect, 2)
        text_surf = get_ui_font(24).render(text, True, text_color)
        text_x = rect.x + (rect.width - text_surf.get_width()) // 2
        text_y = rect.y + (rect.height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))

    def draw_confirm(self, screen):
        enabled = self.can_confirm()
        hovered = enabled and self.confirm_rect.collidepoint(pygame.mouse.get_pos())
        bg_color = (210, 210, 210) if enabled else (70, 70, 70)
        text_color = (20, 20, 20) if enabled else (145, 145, 145)
        border_color = (255, 205, 90) if hovered else (255, 255, 255)
        pygame.draw.rect(screen, bg_color, self.confirm_rect)
        pygame.draw.rect(screen, border_color, self.confirm_rect, 2)
        text_surf = get_ui_font(24).render("确认并进入校园", True, text_color)
        text_x = self.confirm_rect.x + (self.confirm_rect.width - text_surf.get_width()) // 2
        text_y = self.confirm_rect.y + (self.confirm_rect.height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))
