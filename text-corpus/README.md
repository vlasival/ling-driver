# Text Corpus Management

Система управления корпусом текстов с интеграцией Neo4j.

## Быстрый старт

### 1. Настройка

Отредактируйте файл `config.env`:

```env
# Порты серверов
DJANGO_SERVER_PORT=8000      # Бэкенд (API)
WEB_INTERFACE_PORT=8001      # Фронтенд (веб-интерфейс)

# Neo4j настройки
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=123123123
NEO4J_DATABASE=corpus
```

### 2. Запуск

```bash
# Бэкенд (API сервер)
python3 backend.py

# Фронтенд (веб-интерфейс)
python3 frontend.py

# Остановка всех серверов
python3 stop.py
```

### 3. Доступ

- **API**: http://localhost:8000/api/
- **Веб-интерфейс**: http://localhost:8001/

## API Endpoints

### Корпуса
- `GET /api/corpus/` - список корпусов
- `POST /api/corpus/create/` - создание корпуса
- `GET /api/corpus/get/` - получение корпуса
- `PUT /api/corpus/update/` - обновление корпуса
- `DELETE /api/corpus/delete/` - удаление корпуса

### Тексты
- `GET /api/text/` - список текстов
- `POST /api/text/create/` - создание текста
- `GET /api/text/get/` - получение текста
- `PUT /api/text/update/` - обновление текста
- `DELETE /api/text/delete/` - удаление текста

### Онтология
- `GET /api/ontology/` - список узлов
- `POST /api/ontology/create_class/` - создание класса
- `GET /api/ontology/get_class/` - получение класса
- `POST /api/ontology/create_object/` - создание объекта
- `GET /api/ontology/get_object/` - получение объекта

## Веб-интерфейс

- `/` - главная страница (Dashboard)
- `/corpus/` - управление корпусами
- `/text/` - управление текстами
- `/ontology/` - управление онтологией

## Требования

- Python 3.8+
- Django 4.2+
- Neo4j 5.0+
- python-dotenv

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Структура проекта

```
text-corpus/
├── backend.py          # Запуск бэкенда
├── frontend.py         # Запуск фронтенда
├── stop.py            # Остановка серверов
├── config.env         # Конфигурация
├── manage.py          # Django управление
├── core/              # Настройки Django
├── db/                # Модели и API
│   ├── models.py      # Модели данных
│   ├── views.py       # API endpoints
│   ├── api/           # Репозитории
│   └── templates/     # HTML шаблоны
└── requirements.txt   # Зависимости
```