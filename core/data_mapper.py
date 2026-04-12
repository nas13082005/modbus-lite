import yaml
import logging

logger = logging.getLogger(__name__)


def load_config(path: str) -> dict:
    """
    Загрузить YAML-конфиг из файла.
    Выбрасывает понятное исключение, если файл не найден или невалиден.
    """
    try:
        with open(path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info(f"Конфиг загружен: {path}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл конфига не найден: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Ошибка разбора конфига: {e}")
