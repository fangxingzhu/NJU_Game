import pygame
import os
import subprocess

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

    def reset(self):
        self.name = ""
        self.gender = "男"
        self.name_error = ""
        self.created_player_data = None

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Scene.START
                if event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pygame.K_RETURN and self.can_confirm():
                    self.created_player_data = PlayerData(self.name.strip(), self.gender)
                    return Scene.OVERWORLD

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.name_rect.collidepoint(event.pos):
                    self.open_name_dialog()
                elif self.male_rect.collidepoint(event.pos):
                    self.gender = "男"
                elif self.female_rect.collidepoint(event.pos):
                    self.gender = "女"
                elif self.confirm_rect.collidepoint(event.pos) and self.can_confirm():
                    self.created_player_data = PlayerData(self.name.strip(), self.gender)
                    return Scene.OVERWORLD
        return None

    def name_length(self, text):
        length = 0
        for char in text.strip():
            length += 2 if ord(char) > 127 else 1
        return length

    def can_confirm(self):
        return bool(self.name.strip()) and self.name_length(self.name) <= 16

    def open_name_dialog(self):
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
            return

        if result.returncode != 0:
            self.name_error = "姓名输入窗口返回错误"
            return

        value = result.stdout.strip()
        if not value:
            return

        if self.name_length(value) > 16:
            self.name_error = "姓名最多 8 个中文或 16 个英文字符"
            return

        self.name = value
        self.name_error = ""

    def draw(self, screen):
        self.draw_portrait_background(screen)
        self.draw_form(screen)

    def draw_portrait_background(self, screen):
        if self.gender == "男":
            bg_color = (40, 84, 104)
            portrait_color = (92, 178, 196)
        else:
            bg_color = (104, 58, 92)
            portrait_color = (214, 136, 180)

        screen.fill(bg_color)
        pygame.draw.rect(screen, portrait_color, (70, 92, 260, 420))
        pygame.draw.circle(screen, (235, 220, 208), (200, 155), 58)
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

        self.confirm_rect.topleft = (panel_x, 450)
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
