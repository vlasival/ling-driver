# GraphRepository

Репозиторий для работы с графовой базой данных Neo4j.

## Описание

Библиотека `GraphRepository` предоставляет удобный интерфейс для работы с графовыми данными в Neo4j. Поддерживает создание, чтение, обновление и удаление узлов и связей.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env` с параметрами подключения:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
```

## Использование

### Базовое использование

```python
from graph_repository import GraphRepository

# Подключение к базе данных
repo = GraphRepository(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"
)

# Создание узла
node = repo.create_node({
    'title': 'Тестовый узел',
    'description': 'Описание узла',
    'labels': ['TestNode']
})

# Создание связи
arc = repo.create_arc(
    node1_uri=node.uri,
    node2_uri=other_node.uri,
    arc_type="RELATES_TO"
)

# Получение всех узлов
all_nodes = repo.get_all_nodes()

# Закрытие соединения
repo.close()
```

### Запуск примера

```bash
python3 example.py
```

## Структура данных

### TNode
```python
@dataclass
class TNode:
    id: str                    # element ID
    uri: str                   # URI узла
    description: str           # Описание
    title: str                 # Название
    arcs: Optional[List[TArc]] # Список связей
```

### TArc
```python
@dataclass
class TArc:
    id: str           # element ID
    uri: str          # Тип связи
    node_uri_from: str # URI исходного узла
    node_uri_to: str   # URI целевого узла
```

## Методы

### Основные методы
- `get_all_nodes()` — получить все узлы
- `get_all_nodes_and_arcs()` — получить все узлы с их связями
- `get_nodes_by_labels(labels)` — получить узлы по меткам
- `get_node_by_uri(uri)` — получить узел по URI

### Методы создания
- `create_node(params)` — создать узел
- `create_arc(node1_uri, node2_uri, arc_type, properties)` — создать связь

### Методы обновления
- `update_node(uri, params)` — обновить узел

### Методы удаления
- `delete_node_by_uri(uri)` — удалить узел
- `delete_arc_by_id(arc_id)` — удалить связь

### Вспомогательные методы
- `run_custom_query(query, parameters)` — выполнить произвольный запрос
- `generate_random_string(length)` — сгенерировать случайную строку

## Безопасность

- Параметризованные запросы для защиты от инъекций
- Безопасное экранирование меток и типов связей
- Проверка существования узлов и связей

## Требования

- Python 3.7+
- Neo4j 4.0+
- neo4j==5.15.0
- python-dotenv==1.0.0
