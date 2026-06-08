import pygame
import os
from src.config import Scene,TILE_SIZE,MAP_COLS,MAP_ROWS
from src.map import GameMap
from src.player import Player
from src.building import BuildingManager
from src.ui import draw_prompt, get_ui_font



class Overworld:
    def __init__(self):
        self.map = GameMap("data/map.json")
        # 玩家初始位置：道路区域，例如第1列第1行的格子左上角（32,32）
        self.player = Player(TILE_SIZE, TILE_SIZE)
        self.player_data = None
        self.building_manager = BuildingManager(self.map)
        self.nearby_building = None
        self.time_system = None
        self.sun_icon = pygame.image.load(
            "assets/images/sun_icon.png"
        ).convert_alpha()

        self.moon_icon = pygame.image.load(
            "assets/images/moon_icon.png"
        ).convert_alpha()

        self.sun_icon = pygame.transform.scale(
            self.sun_icon,
            (36, 36)
        )

        self.moon_icon = pygame.transform.scale(
            self.moon_icon,
            (36, 36)
        )

    def enter(self, player_data=None, time_system=None):
        self.player_data = player_data
        self.time_system = time_system

        if player_data:
            self.player.x = player_data.x
            self.player.y = player_data.y
            self.player.direction = player_data.direction
            self.player.set_gender(player_data.gender)

    def update(self, events):
        # 处理连续按键（移动）
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.player.speed
        if keys[pygame.K_RIGHT]:
            dx = self.player.speed
        if keys[pygame.K_UP]:
            dy = -self.player.speed
        if keys[pygame.K_DOWN]:
            dy = self.player.speed
        self.player.move(dx, dy, self.map)
        if self.player_data:
            self.player_data.x = self.player.x
            self.player_data.y = self.player.y
            self.player_data.direction = self.player.direction
        player_rect = pygame.Rect(self.player.x, self.player.y,
                                  self.player.width, self.player.height)
        self.nearby_building = self.building_manager.check_nearby(player_rect)

        # 处理事件（切换场景）
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return Scene.START
                if event.key == pygame.K_e and self.nearby_building:
                    return Scene.BUILDING
        return None

    def draw(self, screen):
        # 计算摄像机偏移，让玩家始终保持在屏幕中央
        camera_x = self.player.x - (screen.get_width() // 2) + (self.player.width // 2)
        camera_y = self.player.y - (screen.get_height() // 2) + (self.player.height // 2)

        # 限制摄像机不超出地图边界
        max_camera_x = MAP_COLS * TILE_SIZE - screen.get_width()
        max_camera_y = MAP_ROWS * TILE_SIZE - screen.get_height()
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        self.map.draw(screen, camera_x, camera_y)
        self.player.draw(screen, camera_x, camera_y)
        if self.nearby_building:
            prompt = f"按 E 进入{self.nearby_building['name']}"
        else:
            prompt = ""
        draw_prompt(screen, prompt)
        self.draw_menu_hint(screen)
        self.draw_time_ui(screen)

    def draw_menu_hint(self, screen):
        text_surf = get_ui_font(16).render("按 ESC 打开菜单", True, (60, 60, 60))
        padding = 10
        x = screen.get_width() - text_surf.get_width() - padding
        y = screen.get_height() - text_surf.get_height() - padding
        screen.blit(text_surf, (x, y))

    def draw_time_ui(self, screen):
        if not self.time_system:
            return

        time_text = self.time_system.get_time_string()
        font = get_ui_font(20)
        if self.time_system.is_night():
            state_text = "夜晚"
            icon_surface = self.moon_icon
        else:
            state_text = "白天"
            icon_surface = self.sun_icon

        text_surf = font.render(
            f"{time_text}  {state_text}",
            True,
            (255,255,255)
        )
        padding = 10
        box_padding_y = 8
        icon_size = 36
        gap = 12

        box_width = text_surf.get_width() + icon_size + gap + 32
        box_height = max(icon_size, text_surf.get_height()) + box_padding_y * 2

        box_x = screen.get_width() - box_width - padding
        box_y = padding

        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

        pygame.draw.rect(screen, (24, 28, 42), box_rect)
        pygame.draw.rect(screen, (245, 230, 160), box_rect, 2)

        inner_rect = box_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (80, 88, 120), inner_rect, 1)

        icon_x = box_x + 16
        icon_y = box_y + (box_height - icon_size) // 2
        screen.blit(icon_surface, (icon_x, icon_y))

        text_x = icon_x + icon_size + gap
        text_y = box_y + (box_height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))
