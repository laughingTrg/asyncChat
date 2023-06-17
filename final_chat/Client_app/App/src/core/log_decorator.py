import inspect
import time


class Log():
    def __init__(self, logger) -> None:
        self.logger = logger

    def __call__(self, func):
        def decorated(*args, **kwargs):
            dt = time.ctime(time.time())

            self.logger.info(f'Была вызвана функция {func.__name__} c параметрами {args} , {kwargs}. Вызов из модуля {func.__module__}')
            res = func(*args, **kwargs)
            return res
        return decorated