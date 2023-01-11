import sys
import logging
import traceback
import inspect
from log import server_log_config, client_log_config
from functools import wraps

if sys.argv[0].find('server') == -1:
    LOGGER = logging.getLogger('client.main')
else:
    LOGGER = logging.getLogger('server.main')


def log(func):
    """
    Decorator of function to log name and parameters of executed function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        LOGGER.info(f'Функция {func.__name__} c параметрами'
                           f'{args}, {kwargs} была вызвана из'
                           f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                           f'Вызов из функции {inspect.stack()[1][3]}')
        return res
    return wrapper