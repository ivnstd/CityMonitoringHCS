import logging
from colorlog import ColoredFormatter


# Настройки цветов для уровней логирования
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)s%(reset)s:     [%(name)s] %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Создание логгера
logger = logging.getLogger("parser_service")
logger.setLevel(logging.DEBUG)

# Поток для вывода
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Добавление потока в логгер
logger.addHandler(stream_handler)
