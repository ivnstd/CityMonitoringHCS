import logging
from colorlog import ColoredFormatter


# Настройки цветов для уровней логирования
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-9s%(reset)s %(message)s",
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
logger = logging.getLogger("supervisor")
logger.setLevel(logging.DEBUG)

# Поток для вывода
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Добавление потока в логгер
logger.addHandler(stream_handler)

# # Примеры логирования с разными уровнями
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")
