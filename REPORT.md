# Отчёт о разработке репозитория для работы с графовой базой данных Neo4j

## Введение

В рамках данного проекта была разработана библиотека `GraphRepository` для работы с графовой базой данных Neo4j. Целью проекта являлось создание удобного, безопасного и надежного интерфейса для выполнения основных операций с узлами и связями в графовой базе данных.

Графовые базы данных представляют собой специализированный тип NoSQL баз данных, которые оптимизированы для хранения и обработки связанных данных. Neo4j является одной из наиболее популярных графовых баз данных, использующей язык запросов Cypher для манипуляции данными.

Разработанная библиотека предоставляет типизированный интерфейс для работы с Neo4j, включающий методы для создания, чтения, обновления и удаления узлов и связей, а также выполнения произвольных Cypher-запросов.

## 1. Реализация алгоритма

### 1.1 Архитектура системы

Для реализации системы работы с графовой базой данных был разработан основной класс GraphRepository, приведенный на листинге 1.

```python
class GraphRepository:
    def __init__(self, uri: str, user: str, password: str, database: str = None):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

Листинг 1 – Класс GraphRepository

При инициализации создается драйвер для подключения к Neo4j и настраивается контекстный менеджер для автоматического управления ресурсами.

### 1.2 Реализация методов получения данных

#### 1.2.1 Метод получения всех узлов

Для получения всех узлов графа был реализован метод get_all_nodes(), приведенный на листинге 2.

```python
def get_all_nodes(self) -> List[TNode]:
    query = """
    MATCH (n)
    RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
    """
    results = self._execute_query(query)
    return [self.collect_node(result) for result in results]
```

Листинг 2 – Метод get_all_nodes()

Выполняет Cypher-запрос для получения всех узлов и преобразует результаты в типизированные объекты TNode.

#### 1.2.2 Метод получения узлов с их связями

Для получения всех узлов вместе с их исходящими связями был реализован метод get_all_nodes_and_arcs(), приведенный на листинге 3.

```python
def get_all_nodes_and_arcs(self) -> List[TNode]:
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    WITH n, collect({
        element_id: elementId(r),
        uri: type(r),
        node_uri_from: n.uri,
        node_uri_to: m.uri
    }) as arcs
    RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title, arcs
    """
    results = self._execute_query(query)
    nodes = []
    for result in results:
        node = self.collect_node(result)
        node.arcs = [self.collect_arc(arc) for arc in result.get('arcs', []) if arc.get('element_id')]
        nodes.append(node)
    return nodes
```

Листинг 3 – Метод get_all_nodes_and_arcs()

Использует OPTIONAL MATCH для включения узлов без связей и агрегирует связи с помощью функции collect().

#### 1.2.3 Метод получения узлов по меткам

Для получения узлов по определенным меткам был реализован метод get_nodes_by_labels(), приведенный на листинге 4.

```python
def get_nodes_by_labels(self, labels: List[str]) -> List[TNode]:
    if not labels:
        return []
    
    labels_clause = self._build_labels_clause(labels)
    query = f"""
    MATCH (n{labels_clause})
    RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
    """
    results = self._execute_query(query)
    return [self.collect_node(result) for result in results]
```

Листинг 4 – Метод get_nodes_by_labels()

Безопасно строит строку меток и выполняет запрос для получения узлов с указанными метками.

### 1.3 Реализация методов создания данных

#### 1.3.1 Метод создания узла

Для создания нового узла в графе был реализован метод create_node(), приведенный на листинге 5.

```python
def create_node(self, params: Dict[str, Any]) -> TNode:
    if 'uri' not in params:
        params['uri'] = f"node_{self.generate_random_string()}"
    
    labels = params.pop('labels', [])
    labels_clause = self._build_labels_clause(labels)
    
    query = f"""
    CREATE (n{labels_clause} $props)
    RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
    """
    
    results = self._execute_query(query, {'props': params})
    if results:
        return self.collect_node(results[0])
    raise Exception("Не удалось создать узел")
```

Листинг 5 – Метод create_node()

Генерирует URI, строит безопасную строку меток и создает узел с использованием параметризованного запроса.

#### 1.3.2 Метод создания связи

Для создания связи между узлами был реализован метод create_arc(), приведенный на листинге 6.

```python
def create_arc(self, node1_uri: str, node2_uri: str, arc_type: str = "RELATES_TO", properties: Dict[str, Any] = None) -> TArc:
    safe_arc_type = arc_type.replace('`', '``')
    
    query = f"""
    MATCH (n1 {{uri: $node1_uri}}), (n2 {{uri: $node2_uri}})
    CREATE (n1)-[r:`{safe_arc_type}` $props]->(n2)
    RETURN elementId(r) as element_id, type(r) as uri, n1.uri as node_uri_from, n2.uri as node_uri_to
    """
    
    results = self._execute_query(query, {
        'node1_uri': node1_uri,
        'node2_uri': node2_uri,
        'props': properties or {}
    })
    
    if results:
        return self.collect_arc(results[0])
    raise Exception("Не удалось создать связь")
```

Листинг 6 – Метод create_arc()

Безопасно экранирует тип связи, находит узлы по URI и создает связь между ними.

### 1.4 Реализация методов обновления и удаления

#### 1.4.1 Метод обновления узла

Для обновления свойств существующего узла был реализован метод update_node(), приведенный на листинге 7.

```python
def update_node(self, uri: str, params: Dict[str, Any]) -> Optional[TNode]:
    if not params:
        return None
    
    query = """
    MATCH (n {uri: $uri})
    SET n += $props
    RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
    """
    
    results = self._execute_query(query, {'uri': uri, 'props': params})
    if results:
        return self.collect_node(results[0])
    return None
```

Листинг 7 – Метод update_node()

Находит узел по URI и обновляет его свойства с помощью оператора SET.

#### 1.4.2 Метод удаления узла

Для удаления узла из графа был реализован метод delete_node_by_uri(), приведенный на листинге 8.

```python
def delete_node_by_uri(self, uri: str) -> bool:
    query = """
    MATCH (n {uri: $uri})
    DETACH DELETE n
    """
    
    with self.driver.session(database=self.database) as session:
        result = session.run(query, {'uri': uri})
        summary = result.consume()
        return summary.counters.nodes_deleted > 0
```

Листинг 8 – Метод delete_node_by_uri()

Удаляет узел вместе со всеми его связями и проверяет успешность операции через статистику выполнения.

### 1.5 Обеспечение безопасности

#### 1.5.1 Метод безопасного построения меток

Для защиты от Cypher Injection атак был реализован метод _build_labels_clause(), приведенный на листинге 9.

```python
def _build_labels_clause(self, labels: List[str]) -> str:
    if not labels:
        return ''
    escaped_labels = [f"`{label.replace('`', '``')}`" for label in labels]
    return ':' + ':'.join(escaped_labels)
```

Листинг 9 – Метод _build_labels_clause()

Безопасно экранирует метки узлов с помощью обратных кавычек для предотвращения инъекций.

#### 1.5.2 Метод выполнения запросов

Для безопасного выполнения запросов к базе данных был реализован метод _execute_query(), приведенный на листинге 10.

```python
def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    with self.driver.session(database=self.database) as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]
```

Листинг 10 – Метод _execute_query()

Выполняет параметризованный запрос к базе данных и возвращает результаты в виде списка словарей.

### 1.6 Типизация данных

#### 1.6.1 Структура узла

Для типизации узлов графа была создана структура TNode, приведенная на листинге 11.

```python
@dataclass
class TNode:
    id: str  # element ID (стабильный)
    uri: str
    description: str
    title: str
    arcs: Optional[List['TArc']] = None
```

Листинг 11 – Структура TNode

Типизированное представление узла графа с использованием стабильного element ID и основных свойств.

#### 1.6.2 Структура связи

Для типизации связей графа была создана структура TArc, приведенная на листинге 12.

```python
@dataclass
class TArc:
    id: str  # element ID (стабильный)
    uri: str  # arc.type
    node_uri_from: str
    node_uri_to: str
```

Листинг 12 – Структура TArc

Типизированное представление связи графа с использованием стабильного element ID и URI узлов-участников.

### 1.7 Вспомогательные методы

#### 1.7.1 Метод генерации случайных строк

Для генерации уникальных URI узлов был реализован метод generate_random_string(), приведенный на листинге 13.

```python
def generate_random_string(self, length: int = 10) -> str:
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))
```

Листинг 13 – Метод generate_random_string()

Генерирует случайную строку заданной длины из букв и цифр для создания уникальных URI узлов.

#### 1.7.2 Метод выполнения произвольных запросов

Для выполнения пользовательских Cypher-запросов был реализован метод run_custom_query(), приведенный на листинге 14.

```python
def run_custom_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    return self._execute_query(query, parameters)
```

Листинг 14 – Метод run_custom_query()

Делегирует выполнение произвольного Cypher-запроса к базовому методу _execute_query().


## Заключение

В рамках данного проекта была успешно разработана библиотека `GraphRepository` для работы с графовой базой данных Neo4j. Основные достижения проекта:

1. **Создан безопасный и надежный интерфейс** для работы с Neo4j, защищенный от атак типа Cypher Injection
2. **Реализованы все основные операции** CRUD для узлов и связей графа
3. **Обеспечена типизация данных** с помощью современных возможностей Python
4. **Использованы стабильные идентификаторы** elementId() вместо внутренних ID
5. **Реализована защита от инъекций** через параметризованные запросы

Библиотека готова к использованию в продакшене и может служить основой для более сложных систем, работающих с графовыми данными. Архитектура системы позволяет легко расширять функциональность и адаптировать под различные бизнес-требования.

## Список литературы

1. Neo4j Documentation. [Электронный ресурс]. URL: https://neo4j.com/docs/
2. Cypher Query Language Reference. [Электронный ресурс]. URL: https://neo4j.com/docs/cypher-manual/
3. Python Neo4j Driver Documentation. [Электронный ресурс]. URL: https://neo4j.com/docs/python-manual/
4. Graph Databases: New Opportunities for Connected Data / Ian Robinson, Jim Webber, Emil Eifrem. - O'Reilly Media, 2015
5. Python Dataclasses Documentation. [Электронный ресурс]. URL: https://docs.python.org/3/library/dataclasses.html
6. SQL Injection Prevention Cheat Sheet. [Электронный ресурс]. URL: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
