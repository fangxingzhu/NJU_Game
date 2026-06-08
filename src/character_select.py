import pygame
from src.config import Scene, font1_path, font2_path


class CharacterSelect:
    def __init__(self):
        self.title_font = pygame.font.Font(font1_path, 48)
        self.text_font = pygame.font.Font(font2_path, 28)
        self.selected_gender = "female"

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_gender = "female"
                elif event.key == pygame.K_RIGHT:
                    self.selected_gender = "male"
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    return Scene.OVERWORLD
                elif event.key == pygame.K_ESCAPE:
                    return Scene.START
        return None

    def draw(self, screen):
        screen.fill((20, 20, 40))

        title = self.title_font.render("选择角色", True, (255, 255, 255))
        screen.blit(title, ((screen.get_width() - title.get_width()) // 2, 100))

        female_color = (255, 220, 120) if self.selected_gender == "female" else (180, 180, 180)
        male_color = (255, 220, 120) if self.selected_gender == "male" else (180, 180, 180)

        female_text = self.text_font.render("← 女生", True, female_color)
        male_text = self.text_font.render("男生 →", True, male_color)

        screen.blit(female_text, (220, 260))
        screen.blit(male_text, (460, 260))

        tip = self.text_font.render("左右键选择，空格/回车确认", True, (220, 220, 220))
        screen.blit(tip, ((screen.get_width() - tip.get_width()) // 2, 380))