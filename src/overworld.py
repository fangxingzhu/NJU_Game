import pygame
from src.config import Scene,TILE_SIZE,MAP_COLS,MAP_ROWS,MAP_DISPLAY_SCALE
from src.map import GameMap
from src.player import Player
from src.building import BuildingManager
from src.ui import draw_prompt


class Overworld:
    def __init__(self):
        self.map = GameMap("data/map.json")
        # 玩家初始位置：道路区域，例如第1列第1行的格子左上角（32,32）
        if self.map.player_start:
            self.player = Player(self.map.player_start[0], self.map.player_start[1])
        else:
            self.player = Player(TILE_SIZE, TILE_SIZE)
        self.building_manager = BuildingManager(self.map)
        self.nearby_building = None

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
        scale = MAP_DISPLAY_SCALE
        visible_width = screen.get_width() / scale
        visible_height = screen.get_height() / scale

        # 计算摄像机偏移，让玩家始终保持在屏幕中央
        camera_x = self.player.x - (visible_width / 2) + (self.player.width / 2)
        camera_y = self.player.y - (visible_height / 2) + (self.player.height / 2)

        # 限制摄像机不超出地图边界
        max_camera_x = self.map.width - visible_width
        max_camera_y = self.map.height - visible_height
        camera_x = max(0, min(camera_x, max_camera_x))
        camera_y = max(0, min(camera_y, max_camera_y))

        self.map.draw(screen, camera_x, camera_y, scale)
        self.player.draw(screen, camera_x, camera_y, scale)
        if self.nearby_building:
            prompt = f"按 E 进入{self.nearby_building['name']}"
        else:
            prompt = ""
        draw_prompt(screen, prompt)
