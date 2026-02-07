from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select
from database import get_db, engine, Base
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from models import FileModel
from schemas import FileSchema
import logging
import queue


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # в консоль
        logging.FileHandler('service.log')  # в файл
    ]
)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Сервис мониторинга папки",
    version="1.0.0",
    description="Сервис для мониторинга и обработки текстовых файлов в папке",
    docs_url="/"
)

@app.get("/health", summary='Проверить подключение к бд', tags=['Files'])
def health(db: Session = Depends(get_db)):
    """Проверяет подключение к бд"""
    result = db.scalar(select(1))
    if result != 1:
        raise HTTPException(status_code=503, detail='Соединение с БД не установленно!')

    return {"status":"ok"}

@app.get("/stats", summary='Cтатистика по обработке файлов', tags=['Files'])
def get_stats(db: Session = Depends(get_db)):
    """
    Возвращает статистику по обработке файлов
    """

    total = db.query(FileModel).count()
    ok = db.query(FileModel).filter_by(status="OK").count()
    failed = db.query(FileModel).filter_by(status="FAILED").count()
    queued = 0
    file_queue = getattr(app.state, 'file_queue', None)
    if file_queue:
        queued = file_queue.qsize()

    return {
        "total": total,
        "ok": ok,
        "failed": failed,
        "queued": queued
    }

@app.get('/files', summary='Получить последние 20 записей', tags=['Files'], response_model=list[FileSchema])
def last_20_lines(db: Session = Depends(get_db)):
    """Получает последне 20 записей из БД"""
    result = db.scalars(
        select(FileModel).order_by(desc('created_at')).limit(20)
    ).all()
    return result

if __name__ == '__main__':
    import uvicorn
    import threading
    from watcher import start_watcher
    from processor import worker_loop
    from config import settings

    file_queue = queue.Queue()
    app.state.file_queue = file_queue
    logger.info(f"Очередь создана, размер: {file_queue.qsize()}")

    logger.info(f"Запуск Watcher для папки: {settings.WATCH_PATH}")
    watcher_thread = threading.Thread(
        target=start_watcher,
        args=(file_queue, settings.WATCH_PATH),
        daemon=True,
        name="watcher-thread"
    )
    watcher_thread.start()
    logger.info("Watcher запущен")

    logger.info("Запуск Worker для обработки файлов...")
    worker_thread = threading.Thread(
        target=worker_loop,
        args=(file_queue,),
        daemon=True,
        name="worker-thread"
    )
    worker_thread.start()
    logger.info("Worker запущен")

    uvicorn.run(app)
