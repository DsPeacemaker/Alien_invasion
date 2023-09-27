
class GameStats:
    '''Отслеживание статистики для игры'''

    def __init__(self, ai_game):
        '''Инициализация статистики'''
        self.settings = ai_game.settings
        self.reset_stats()
        # Игра запускается в неактивном состоянии
        self.game_active = False
        # Глобальный рекорд
        self.high_score = 1

    def reset_stats(self):
        '''Статистика в ходе игры'''
        self.ship_left = self.settings.ship_limit
        self.score = 0
        self.level = 1