# Graph Database Repository

Репозиторий для работы с графовой базой данных Neo4j. Предоставляет удобный интерфейс для работы с узлами и связями графа.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env` в корне проекта:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Работа с базами данных

По умолчанию репозиторий работает с системной базой данных Neo4j. Для работы с конкретной базой данных передайте параметр `database`:

```python
# Работа с конкретной базой данных
repo = GraphRepository(
    uri='bolt://localhost:7687',
    user='neo4j',
    password='your_password',
    database='driver-test'  # название базы данных
)
```

## Быстрый старт

```python
from graph_repository import GraphRepository

# Инициализация репозитория
repo = GraphRepository(
    uri='bolt://localhost:7687',
    user='neo4j',
    password='your_password',
    database='driver-test'  # опционально
)

with repo:
    # Создание узла
    node_params = {
        'title': 'Test Node',
        'description': 'Test Description',
        'labels': ['Test', 'Example']
    }
    node = repo.create_node(node_params)
    
    # Получение всех узлов
    nodes = repo.get_all_nodes()
    print(f"Создано узлов: {len(nodes)}")
```

## API Документация

### Основные методы

#### Получение данных

- **`get_all_nodes()`** - получить все узлы графа
  ```python
  nodes = repo.get_all_nodes()
  ```

- **`get_all_nodes_and_arcs()`** - получить все узлы с их связями
  ```python
  nodes_with_arcs = repo.get_all_nodes_and_arcs()
  ```

- **`get_nodes_by_labels(labels: List[str])`** - получить выборку узлов по их меткам
  ```python
  user_nodes = repo.get_nodes_by_labels(['User', 'Person'])
  ```

- **`get_node_by_uri(uri: str)`** - получить узел по URI
  ```python
  node = repo.get_node_by_uri('node_abc123')
  ```

#### Создание данных

- **`create_node(params: Dict[str, Any])`** - создать новый узел
  ```python
  node_params = {
      'title': 'Новый узел',
      'description': 'Описание узла',
      'labels': ['User'],  # опционально
      'custom_property': 'значение'  # любые дополнительные свойства
  }
  node = repo.create_node(node_params)
  ```

- **`create_arc(node1_uri: str, node2_uri: str, arc_type: str, properties: Dict)`** - создать связь между узлами
  ```python
  arc = repo.create_arc(
      'node1_uri', 
      'node2_uri', 
      'RELATES_TO',
      {'weight': 1.0, 'created_at': '2024-01-01'}
  )
  ```

#### Обновление данных

- **`update_node(uri: str, params: Dict[str, Any])`** - обновить узел
  ```python
  updated_node = repo.update_node('node_uri', {
      'description': 'Новое описание',
      'status': 'updated'
  })
  ```

#### Удаление данных

- **`delete_node_by_uri(uri: str)`** - удалить узел по URI
  ```python
  success = repo.delete_node_by_uri('node_uri')
  ```

- **`delete_arc_by_id(arc_id: int)`** - удалить связь по ID
  ```python
  success = repo.delete_arc_by_id(123)
  ```

#### Вспомогательные методы

- **`generate_random_string(length: int = 10)`** - генерация строки для URI узла
  ```python
  random_uri = repo.generate_random_string(8)
  ```

- **`run_custom_query(query: str, parameters: Dict)`** - выполнение произвольного Cypher запроса
  ```python
  results = repo.run_custom_query(
      "MATCH (n:User) WHERE n.age > $min_age RETURN n",
      {'min_age': 18}
  )
  ```

### Типы данных

#### TNode
```python
@dataclass
class TNode:
    id: str  # element ID (стабильный)
    uri: str
    description: str
    title: str
    arcs: Optional[List[TArc]] = None
```

#### TArc
```python
@dataclass
class TArc:
    id: str  # element ID (стабильный)
    uri: str  # тип связи
    node_uri_from: str
    node_uri_to: str
```

## Примеры использования

### Создание графа пользователей и проектов

```python
repo = GraphRepository(
    uri='bolt://localhost:7687',
    user='neo4j',
    password='your_password',
    database='driver-test'
)

with repo:
    # Создаем пользователя
    user = repo.create_node({
        'title': 'Иван Иванов',
        'description': 'Разработчик',
        'labels': ['User', 'Developer'],
        'email': 'ivan@example.com'
    })
    
    # Создаем проект
    project = repo.create_node({
        'title': 'Мой проект',
        'description': 'Веб-приложение',
        'labels': ['Project'],
        'status': 'active'
    })
    
    # Создаем связь
    repo.create_arc(
        user.uri, 
        project.uri, 
        'OWNS',
        {'role': 'owner', 'created_at': '2024-01-01'}
    )
```

### Поиск и фильтрация

```python
repo = GraphRepository(
    uri='bolt://localhost:7687',
    user='neo4j',
    password='your_password',
    database='driver-test'
)

with repo:
    # Поиск всех пользователей
    users = repo.get_nodes_by_labels(['User'])

    # Поиск узлов с определенными свойствами
    results = repo.run_custom_query(
        "MATCH (n:User) WHERE n.email CONTAINS '@example.com' RETURN n"
    )

    # Поиск путей между узлами
    paths = repo.run_custom_query("""
        MATCH path = (start:User)-[*1..3]-(end:Project)
        WHERE start.uri = $user_uri
        RETURN path, length(path) as path_length
        ORDER BY path_length
    """, {'user_uri': user.uri})
```

## Запуск

```bash
python example.py
```

Этот пример демонстрирует все основные возможности GraphRepository:
- Создание узлов и связей
- Получение данных различными способами
- Продвинутые Cypher запросы
- Обновление данных
- Утилиты и вспомогательные функции

## Особенности

- **Безопасность**: Защита от Cypher Injection через параметризованные запросы
- **Стабильные ID**: Использование elementId() вместо внутренних ID
- **Автоматическое управление соединениями**: Контекстный менеджер
- **Типизированные объекты**: `TNode` и `TArc` с полной типизацией
- **Гибкость**: Поддержка произвольных свойств узлов и связей
- **Надежность**: Правильная обработка статистики выполнения запросов
- **Удобство**: Автоматическая генерация URI
