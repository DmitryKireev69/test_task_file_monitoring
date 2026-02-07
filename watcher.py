import os
import re
import time
import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class FileHandler(FileSystemEventHandler):
    def __init__(self, queue, watch_path):
        self.queue = queue
        self.watch_path = watch_path
        self.pattern = re.compile(r'^test_\d+\.txt$')

    def on_created(self, event):
        if not event.is_directory:
            self._handle_file(event.src_path, "created")

    def on_moved(self, event):
        if not event.is_directory:
            self._handle_file(event.dest_path, "moved")

    def _handle_file(self, filepath, event_type):
        filename = os.path.basename(filepath)

        if not self.pattern.match(filename):
            return

        logger.info(f"Найден файл: {filename} (event: {event_type})")

        if self._wait_for_stable(filepath):
            self.queue.put(filepath)
            logger.info(f"Файл добавлен в очередь: {filename}")
        else:
            logger.error(f"Файл не стабильный: {filename}")

    @staticmethod
    def _wait_for_stable(filepath, check_interval=2, max_checks=5):
        """Защита от недописанного файла"""
        try:
            prev_size = -1
            for i in range(max_checks):
                if os.path.exists(filepath):
                    curr_size = os.path.getsize(filepath)
                    if curr_size == prev_size and prev_size != -1:
                        return True
                    prev_size = curr_size
                time.sleep(check_interval)
            return False
        except Exception as e:
            logger.error(f"Ошибка проверка файла на стабильность: {e}")
            return False


def start_watcher(queue, watch_path):
    """Запускает наблюдатель файловой системы"""

    event_handler = FileHandler(queue, watch_path)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()
    logger.info(f"Наблюдатель запущен по пути {watch_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
