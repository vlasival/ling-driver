# Text Corpus Django Project

Django проект для хранения и управления корпусом текстов с интеграцией Neo4j онтологии.

## Описание

Проект реализует REST API для работы с корпусами текстов и отдельными текстами, а также интегрирует функциональность Neo4j для работы с онтологиями.

## Структура проекта

```
text-corpus/
├── core/                    # Основные настройки Django
│   ├── settings.py         # Настройки проекта
│   ├── urls.py            # Главные URL маршруты
│   └── wsgi.py            # WSGI конфигурация
├── db/                     # Основное приложение
│   ├── models.py          # Модели данных (Corpus, Text)
│   ├── views.py           # API views
│   ├── urls.py            # URL маршруты API
│   └── api/               # Репозитории
│       ├── CorpusRepository.py
│       ├── TextRepository.py
│       ├── graph_repository.py
│       └── ontology_repository.py
├── manage.py              # Django management script
└── requirements.txt       # Зависимости
```

## Модели данных

### Corpus (Корпус)
- `name` - название корпуса
- `description` - описание
- `genre` - жанр
- `created_at` - дата создания
- `updated_at` - дата обновления

### Text (Текст)
- `name` - название текста
- `description` - описание
- `text` - содержимое текста
- `corpus` - связь с корпусом (ForeignKey)
- `has_translation` - связь с переводом (Self-reference)
- `created_at` - дата создания
- `updated_at` - дата обновления

## API Endpoints

### Корпуса (Corpus)
- `GET /api/corpus/` - получить все корпуса
- `POST /api/corpus/create/` - создать корпус
- `GET /api/corpus/get/?id={id}` - получить корпус по ID
- `GET /api/corpus/get_with_texts/?id={id}` - получить корпус со всеми текстами
- `PUT /api/corpus/update/?id={id}` - обновить корпус
- `DELETE /api/corpus/delete/?id={id}` - удалить корпус

### Тексты (Text)
- `GET /api/text/` - получить все тексты
- `POST /api/text/create/` - создать текст
- `GET /api/text/get/?id={id}` - получить текст по ID
- `GET /api/text/get_by_corpus/?corpus_id={id}` - получить тексты корпуса
- `PUT /api/text/update/?id={id}` - обновить текст
- `DELETE /api/text/delete/?id={id}` - удалить текст

### Онтология (Ontology)
- `GET /api/ontology/` - получить всю онтологию
- `GET /api/ontology/parent_classes/` - получить корневые классы
- `GET /api/ontology/class/?uri={uri}` - получить класс по URI
- `POST /api/ontology/class/create/` - создать класс
- `GET /api/ontology/signature/?uri={uri}` - собрать signature класса

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Запуск сервера
```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://localhost:8000

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=ontology
```

## Примеры использования

### Создание корпуса
```bash
curl -X POST "http://localhost:8000/api/corpus/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Русская литература",
    "description": "Корпус русской литературы",
    "genre": "Художественная литература"
  }'
```

### Создание текста
```bash
curl -X POST "http://localhost:8000/api/text/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Евгений Онегин",
    "description": "Роман в стихах",
    "text": "Мой дядя самых честных правил...",
    "corpus_id": 1
  }'
```

### Получение корпуса со всеми текстами
```bash
curl -X GET "http://localhost:8000/api/corpus/get_with_texts/?id=1"
```

## Интеграция с Neo4j

Проект интегрирует репозитории из предыдущих лабораторных работ:
- `GraphRepository` - базовый функционал работы с Neo4j
- `OntologyRepository` - работа с онтологиями

## Технологии

- **Django 4.2.7** - веб-фреймворк
- **Django REST Framework 3.14.0** - REST API
- **Neo4j 5.15.0** - графовая база данных
- **SQLite** - реляционная база данных (по умолчанию)
- **PostgreSQL** - поддерживается через psycopg2

## Особенности реализации

1. **Репозиторный паттерн** - вся бизнес-логика вынесена в репозитории
2. **Типизация** - использование type hints для лучшей читаемости кода
3. **Обработка ошибок** - корректная обработка исключений в API
4. **Валидация данных** - проверка входных данных
5. **CORS поддержка** - для работы с фронтендом
6. **Интеграция Neo4j** - полная интеграция с графовой базой данных

## Тестирование

API протестировано с помощью curl команд. Все основные операции CRUD работают корректно.

## Разработчик

Senior Python Neo4j Developer с 15-летним опытом.
