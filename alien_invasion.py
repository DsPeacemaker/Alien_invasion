import sys
import pygame
from time import sleep
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button


class AlienInvasion:
    ''' Класс для управления ресурсами и поведением игры.'''
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')
        # Создание экземпляра для хранения игровой статистики
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # назначение цвета фона
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Создание кнопки Play
        self.play_button = Button(self, "Play")

    def run_game(self):
        '''Запуск основного цикла игры'''
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_aliens()
                self._update_bullets()

            self._update_screen()

            # При каждом проходе цикла перерисовывается экран
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()
            # отображение последнего отрисованного экрана
            #pygame.display.flip()


    def _check_events(self):
        '''Обрабатывает события клавиатуры и мыши'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        '''Запускает игру при нажатии кнопки Play'''
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Сброс игровых настроек
            self.settings.initialize_dynamic_settings()
            # Сброс игровой статистики
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.stats.game_active = True

            # Очистка списков прищельцев и снарядов
            self.bullets.empty()
            self.aliens.empty()

            # Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()

            # Указатель мыши скрывается после нажатия
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        '''Реагирует на нажатие клавиш'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        '''Реагирует на отпускание клавиш'''
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        '''Создание нового снаряда и включение его в группу bullets'''
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        '''Обновляет позиции снарядов и уничтожает старые снаряды'''
        # Обновление позиции снарядов.
        self.bullets.update()

        # Удаление снарядов, вышедших за край экрана
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _create_fleet(self):
        '''Создание флота вторжения'''
        # Создание пришельца и вычисление количества пришельцев в ряду
        # Интервал между двумя пришельцами равен ширине пришельца
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien_width = alien.rect.width
        avaliable_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = avaliable_space_x // (2 * alien_width)
        '''Определяет количество рядов, помещающихся на экран'''
        ship_height = self.ship.rect.height
        avaliable_space_y = (self.settings.screen_height - (4 * alien_height) - ship_height)
        number_rows = avaliable_space_y // (2 * alien_height)

        # Создание флота вторжения
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_fleet_alien(alien_number, row_number)

    def _check_bullet_alien_collisions(self):
        '''Обработка коллизий снарядов с пришельцами'''
        # Проверка попаданий пришельцев.
        # При обнаружении попадания удалить снаряд и пришельца
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Создание нового флота и уничтожение старых снарядов
            self._create_fleet()
            self.bullets.empty()
            self.settings.increase_speed()

            # Увеличение уровня
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        '''Проверяет достиг ли флот края экрана и
        Обновляет позиции всех пришельцев во флоте'''
        self._check_fleet_edges()
        self.aliens.update()

        # Проверка коллизий 'чужой - корабль'
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Проверка коллизий "чужой-низ экрана"
        self._check_aliens_bottom()

    def _update_screen(self):
        '''Обновляет изображения на экране и отображает новый экран'''
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # Вывод информации о счете
        self.sb.show_score()

        # Кнопка отображается в том случае, если игра неактивна
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _create_fleet_alien(self, alien_number, row_number):
        '''Создание пришельца и размещение его в ряду'''
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _change_fleet_direction(self):
        '''Опускает весь флот и меняет направление флота'''
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_fleet_edges(self):
        '''Реагирует на достижение пришельцем края экрана'''
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _ship_hit(self):
        '''Обрабатывает столкновение корабля с пришельцем'''
        if self.stats.ship_left > 0:
            self.stats.ship_left -= 1
            # Очистка списков пришельцев и снарядов
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и размещение корабля в центре
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)

        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        '''проверяет добрались ли чужие до нижнего края экрана'''
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Проходит то же, что при столкновении с кораблем
                self._ship_hit()
                break


if __name__ == '__main__':
    # Создание экземпляра и запсук игры
    ai = AlienInvasion()
    ai.run_game()
