import os
import pygame

from src.config import TILE_SIZE, PLAYER_SPEED, COLOR_PLAYER


class Player:
    DIRECTION_ROW = {
        "down": 0,
       "right": 1,
       "left": 2,
        "up": 3,
    }

    def __init__(self, x, y, gender="男"):
        self.x = x
        self.y = y

        self.width = TILE_SIZE-8
        self.height = TILE_SIZE-8
        self.speed = PLAYER_SPEED

        self.direction = "down"
        self.gender = gender

        self.frame_index = 0
        self.anim_timer = 0
        self.anim_delay = 8
        self.moving = False

        self.animations = self.load_animations()

    def set_gender(self, gender):
        if self.gender != gender:
            self.gender = gender
            self.animations = self.load_animations()

    def load_animations(self):
        if self.gender == "男":
            filename = "boy_walk.png"
            frame_size = 313
        else:
            filename = "girl_walk.png"
            frame_size = 256

        image_path = os.path.join("assets", "images", filename)

        if not os.path.exists(image_path):
            print(f"找不到角色图片：{image_path}")
            return None

        sprite_sheet = pygame.image.load(image_path).convert_alpha()

        animations = {
            "down": [],
            "left": [],
            "right": [],
            "up": [],
        }

        for direction, row in self.DIRECTION_ROW.items():
            for col in range(4):
                frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)

                frame.blit(
                    sprite_sheet,
                    (0, 0),
                    (
                        col * frame_size,
                        row * frame_size,
                        frame_size,
                        frame_size,
                    ),
                )

                frame = pygame.transform.scale(frame, (80, 80))
                animations[direction].append(frame)

        return animations

    def move(self, dx, dy, game_map):
        # 1. 尝试同时移动X和Y
        if dx == 0 and dy == 0:
            self.moving = False
            self.frame_index = 0
            return

        # 检测在某个偏移下的碰撞（不考虑方向收缩，保持16x16原始大小）
        def can_move(offset_x, offset_y):
            nx = self.x + offset_x
            ny = self.y + offset_y
            # 四个角
            corners = [
                (nx, ny),
                (nx + self.width - 1, ny),
                (nx, ny + self.height - 1),
                (nx + self.width - 1, ny + self.height - 1)
            ]
            for cx, cy in corners:
                col = int(cx // TILE_SIZE)
                row = int(cy // TILE_SIZE)
                if not game_map.is_walkable(col, row):
                    return False
            return True

        # 尝试完全移动
        if can_move(dx, dy):
            self.x += dx
            self.y += dy
            success = True
        else:
            # 2. 分别尝试只移动X或只移动Y（滑动）
            can_x = can_move(dx, 0)
            can_y = can_move(0, dy)

            if can_x:
                self.x += dx
            if can_y:
                self.y += dy
            success = can_x or can_y

        # 更新朝向和动画（仅当有移动）
        if success and (dx != 0 or dy != 0):
            self.moving = True
            if dx > 0:
                self.direction = "right"
            elif dx < 0:
                self.direction = "left"
            elif dy > 0:
                self.direction = "down"
            elif dy < 0:
                self.direction = "up"

            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % 4
        else:
            self.moving = False
            self.frame_index = 0
            self.anim_timer = 0

    def draw(self, screen, camera_x=0, camera_y=0):
        if not self.animations:
            draw_x = self.x - camera_x
            draw_y = self.y - camera_y
            pygame.draw.rect(screen, COLOR_PLAYER, (draw_x, draw_y, self.width, self.height))
            return

        frame = self.animations[self.direction][self.frame_index]

        draw_x = self.x - camera_x - 24
        draw_y = self.y - camera_y - 48

        screen.blit(frame, (draw_x, draw_y))
