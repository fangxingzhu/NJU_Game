import pygame
from src.config import font2_path

def draw_prompt(screen, text):
    if not text:
        return
    font = pygame.font.Font(font2_path, 24)
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