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

        self.width = TILE_SIZE
        self.height = TILE_SIZE
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
        new_x = self.x + dx
        new_y = self.y + dy

        corners = [
            (new_x, new_y),
            (new_x + self.width - 1, new_y),
            (new_x, new_y + self.height - 1),
            (new_x + self.width - 1, new_y + self.height - 1),
        ]

        for cx, cy in corners:
            col = int(cx // TILE_SIZE)
            row = int(cy // TILE_SIZE)

            if not game_map.is_walkable(col, row):
                self.moving = False
                self.frame_index = 0
                return

        self.x = new_x
        self.y = new_y

        self.moving = dx != 0 or dy != 0

        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        if self.moving:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % 4
        else:
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
