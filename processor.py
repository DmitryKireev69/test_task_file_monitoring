import time
import os
import logging
from datetime import datetime

from database import get_db_session
from models import FileModel
logger = logging.getLogger(__name__)


def process_file(filepath):
    """Обработка одного файла"""
    try:
        encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin-1', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            raise UnicodeDecodeError("Не удалось определить кодировку файла")

        lines = content.count('\n') + (1 if content else 0)

        return {
            'path': filepath,
            'status': 'OK',
            'lines': lines,
            'error': None,
            'created_at': datetime.now(),
            'processed_at': datetime.now()
        }
    except Exception as e:
        return {
            'path': filepath,
            'status': 'FAILED',
            'lines': None,
            'error': str(e),
            'created_at': datetime.now(),
            'processed_at': None
        }


def save_result(result):
    """Сохранение результата в БД"""
    with get_db_session() as conn:
        file = FileModel(**result)
        conn.add(file)


def process_file_with_retry(filepath, max_retries=3):
    """Обработка с повторными попытками"""
    retry_delays = [1, 3, 5]

    for attempt in range(max_retries):
        try:
            result = process_file(filepath)
            save_result(result)
            logger.info(f"Файл обработан: {os.path.basename(filepath)} - статус: {result['status']}")
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                delay = retry_delays[attempt]
                logger.warning(f"Повторная попытка {attempt+1} для {filepath} через {delay} секунд")
                time.sleep(delay)
            else:
                logger.error(f"Не удалось обработать после {max_retries} попыток: {filepath}")
                logger.error(f"Ошибка: {e}")
                return False


def worker_loop(queue):
    """Основной цикл worker"""
    logger.info("Воркер по обработке файлов запущен")
    while True:
        try:
            filepath = queue.get()
            logger.info(f"Начинаю обработку файла: {filepath}")
            process_file_with_retry(filepath)
            queue.task_done()
        except Exception as e:
            logger.error(f"Ошибка в worker: {e}")
