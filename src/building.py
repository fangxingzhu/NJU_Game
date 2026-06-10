import pygame
from src.config import TILE_SIZE

class BuildingManager:
    def __init__(self, game_map):
        self.buildings = game_map.buildings

    def check_nearby(self, player_rect):
        for b in self.buildings:
            # 获取所有碰撞矩形，支持 rects 或 rect
            rect_list = b.get('rects')
            if not rect_list:
                # 兼容旧版单个 rect
                rect_list = [b['rect']] if 'rect' in b else []

            for r in rect_list:
                bx, by, bw, bh = r
                building_rect = pygame.Rect(
                    bx * TILE_SIZE, by * TILE_SIZE,
                    bw * TILE_SIZE, bh * TILE_SIZE
                )
                trigger_rect = building_rect.inflate(32, 32)  # 触发范围
                if trigger_rect.colliderect(player_rect):
                    return b
        return None