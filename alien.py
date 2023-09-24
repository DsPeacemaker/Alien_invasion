import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    '''Класс, представляющий одного пришельца'''

    def __init__(self, ai_game):
        super().__init__()
        self.settings = ai_game.settings
        self.screen = ai_game.screen

        # Загрузка изображения чужого и присвоение атрибута rect
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Каждый новый пришелец появляется в левом верхнем углу экрана
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Сохранение точной горизонтальной позиции пришельца
        self.x = float(self.rect.x)

    def update(self):
        '''Перемещает чужого вправо'''
        self.x += self.settings.alien_speed
        self.rect.x = self.x