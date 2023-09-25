
class GameStats:
    '''Отслеживание статистики для игры'''

    def __init__(self, ai_game):
        '''Инициализация статистики'''
        self.settings = ai_game.settings
        self.reset_stats()

    def reset_stats(self):
        '''Статистика в ходе игры'''
        self.ship_left = self.settings.ship_limit