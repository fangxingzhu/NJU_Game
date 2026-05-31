import pygame
from src.config import TILE_SIZE

class BuildingManager:
    def __init__(self, game_map):
        self.buildings = game_map.buildings

    def check_nearby(self, player_rect):
        for b in self.buildings:
            bx, by, bw, bh = b['rect']
            building_rect = pygame.Rect(bx * TILE_SIZE, by * TILE_SIZE,
                                        bw * TILE_SIZE, bh * TILE_SIZE)
            trigger_rect = building_rect.inflate(32, 32)   # 触发范围比建筑大一圈
            if trigger_rect.colliderect(player_rect):
                return b
        return None