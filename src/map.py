import json
import pygame
from src.config import TILE_SIZE, MAP_COLS, MAP_ROWS, COLOR_BUILDING, COLOR_PATH, COLOR_ROAD


def _point_in_polygon(point, polygon):
    x, y = point
    inside = False
    count = len(polygon)
    if count < 3:
        return False
    j = count - 1
    for i in range(count):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1) + xi:
            inside = not inside
        j = i
    return inside


def _orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_intersect(a, b, c, d):
    def on_segment(p, q, r):
        return (
            min(p[0], r[0]) <= q[0] <= max(p[0], r[0])
            and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])
        )

    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)
    if o1 == 0 and on_segment(a, c, b):
        return True
    if o2 == 0 and on_segment(a, d, b):
        return True
    if o3 == 0 and on_segment(c, a, d):
        return True
    if o4 == 0 and on_segment(c, b, d):
        return True
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def _rect_collides_polygon(rect, polygon):
    if len(polygon) < 3:
        return False
    rect_points = [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.right, rect.bottom),
        (rect.left, rect.bottom),
    ]
    rect_edges = list(zip(rect_points, rect_points[1:] + rect_points[:1]))
    polygon_edges = list(zip(polygon, polygon[1:] + polygon[:1]))

    if any(_point_in_polygon(point, polygon) for point in rect_points):
        return True
    if any(rect.collidepoint(point) for point in polygon):
        return True
    return any(_segments_intersect(a, b, c, d) for a, b in rect_edges for c, d in polygon_edges)


class GameMap:
    def __init__(self, map_file):
        with open(map_file, 'r', encoding='utf-8') as f: #打开地图的json文件，只读，utf-8编码
            data = json.load(f) #得到一个存储json文件的字典
        self.mode = data.get('mode', 'tile')
        self.tiles = data.get('tiles', [])
        self.buildings = data['buildings']
        self.collisions = data.get('collisions', [])
        self.player_start = data.get('player_start')
        self.collision_mask = None
        self.width = data.get('image_size', [MAP_COLS * TILE_SIZE, MAP_ROWS * TILE_SIZE])[0]
        self.height = data.get('image_size', [MAP_COLS * TILE_SIZE, MAP_ROWS * TILE_SIZE])[1]
        self.background = None
        self.display_background = None
        background_path = data.get('background')
        if background_path:
            try:
                self.background = pygame.image.load(background_path).convert()
                self.width = self.background.get_width()
                self.height = self.background.get_height()
            except pygame.error:
                self.background = None
        collision_mask_path = data.get('collision_mask')
        if collision_mask_path:
            try:
                self.collision_mask = pygame.image.load(collision_mask_path).convert()
            except pygame.error:
                self.collision_mask = None

    def get_tile(self, col, row):
        """获取指定行列的图块编号（0=道路，1=建筑），越界返回1"""
        if 0 <= col < MAP_COLS and 0 <= row < MAP_ROWS:
            return self.tiles[row][col]
        return 1  # 边界外视为障碍

    def is_walkable(self, col, row):
        return self.get_tile(col, row) != 1

    def is_rect_walkable(self, rect):
        if rect.left < 0 or rect.top < 0 or rect.right > self.width or rect.bottom > self.height:
            return False
        if self.mode != 'pixel':
            corners = [
                (rect.left, rect.top),
                (rect.right - 1, rect.top),
                (rect.left, rect.bottom - 1),
                (rect.right - 1, rect.bottom - 1)
            ]
            for cx, cy in corners:
                col = int(cx // TILE_SIZE)
                row = int(cy // TILE_SIZE)
                if not self.is_walkable(col, row):
                    return False
            return True

        if self.collision_mask:
            sample_points = [
                (rect.left + 2, rect.top + 2),
                (rect.centerx, rect.top + 2),
                (rect.right - 3, rect.top + 2),
                (rect.left + 2, rect.centery),
                (rect.centerx, rect.centery),
                (rect.right - 3, rect.centery),
                (rect.left + 2, rect.bottom - 3),
                (rect.centerx, rect.bottom - 3),
                (rect.right - 3, rect.bottom - 3),
            ]
            for x, y in sample_points:
                if not (0 <= x < self.collision_mask.get_width() and 0 <= y < self.collision_mask.get_height()):
                    return False
                if self.collision_mask.get_at((int(x), int(y))).r > 128:
                    return False
            return True

        for item in self.collisions:
            if 'polygon' in item:
                bounds = pygame.Rect(item['rect'])
                if rect.colliderect(bounds) and _rect_collides_polygon(rect, item['polygon']):
                    return False
            elif rect.colliderect(pygame.Rect(item['rect'])):
                return False
        return True

    def draw(self, screen, camera_x, camera_y, scale=1.0):
        """绘制整张地图"""
        if self.background:
            if scale == 1:
                screen.blit(self.background, (-camera_x, -camera_y))
            else:
                scaled_size = (round(self.width * scale), round(self.height * scale))
                if self.display_background is None or self.display_background.get_size() != scaled_size:
                    self.display_background = pygame.transform.smoothscale(self.background, scaled_size)
                screen.blit(self.display_background, (-camera_x * scale, -camera_y * scale))
            return

        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                tile = self.tiles[row][col]
                x = (col * TILE_SIZE - camera_x) * scale
                y = (row * TILE_SIZE - camera_y) * scale
                size = max(1, round(TILE_SIZE * scale))
                if tile == 0:  # 道路
                    color = COLOR_PATH
                elif tile == 1:  # 建筑/墙壁
                    color = COLOR_BUILDING
                elif tile == 2:
                    color = COLOR_ROAD
                else:
                    color = (0, 0, 0)  # 未定义用黑色
                pygame.draw.rect(screen, color, (x, y, size, size))
