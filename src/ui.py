import pygame
from src.config import font2_path

_font_cache = {}


def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(font2_path, size)
    return _font_cache[size]


def draw_prompt(screen, text):
    if not text:
        return
    font = get_font(24)
    text_surf = font.render(text, True, (255, 255, 255))
    padding = 20
    bg_width = text_surf.get_width() + padding * 2
    bg_height = text_surf.get_height() + padding
    bg_rect = pygame.Rect(0, 0, bg_width, bg_height)
    bg_rect.centerx = screen.get_width() // 2
    bg_rect.top = 30

    # 半透明背景
    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))
    screen.blit(bg_surface, bg_rect.topleft)

    text_x = bg_rect.x + padding
    text_y = bg_rect.y + padding // 2
    screen.blit(text_surf, (text_x, text_y))

def draw_dialog_box(screen, text):
    if not text:
        return
    font = get_font(24)
    text_surf = font.render(text, True, (255, 255, 255))
    padding = 20
    box_width = screen.get_width() - 100
    box_height = 80
    box_x = 50
    box_y = screen.get_height() - box_height - 30

    # 半透明背景
    bg_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 200))
    screen.blit(bg_surface, (box_x, box_y))

    # 白色边框
    pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 2)

    # 文字（左对齐，垂直居中）
    text_x = box_x + padding
    text_y = box_y + (box_height - text_surf.get_height()) // 2
    screen.blit(text_surf, (text_x, text_y))
