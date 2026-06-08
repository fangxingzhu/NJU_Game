import os
import pygame
from src.config import TILE_SIZE, PLAYER_SPEED


class Player:
    DOWN = 0
    RIGHT = 1
    LEFT = 2
    UP = 3

    def __init__(self, x, y, gender="female"):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = PLAYER_SPEED

        self.gender = gender
        self.direction = self.DOWN
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_delay = 4
        self.moving = False

        self.animations = self.load_animations()

    def load_animations(self):
        data = {
            "female": {"file": "girl_walk.png", "frame_size": 256},
            "male": {"file": "boy_walk.png", "frame_size": 313},
        }.get(self.gender, {"file": "girl_walk.png", "frame_size": 256})

        path = os.path.join("assets", "images", data["file"])
        sheet = pygame.image.load(path).convert_alpha()

        frame_size = data["frame_size"]
        animations = {
            self.DOWN: [],
            self.LEFT: [],
            self.RIGHT: [],
            self.UP: [],
        }

        for row in range(4):
            for col in range(4):
                frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
                frame.blit(
                    sheet,
                    (0, 0),
                    (col * frame_size, row * frame_size, frame_size, frame_size)
                )
                frame = pygame.transform.scale(frame, (80, 80))
                animations[row].append(frame)

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
            self.direction = self.RIGHT
        elif dx < 0:
            self.direction = self.LEFT
        elif dy > 0:
            self.direction = self.DOWN
        elif dy < 0:
            self.direction = self.UP

        if self.moving:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_delay:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % 4
        else:
            self.frame_index = 0
            self.anim_timer = 0

    def draw(self, screen, camera_x=0, camera_y=0):
        frame = self.animations[self.direction][self.frame_index]

        draw_x = self.x - camera_x - 24
        draw_y = self.y - camera_y - 48

        screen.blit(frame, (draw_x, draw_y))