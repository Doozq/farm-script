import logging
from pathlib import Path

# Директория для логов
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Основные файлы логов
general_log_file = log_dir / "general.log"
error_log_file = log_dir / "errors.log"

# Форматтер для логов
format_string = "[%(asctime)s] [%(levelname)-8s] [%(threadName)-15s] - %(message)s"
formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

# Настройка корневого логгера
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Обработчик для общего лога
general_handler = logging.FileHandler(general_log_file, mode='a')
general_handler.setFormatter(formatter)
root_logger.addHandler(general_handler)

# Обработчик для ошибок
error_handler = logging.FileHandler(error_log_file, mode='a')
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)  # Только ошибки
root_logger.addHandler(error_handler)