import pygame
import sys
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, load_auto_save_setting, save_auto_save_setting
from src.scene_manager import SceneManager


def main():
    # 加载自动存档设置
    load_auto_save_setting()
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NJU_Game") #窗口名字
    clock = pygame.time.Clock()

    manager = SceneManager()

    while True:
        dt = clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: #窗口关闭事件（点击红叉）
                save_auto_save_setting()
                pygame.quit()
                sys.exit()

        if manager.update(events) == "quit":
            pygame.quit()
            sys.exit()
        manager.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
