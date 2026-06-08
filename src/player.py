import pygame
from src.config import TILE_SIZE, PLAYER_SPEED, COLOR_PLAYER


class Player:
    def __init__(self, x, y):
        self.x = x  # 像素坐标（左上角）
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = PLAYER_SPEED
        self.direction = "down"  # 朝向（以后可用于动画）

    def move(self, dx, dy, game_map):
        """尝试移动，dx、dy 为像素偏移量。game_map 用于碰撞检测"""
        new_x = self.x + dx
        new_y = self.y + dy

        # 检测新位置的四个角是否都在可行走区域
        corners = [
            (new_x, new_y),  # 左上角
            (new_x + self.width - 1, new_y),  # 右上角
            (new_x, new_y + self.height - 1),  # 左下角
            (new_x + self.width - 1, new_y + self.height - 1)  # 右下角
        ]

        for cx, cy in corners:
            col = int(cx // TILE_SIZE)
            row = int(cy // TILE_SIZE)
            if not game_map.is_walkable(col, row):
                return  # 有一个角不可行走，则不能移动

        # 所有角都可行走，更新位置
        self.x = new_x
        self.y = new_y

        # 更新朝向
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

    def draw(self, screen, camera_x=0, camera_y=0):
        """绘制玩家，camera_x/y 为摄像机偏移"""
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        pygame.draw.rect(screen, COLOR_PLAYER, (draw_x, draw_y, self.width, self.height))