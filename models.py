from datetime import datetime
from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class FileModel(Base):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, comment='Идентификатор файла')
    path: Mapped[str] = mapped_column(comment='Путь до файла')
    status: Mapped[str] = mapped_column(comment='Статус обработки')
    lines: Mapped[int] = mapped_column(comment='Количество строк в файле')
    error: Mapped[str | None] = mapped_column(comment='Текст ошибки обработки')
    created_at: Mapped[datetime] = mapped_column(comment='Дата и время создания файла')
    processed_at: Mapped[datetime | None] = mapped_column(comment='Дата и время завершения обработки файла')
