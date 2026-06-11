import pygame
import os
from src.config import Scene,TILE_SIZE,MAP_COLS,MAP_ROWS
from src.map import GameMap
from src.player import Player
from src.building import BuildingManager
from src.ui import draw_prompt, get_ui_font
from src.ui import draw_time_ui


class Overworld:
    def __init__(self):
        self.map = GameMap("data/map.json")
        # 玩家初始位置：道路区域，例如第24行20列
        self.player = Player(19*TILE_SIZE, 23*TILE_SIZE)
        self.player_data = None
        self.building_manager = BuildingManager(self.map)
        self.nearby_building = None
        self.time_system = None
        self.music_manager = None
        self.map_day = pygame.image.load("assets/images/overworld_daytime.png").convert()
        self.map_night = pygame.image.load("assets/images/overworld_nighttime.png").convert()


    def enter(self, player_data=None, time_system=None, music_manager=None):
        self.player_data = player_data
        self.time_system = time_system
        self.music_manager = music_manager

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

        # 合并事件处理
        for event in events:
            # 鼠标点击音乐按钮
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                music_rect = pygame.Rect(10, 10, 40, 40)
                if music_rect.collidepoint(mouse_pos):
                    if self.music_manager:
                        self.music_manager.toggle()

            # 键盘按键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and self.nearby_building:
                    return Scene.BUILDING

        return None

    def draw(self, screen):
        # 摄像机计算（保持不变）
        camera_x = self.player.x - (screen.get_width() // 2) + (self.player.width // 2)
        camera_y = self.player.y - (screen.get_height() // 2) + (self.player.height // 2)
        max_camera_x = MAP_COLS * TILE_SIZE - screen.get_width()
        max_camera_y = MAP_ROWS * TILE_SIZE - screen.get_height()
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        # 绘制地图背景（替换原来的色块绘制）
        if self.time_system and self.time_system.is_night():
            screen.blit(self.map_night, (-camera_x, -camera_y))
        else:
            screen.blit(self.map_day, (-camera_x, -camera_y))

        # 绘制玩家、提示、时间等（保持不变）
        self.player.draw(screen, camera_x, camera_y)
        if self.nearby_building:
            prompt = f"按 E 进入{self.nearby_building['name']}"
        else:
            prompt = ""
        draw_prompt(screen, prompt)
        self.draw_menu_hint(screen)
        draw_time_ui(screen, self.time_system)
        self.draw_music_button(screen)

    def draw_menu_hint(self, screen):
        text_surf = get_ui_font(16).render("按 ESC 打开菜单", True, (60, 60, 60))
        padding = 10
        x = screen.get_width() - text_surf.get_width() - padding
        y = screen.get_height() - text_surf.get_height() - padding
        screen.blit(text_surf, (x, y))

    def draw_music_button(self, screen):
        if not self.music_manager:
            return
        font = get_ui_font(24)

        icon = "♪"
        if not self.music_manager.is_enabled():
            icon = "×"

        button_rect = pygame.Rect(
            10,
            10,
            40,
            40
        )

        pygame.draw.rect(
            screen,
            (88, 58, 120),
            button_rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (245,230,160),
            button_rect,
            2,
            border_radius=8
        )

        text = font.render(icon, True, (255,255,255))

        screen.blit(
            text,
            (
                button_rect.centerx - text.get_width()//2,
                button_rect.centery - text.get_height()//2
            )
        )

