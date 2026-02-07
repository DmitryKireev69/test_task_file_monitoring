# 1.Клонировать репозиторий:
```
git clone https://github.com/DmitryKireev69/test_task_file_monitoring.git
cd test_task_file_monitoring
```
# 2. Создать файл переменных окружения:
```   
В корне проекта есть шаблон:
.env.template
Создайте на его основе файл .env с указанием желаемых параметров:
 ```

# 3. Собрать и запустить
```
Создать окружене:
    Windows
    python -m venv .venv
    # Linux/Mac
    python3 -m venv .venv
Активировать:
    Windows
    .venv\Scripts\activate
    Linux/Mac
    source .venv/bin/activate
Установка зависимостей
    pip install -r requirements.txt
Запуск:
    python main.py
```