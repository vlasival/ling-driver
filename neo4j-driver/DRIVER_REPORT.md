**МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ**  
**РОССИЙСКОЙ ФЕДЕРАЦИИ**

**ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ**  
**ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ**  
**«НОВОСИБИРСКИЙ НАЦИОНАЛЬНЫЙ ИССЛЕДОВАТЕЛЬСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ»**

**ФАКУЛЬТЕТ ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ**

Кафедра Систем информатики

Направление подготовки 09.06.01 – Информатика и вычислительная техника

**Тема задания**:   
**Разработка драйвера для графовой базы данных Neo4j**

Новосибирск 2025

**[Введение	3](#введение)**

[1 Архитектура системы	4](#1-архитектура-системы)

[2 Реализация методов получения данных	4](#2-реализация-методов-получения-данных)

[1.2.1 Метод получения всех узлов	4](#1.2.1-метод-получения-всех-узлов)

[2.2 Метод получения узлов с их связями	5](#2.2-метод-получения-узлов-с-их-связями)

[2.3 Метод получения узлов по меткам	5](#2.3-метод-получения-узлов-по-меткам)

[3 Реализация методов создания данных	7](#3-реализация-методов-создания-данных)

[3.1 Метод создания узла	7](#3.1-метод-создания-узла)

[3.2 Метод создания связи	7](#3.2-метод-создания-связи)

[4 Реализация методов обновления и удаления	9](#4-реализация-методов-обновления-и-удаления)

[4.1 Метод обновления узла	9](#4.1-метод-обновления-узла)

[4.2 Метод удаления узла	9](#4.2-метод-удаления-узла)

[5 Типизация данных	11](#5-типизация-данных)

[5.1 Структура узла	11](#5.1-структура-узла)

[5.2 Структура связи	11](#5.2-структура-связи)

[6 Вспомогательные методы	12](#6-вспомогательные-методы)

[6.1 Метод генерации случайных строк	12](#6.1-метод-генерации-случайных-строк)

[6.2 Метод выполнения произвольных запросов	12](#6.2-метод-выполнения-произвольных-запросов)

[6.3 Метод трансформации узла	12](#6.3-метод-трансформации-узла)

[6.4 Метод трансформации связи	13](#6.4-метод-трансформации-связи)

[**Заключение	14**](#заключение)

[**Список литературы	15**](#список-литературы)

## 

## **Введение** {#введение}

В рамках данного проекта была разработана библиотека GraphRepository для работы с графовой базой данных Neo4j. Целью проекта являлось создание удобного, безопасного и надежного интерфейса для выполнения основных операций с узлами и связями в графовой базе данных.

Разработанная библиотека предоставляет типизированный интерфейс для работы с Neo4j, включающий методы для создания, чтения, обновления и удаления узлов и связей, а также выполнения произвольных Cypher-запросов.

## 

### **1 Архитектура системы** {#1-архитектура-системы}

Для реализации системы работы с графовой базой данных был разработан основной класс GraphRepository, приведенный на листинге 1\.

class GraphRepository:

    def \_\_init\_\_(self, uri: str, user: str, password: str, database: str \= None):

        self.uri \= uri

        self.user \= user

        self.password \= password

        self.database \= database

        self.driver \= GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    

    def \_\_enter\_\_(self):

        return self

    

    def \_\_exit\_\_(self, exc\_type, exc\_val, exc\_tb):

        self.close()

Листинг 1 – Класс GraphRepository

При инициализации создается драйвер для подключения к Neo4j и настраивается контекстный менеджер для автоматического управления ресурсами.

### **2 Реализация методов получения данных** {#2-реализация-методов-получения-данных}

#### **1.2.1 Метод получения всех узлов** {#1.2.1-метод-получения-всех-узлов}

Для получения всех узлов графа был реализован метод get\_all\_nodes(), приведенный на листинге 2\.

def get\_all\_nodes(self) \-\> List\[TNode\]:

    query \= """

    MATCH (n)

    RETURN elementId(n) as element\_id, n.uri as uri, n.description as description, n.title as title

    """

    results \= self.\_execute\_query(query)

    return \[self.collect\_node(result) for result in results\]

Листинг 2 – Метод get\_all\_nodes()

Выполняет Cypher-запрос для получения всех узлов и преобразует результаты в типизированные объекты TNode.

#### **2.2 Метод получения узлов с их связями** {#2.2-метод-получения-узлов-с-их-связями}

Для получения всех узлов вместе с их исходящими связями был реализован метод get\_all\_nodes\_and\_arcs(), приведенный на листинге 3\.

def get\_all\_nodes\_and\_arcs(self) \-\> List\[TNode\]:

    query \= """

    MATCH (n)

    OPTIONAL MATCH (n)-\[r\]-\>(m)

    WITH n, collect({

        element\_id: elementId(r),

        uri: type(r),

        node\_uri\_from: n.uri,

        node\_uri\_to: m.uri

    }) as arcs

    RETURN elementId(n) as element\_id, n.uri as uri, n.description as description, n.title as title, arcs

    """

    results \= self.\_execute\_query(query)

    nodes \= \[\]

    for result in results:

        node \= self.collect\_node(result)

        node.arcs \= \[self.collect\_arc(arc) for arc in result.get('arcs', \[\]) if arc.get('element\_id')\]

        nodes.append(node)

    return nodes

Листинг 3 – Метод get\_all\_nodes\_and\_arcs()

Использует OPTIONAL MATCH для включения узлов без связей и агрегирует связи с помощью функции collect().

#### **2.3 Метод получения узлов по меткам** {#2.3-метод-получения-узлов-по-меткам}

Для получения узлов по определенным меткам был реализован метод get\_nodes\_by\_labels(), приведенный на листинге 4\.

def get\_nodes\_by\_labels(self, labels: List\[str\]) \-\> List\[TNode\]:

    if not labels:

        return \[\]

    

    labels\_clause \= self.\_build\_labels\_clause(labels)

    query \= f"""

    MATCH (n{labels\_clause})

    RETURN elementId(n) as element\_id, n.uri as uri, n.description as description, n.title as title

    """

    results \= self.\_execute\_query(query)

    return \[self.collect\_node(result) for result in results\]

Листинг 4 – Метод get\_nodes\_by\_labels()

Строит строку меток и выполняет запрос для получения узлов с указанными метками.

### 

### **3 Реализация методов создания данных** {#3-реализация-методов-создания-данных}

#### **3.1 Метод создания узла** {#3.1-метод-создания-узла}

Для создания нового узла в графе был реализован метод create\_node(), приведенный на листинге 5\.

def create\_node(self, params: Dict\[str, Any\]) \-\> TNode:

    if 'uri' not in params:

        params\['uri'\] \= f"node\_{self.generate\_random\_string()}"

    

    labels \= params.pop('labels', \[\])

    labels\_clause \= self.\_build\_labels\_clause(labels)

    

    query \= f"""

    CREATE (n{labels\_clause} $props)

    RETURN elementId(n) as element\_id, n.uri as uri, n.description as description, n.title as title

    """

    

    results \= self.\_execute\_query(query, {'props': params})

    if results:

        return self.collect\_node(results\[0\])

    raise Exception("Не удалось создать узел")

Листинг 5 – Метод create\_node()

Генерирует URI, строит строку меток и создает узел с использованием параметризованного запроса.

#### **3.2 Метод создания связи** {#3.2-метод-создания-связи}

Для создания связи между узлами был реализован метод create\_arc(), приведенный на листинге 6\.

def create\_arc(self, node1\_uri: str, node2\_uri: str, arc\_type: str \= "RELATES\_TO", properties: Dict\[str, Any\] \= None) \-\> TArc:

    safe\_arc\_type \= arc\_type.replace('\`', '\`\`')

    

    query \= f"""

    MATCH (n1 {{uri: $node1\_uri}}), (n2 {{uri: $node2\_uri}})

    CREATE (n1)-\[r:\`{safe\_arc\_type}\` $props\]-\>(n2)

    RETURN elementId(r) as element\_id, type(r) as uri, n1.uri as node\_uri\_from, n2.uri as node\_uri\_to

    """

    

    results \= self.\_execute\_query(query, {

        'node1\_uri': node1\_uri,

        'node2\_uri': node2\_uri,

        'props': properties or {}

    })

    

    if results:

        return self.collect\_arc(results\[0\])

    raise Exception("Не удалось создать связь")

Листинг 6 – Метод create\_arc()

Безопасно экранирует тип связи, находит узлы по URI и создает связь между ними.

### 

### **4 Реализация методов обновления и удаления** {#4-реализация-методов-обновления-и-удаления}

#### **4.1 Метод обновления узла** {#4.1-метод-обновления-узла}

Для обновления свойств существующего узла был реализован метод update\_node(), приведенный на листинге 7\.

def update\_node(self, uri: str, params: Dict\[str, Any\]) \-\> Optional\[TNode\]:

    if not params:

        return None

    

    query \= """

    MATCH (n {uri: $uri})

    SET n \+= $props

    RETURN elementId(n) as element\_id, n.uri as uri, n.description as description, n.title as title

    """

    

    results \= self.\_execute\_query(query, {'uri': uri, 'props': params})

    if results:

        return self.collect\_node(results\[0\])

    return None

Листинг 7 – Метод update\_node()

Находит узел по URI и обновляет его свойства с помощью оператора SET.

#### **4.2 Метод удаления узла** {#4.2-метод-удаления-узла}

Для удаления узла из графа был реализован метод delete\_node\_by\_uri(), приведенный на листинге 8\.

def delete\_node\_by\_uri(self, uri: str) \-\> bool:

    query \= """

    MATCH (n {uri: $uri})

    DETACH DELETE n

    """

    

    with self.driver.session(database=self.database) as session:

        result \= session.run(query, {'uri': uri})

        summary \= result.consume()

        return summary.counters.nodes\_deleted \> 0

Листинг 8 – Метод delete\_node\_by\_uri()

Удаляет узел вместе со всеми его связями и проверяет успешность операции через статистику выполнения.

### 

### **5 Типизация данных** {#5-типизация-данных}

#### **5.1 Структура узла** {#5.1-структура-узла}

Для типизации узлов графа была создана структура TNode, приведенная на листинге 11\.

@dataclass

class TNode:

    id: str  *\# element ID (стабильный)*

    uri: str

    description: str

    title: str

    arcs: Optional\[List\['TArc'\]\] \= None

Листинг 11 – Структура TNode

Типизированное представление узла графа с использованием стабильного element ID и основных свойств.

#### **5.2 Структура связи** {#5.2-структура-связи}

Для типизации связей графа была создана структура TArc, приведенная на листинге 12\.

@dataclass

class TArc:

    id: str  *\# element ID (стабильный)*

    uri: str  *\# arc.type*

    node\_uri\_from: str

    node\_uri\_to: str

Листинг 12 – Структура TArc

Типизированное представление связи графа с использованием стабильного element ID и URI узлов-участников.

### 

### **6 Вспомогательные методы** {#6-вспомогательные-методы}

#### **6.1 Метод генерации случайных строк** {#6.1-метод-генерации-случайных-строк}

Для генерации уникальных URI узлов был реализован метод generate\_random\_string(), приведенный на листинге 13\.

def generate\_random\_string(self, length: int \= 10) \-\> str:

    letters \= string.ascii\_lowercase \+ string.digits

    return ''.join(random.choice(letters) for \_ in range(length))

Листинг 13 – Метод generate\_random\_string()

Генерирует случайную строку заданной длины из букв и цифр для создания уникальных URI узлов.

#### **6.2 Метод выполнения произвольных запросов** {#6.2-метод-выполнения-произвольных-запросов}

Для выполнения пользовательских Cypher-запросов был реализован метод run\_custom\_query(), приведенный на листинге 14\.

def run\_custom\_query(self, query: str, parameters: Dict\[str, Any\] \= None) \-\> List\[Dict\[str, Any\]\]:

    return self.\_execute\_query(query, parameters)

Листинг 14 – Метод run\_custom\_query()

Делегирует выполнение произвольного Cypher-запроса к базовому методу \_execute\_query().

#### **6.3 Метод трансформации узла** {#6.3-метод-трансформации-узла}

Для преобразования необработанных данных узла из базы данных в типизированный объект `TNode` был реализован метод `collect_node()`, приведенный на листинге 15\.

def collect\_node(self, node\_data: Dict\[str, Any\]) \-\> TNode:

      return TNode(

        id=node\_data.get('element\_id', ''),

        uri=node\_data.get('uri', ''),

        description=node\_data.get('description', ''),

        title=node\_data.get('title', ''),

        arcs=node\_data.get('arcs', \[\])

    )

Листинг 15 – Метод `collect_node()`

Преобразует словарь с данными узла в типизированную структуру `TNode`, обеспечивая унифицированное представление данных в приложении.

#### **6.4 Метод трансформации связи** {#6.4-метод-трансформации-связи}

Для преобразования необработанных данных связи из базы данных в типизированный объект `TArc` был реализован метод `collect_arc()`, приведенный на листинге 16\.

def collect\_arc(self, arc\_data: Dict\[str, Any\]) \-\> TArc:

    return TArc(

        id=arc\_data.get('element\_id', ''),

        uri=arc\_data.get('uri', ''),

        node\_uri\_from=arc\_data.get('node\_uri\_from', ''),

        node\_uri\_to=arc\_data.get('node\_uri\_to', '')

    )

Листинг 16 – Метод `collect_arc()`

Преобразует словарь с данными связи в типизированную структуру `TArc`, что позволяет легко работать со связями в коде.

## 

## **Заключение** {#заключение}

В рамках данного проекта была успешно разработана библиотека GraphRepository для работы с графовой базой данных Neo4j. Основные достижения проекта:

1. **Создан безопасный и надежный интерфейс** для работы с Neo4j  
2. **Реализованы все основные операции** CRUD для узлов и связей графа  
3. **Обеспечена типизация данных** с помощью современных возможностей Python

Библиотека готова к использованию в продакшене и может служить основой для более сложных систем, работающих с графовыми данными. Архитектура системы позволяет легко расширять функциональность и адаптировать под различные бизнес-требования.

## 

## **Список литературы** {#список-литературы}

1. Neo4j Documentation. \[Электронный ресурс\]. URL: [https://neo4j.com/docs/](https://neo4j.com/docs/)  
2. Cypher Query Language Reference. \[Электронный ресурс\]. URL: [https://neo4j.com/docs/cypher-manual/](https://neo4j.com/docs/cypher-manual/)  
3. Python Neo4j Driver Documentation. \[Электронный ресурс\]. URL: [https://neo4j.com/docs/python-manual/](https://neo4j.com/docs/python-manual/)  
4. Python Dataclasses Documentation. \[Электронный ресурс\]. URL: [https://docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)  
   

