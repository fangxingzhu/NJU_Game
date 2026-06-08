import pygame
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

    def enter(self, player_data=None):
        self.player_data = player_data
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

    def draw_menu_hint(self, screen):
        text_surf = get_ui_font(16).render("按 ESC 打开菜单", True, (60, 60, 60))
        padding = 10
        x = screen.get_width() - text_surf.get_width() - padding
        y = screen.get_height() - text_surf.get_height() - padding
        screen.blit(text_surf, (x, y))
