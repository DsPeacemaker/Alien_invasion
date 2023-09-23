import sys
import pygame
from settings import Settings
from ship import Ship


class AlienInvasion:
    # Класс для управления ресурсами и поведением игры.
    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')
        # назначение цвета фона
        self.bg_color = (230, 230, 230)
        self.ship = Ship(self)

    def run_game(self):
        '''Запуск основного цикла игры'''
        while True:
            self._check_events()
            self._update_screen()
            # При каждом проходе цикла перерисовывается экран
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()
            # отображение последнего отрисованного экрана
            pygame.display.flip()

    def _check_events(self):
        # Обрабатывает события клавиатуры и мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def _update_screen(self):
        '''Обновляет изображения на экране и отображает новый экран'''
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        pygame.display.flip()

if __name__ == '__main__':
    # Создание экземпляра и запсук игры
    ai = AlienInvasion()
    ai.run_game()
