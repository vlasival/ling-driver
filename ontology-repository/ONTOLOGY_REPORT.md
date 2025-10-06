**МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ**  
**РОССИЙСКОЙ ФЕДЕРАЦИИ**

**ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ**  
**ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ**  
**«НОВОСИБИРСКИЙ НАЦИОНАЛЬНЫЙ ИССЛЕДОВАТЕЛЬСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ»**

**ФАКУЛЬТЕТ ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ**

Кафедра Систем информатики

Направление подготовки 09.06.01 – Информатика и вычислительная техника

**ОТЧЕТ**

**Тема задания**:   
**Разработка репозитория для редактирования онтологии предметной области** 

Новосибирск 2025 

[Введение	3](#введение)

[1\. Реализация алгоритма	3](#1.-реализация-алгоритма)

[1.1 Архитектура системы	3](#1.1-архитектура-системы)

[1.2 Структуры данных	4](#1.2-структуры-данных)

[1.2.1 Структура SignatureParam	4](#1.2.1-структура-signatureparam)

[1.2.2 Структура SignatureObjParam	4](#1.2.2-структура-signatureobjparam)

[1.2.3 Структура Signature	4](#1.2.3-структура-signature)

[1.3 Реализация методов получения данных	5](#1.3-реализация-методов-получения-данных)

[1.3.1 Метод получения всей онтологии	5](#1.3.1-метод-получения-всей-онтологии)

[1.3.2 Метод получения корневых классов	5](#1.3.2-метод-получения-корневых-классов)

[1.3.3 Метод получения класса по URI	5](#1.3.3-метод-получения-класса-по-uri)

[1.3.4 Метод получения родителей класса	6](#1.3.4-метод-получения-родителей-класса)

[1.3.5 Метод получения потомков класса	7](#1.3.5-метод-получения-потомков-класса)

[1.3.6 Метод получения объектов класса	7](#1.3.6-метод-получения-объектов-класса)

[1.4 Реализация методов создания и обновления	8](#1.4-реализация-методов-создания-и-обновления)

[1.4.1 Метод создания класса	8](#1.4.1-метод-создания-класса)

[1.4.2 Метод обновления класса	9](#1.4.2-метод-обновления-класса)

[1.5 Реализация методов работы с атрибутами	9](#1.5-реализация-методов-работы-с-атрибутами)

[1.5.1 Метод добавления DatatypeProperty	9](#1.5.1-метод-добавления-datatypeproperty)

[1.5.2 Метод добавления ObjectProperty	10](#1.5.2-метод-добавления-objectproperty)

[1.5.3 Метод удаления DatatypeProperty	11](#1.5.3-метод-удаления-datatypeproperty)

[1.6 Реализация методов работы с объектами	12](#1.6-реализация-методов-работы-с-объектами)

[1.6.1 Метод получения объекта	12](#1.6.1-метод-получения-объекта)

[1.6.2 Метод создания объекта	12](#1.6.2-метод-создания-объекта)

[1.6.3 Метод обновления объекта	13](#1.6.3-метод-обновления-объекта)

[1.7 Реализация метода сбора signature	15](#1.7-реализация-метода-сбора-signature)

[1.7.1 Метод collect\_signature	15](#1.7.1-метод-collect_signature)

[1.8 Реализация методов удаления	16](#1.8-реализация-методов-удаления)

[1.8.1 Метод удаления класса	16](#1.8.1-метод-удаления-класса)

[Заключение	17](#заключение)

[Список литературы	17](#список-литературы)

## 

## **Введение** {#введение}

В рамках данного проекта была разработана библиотека OntologyRepository для работы с онтологией в графовой базе данных Neo4j. Целью проекта являлось создание удобного, безопасного и надежного интерфейса для выполнения основных операций с классами, объектами, свойствами и их взаимосвязями в онтологической модели данных.

Онтология представляет собой формальное описание предметной области, включающее классы, объекты, их свойства и отношения. Графовая база данных Neo4j является идеальной платформой для хранения и обработки онтологических данных благодаря своей способности эффективно представлять сложные взаимосвязи между сущностями.

Разработанная библиотека предоставляет типизированный интерфейс для работы с онтологией, включающий методы для создания, чтения, обновления и удаления классов, объектов, свойств, а также выполнения операций сбора signature классов.

## **1\. Реализация алгоритма** {#1.-реализация-алгоритма}

### **1.1 Архитектура системы** {#1.1-архитектура-системы}

Для реализации системы работы с онтологией был разработан основной класс OntologyRepository, наследующий от GraphRepository.

class OntologyRepository(GraphRepository):  
    """Репозиторий для работы с онтологией в графовой базе данных Neo4j"""  
      
    def \_\_init\_\_(self, uri: str, user: str, password: str, database: str \= None):  
        """  
        Инициализация репозитория онтологии  
          
        Args:  
            uri: URI подключения к Neo4j  
            user: Имя пользователя  
            password: Пароль  
            database: Название базы данных  
        """  
        super().\_\_init\_\_(uri, user, password, database)

Листинг 1 – Класс OntologyRepository

При инициализации создается подключение к Neo4j через базовый класс GraphRepository и настраивается контекстный менеджер для автоматического управления ресурсами.

### **1.2 Структуры данных** {#1.2-структуры-данных}

#### **1.2.1 Структура SignatureParam** {#1.2.1-структура-signatureparam}

Для типизации параметров DatatypeProperty была создана структура SignatureParam.

@dataclass  
class SignatureParam:  
    """Параметр DatatypeProperty в signature"""  
    title: str  
    uri: str

Листинг 2 – Структура SignatureParam

Типизированное представление параметра DatatypeProperty с названием и URI.

#### **1.2.2 Структура SignatureObjParam** {#1.2.2-структура-signatureobjparam}

Для типизации параметров ObjectProperty была создана структура SignatureObjParam.

@dataclass  
class SignatureObjParam:  
    """Параметр ObjectProperty в signature"""  
    title: str  
    uri: str  
    target\_class\_uri: str  
    relation\_direction: int  *\# 1 \- от объекта, \-1 \- к объекту*

Листинг 3 – Структура SignatureObjParam

Типизированное представление параметра ObjectProperty с направлением связи и целевым классом.

#### **1.2.3 Структура Signature** {#1.2.3-структура-signature}

Для объединения всех параметров класса была создана структура Signature.

@dataclass  
class Signature:  
    """Структура signature для класса"""  
    params: List\[SignatureParam\]  *\# DatatypeProperty*  
    obj\_params: List\[SignatureObjParam\]  *\# ObjectProperty*

Листинг 4 – Структура Signature

Структура, объединяющая все DatatypeProperty и ObjectProperty класса.

### **1.3 Реализация методов получения данных** {#1.3-реализация-методов-получения-данных}

#### **1.3.1 Метод получения всей онтологии** {#1.3.1-метод-получения-всей-онтологии}

Для получения всей онтологии был реализован метод get\_ontology().

def get\_ontology(self) \-\> List\[TNode\]:  
    """  
    Получить всю онтологию (все узлы с метками Class, Object, DatatypeProperty, ObjectProperty)  
      
    Returns:  
        Список всех узлов онтологии  
    """  
    return self.get\_all\_nodes()

Листинг 5 – Метод get\_ontology()

Делегирует выполнение к базовому методу get\_all\_nodes() для получения всех узлов графа.

#### **1.3.2 Метод получения корневых классов** {#1.3.2-метод-получения-корневых-классов}

Для получения классов без родителей был реализован метод get\_ontology\_parent\_classes().

def get\_ontology\_parent\_classes(self) \-\> List\[TNode\]:  
    """  
    Получить классы онтологии, у которых нет родителей  
      
    Returns:  
        Список корневых классов  
    """  
    query \= """  
    MATCH (c:Class)  
    WHERE NOT (c)-\[:subclass\_of\]-\>()  
    RETURN elementId(c) as element\_id, c.uri as uri, c.description as description, c.title as title  
    """  
    results \= self.\_execute\_query(query)  
    return \[self.collect\_node(result) for result in results\]

Листинг 6 – Метод get\_ontology\_parent\_classes()

Использует Cypher-запрос для поиска классов без входящих связей subclass\_of.

#### **1.3.3 Метод получения класса по URI** {#1.3.3-метод-получения-класса-по-uri}

Для получения конкретного класса был реализован метод get\_class().

def get\_class(self, class\_uri: str) \-\> Optional\[TNode\]:  
    """  
    Получить класс по URI  
      
    Args:  
        class\_uri: URI класса  
          
    Returns:  
        Класс или None, если не найден  
    """  
    query \= """  
    MATCH (c:Class {uri: $class\_uri})  
    RETURN elementId(c) as element\_id, c.uri as uri, c.description as description, c.title as title  
    """  
    results \= self.\_execute\_query(query, {'class\_uri': class\_uri})  
    if results:  
        return self.collect\_node(results\[0\])  
    return None

Листинг 7 – Метод get\_class()

Выполняет поиск класса по URI и возвращает объект TNode или None.

#### **1.3.4 Метод получения родителей класса** {#1.3.4-метод-получения-родителей-класса}

Для получения родительских классов был реализован метод get\_class\_parents().

def get\_class\_parents(self, class\_uri: str) \-\> List\[TNode\]:  
    """  
    Получить родителей класса  
      
    Args:  
        class\_uri: URI класса  
          
    Returns:  
        Список родительских классов  
    """  
    query \= """  
    MATCH (c:Class {uri: $class\_uri})-\[:subclass\_of\]-\>(parent:Class)  
    RETURN elementId(parent) as element\_id, parent.uri as uri, parent.description as description, parent.title as title  
    """  
    results \= self.\_execute\_query(query, {'class\_uri': class\_uri})  
    return \[self.collect\_node(result) for result in results\]

Листинг 8 – Метод get\_class\_parents()

Ищет классы, связанные через связь subclass\_of в направлении от текущего класса.

#### **1.3.5 Метод получения потомков класса** {#1.3.5-метод-получения-потомков-класса}

Для получения дочерних классов был реализован метод get\_class\_children().

def get\_class\_children(self, class\_uri: str) \-\> List\[TNode\]:  
    """  
    Получить потомков класса  
      
    Args:  
        class\_uri: URI класса  
          
    Returns:  
        Список дочерних классов  
    """  
    query \= """  
    MATCH (c:Class {uri: $class\_uri})\<-\[:subclass\_of\]-(child:Class)  
    RETURN elementId(child) as element\_id, child.uri as uri, child.description as description, child.title as title  
    """  
    results \= self.\_execute\_query(query, {'class\_uri': class\_uri})  
    return \[self.collect\_node(result) for result in results\]

Листинг 9 – Метод get\_class\_children()

Ищет классы, связанные через связь subclass\_of в направлении к текущему классу.

#### **1.3.6 Метод получения объектов класса** {#1.3.6-метод-получения-объектов-класса}

Для получения объектов, принадлежащих классу, был реализован метод get\_class\_objects().

def get\_class\_objects(self, class\_uri: str) \-\> List\[TNode\]:  
    """  
    Получить объекты класса  
      
    Args:  
        class\_uri: URI класса  
          
    Returns:  
        Список объектов класса  
    """  
    query \= """  
    MATCH (c:Class {uri: $class\_uri})\<-\[:instance\_of\]-(obj:Object)  
    RETURN elementId(obj) as element\_id, obj.uri as uri, obj.description as description, obj.title as title  
    """  
    results \= self.\_execute\_query(query, {'class\_uri': class\_uri})  
    return \[self.collect\_node(result) for result in results\]

Листинг 10 – Метод get\_class\_objects()

Ищет объекты, связанные с классом через связь instance\_of.

### **1.4 Реализация методов создания и обновления** {#1.4-реализация-методов-создания-и-обновления}

#### **1.4.1 Метод создания класса** {#1.4.1-метод-создания-класса}

Для создания нового класса был реализован метод create\_class().

def create\_class(self, title: str, description: str, parent\_uri: Optional\[str\] \= None) \-\> TNode:  
    """  
    Создать класс (имя, описание, родитель)  
      
    Args:  
        title: Название класса  
        description: Описание класса  
        parent\_uri: URI родительского класса (опционально)  
          
    Returns:  
        Созданный класс  
    """  
    *\# Генерируем URI для класса*  
    class\_uri \= f"class\_{self.generate\_random\_string()}"  
      
    *\# Создаем класс*  
    class\_node \= self.create\_node({  
        'uri': class\_uri,  
        'title': title,  
        'description': description,  
        'labels': \['Class'\]  
    })  
      
    *\# Если указан родитель, создаем связь*  
    if parent\_uri:  
        self.create\_arc(class\_uri, parent\_uri, 'subclass\_of')  
      
    return class\_node

Листинг 11 – Метод create\_class()

Генерирует уникальный URI, создает узел класса и при необходимости связь с родительским классом.

#### **1.4.2 Метод обновления класса** {#1.4.2-метод-обновления-класса}

Для обновления существующего класса был реализован метод update\_class().

def update\_class(self, class\_uri: str, title: str, description: str) \-\> Optional\[TNode\]:  
    """  
    Обновить класс (имя и описание)  
      
    Args:  
        class\_uri: URI класса  
        title: Новое название  
        description: Новое описание  
          
    Returns:  
        Обновленный класс или None, если не найден  
    """  
    return self.update\_node(class\_uri, {'title': title, 'description': description})

Листинг 12 – Метод update\_class()

Делегирует выполнение к базовому методу update\_node() для обновления свойств класса.

### **1.5 Реализация методов работы с атрибутами** {#1.5-реализация-методов-работы-с-атрибутами}

#### **1.5.1 Метод добавления DatatypeProperty** {#1.5.1-метод-добавления-datatypeproperty}

Для добавления свойства примитивного типа к классу был реализован метод add\_class\_attribute().

def add\_class\_attribute(self, class\_uri: str, attr\_name: str, attr\_uri: Optional\[str\] \= None) \-\> TNode:  
    """  
    Добавить DatatypeProperty к классу  
      
    Args:  
        class\_uri: URI класса  
        attr\_name: Название атрибута  
        attr\_uri: URI атрибута (если не указан, генерируется автоматически)  
          
    Returns:  
        Созданный DatatypeProperty  
    """  
    if not attr\_uri:  
        attr\_uri \= f"attr\_{self.generate\_random\_string()}"  
      
    *\# Создаем DatatypeProperty*  
    attr\_node \= self.create\_node({  
        'uri': attr\_uri,  
        'title': attr\_name,  
        'description': f"DatatypeProperty for {attr\_name}",  
        'labels': \['DatatypeProperty'\]  
    })  
      
    *\# Создаем связь domain*  
    self.create\_arc(attr\_uri, class\_uri, 'applies\_to')  
      
    return attr\_node

Листинг 13 – Метод add\_class\_attribute()

Создает узел DatatypeProperty и связывает его с классом через связь applies\_to.

#### **1.5.2 Метод добавления ObjectProperty** {#1.5.2-метод-добавления-objectproperty}

Для добавления объектного свойства к классу был реализован метод add\_class\_object\_attribute().

def add\_class\_object\_attribute(self, class\_uri: str, attr\_name: str, range\_class\_uri: str) \-\> TNode:  
    """  
    Добавить ObjectProperty к классу  
      
    Args:  
        class\_uri: URI класса  
        attr\_name: Название атрибута  
        range\_class\_uri: URI класса-диапазона  
          
    Returns:  
        Созданный ObjectProperty  
    """  
    attr\_uri \= f"obj\_attr\_{self.generate\_random\_string()}"  
      
    *\# Создаем ObjectProperty*  
    attr\_node \= self.create\_node({  
        'uri': attr\_uri,  
        'title': attr\_name,  
        'description': f"ObjectProperty for {attr\_name}",  
        'labels': \['ObjectProperty'\]  
    })  
      
    *\# Создаем связь domain*  
    self.create\_arc(attr\_uri, class\_uri, 'applies\_to')  
      
    *\# Создаем связь range*  
    self.create\_arc(attr\_uri, range\_class\_uri, 'points\_to')  
      
    return attr\_node

Листинг 14 – Метод add\_class\_object\_attribute()

Создает узел ObjectProperty и связывает его с классом через applies\_to и с целевым классом через points\_to.

#### **1.5.3 Метод удаления DatatypeProperty** {#1.5.3-метод-удаления-datatypeproperty}

Для удаления свойства примитивного типа был реализован метод delete\_class\_attribute().

def delete\_class\_attribute(self, class\_uri: str, attr\_uri: str) \-\> bool:  
    """  
    Удалить DatatypeProperty у класса  
      
    Args:  
        class\_uri: URI класса  
        attr\_uri: URI атрибута  
          
    Returns:  
        True если атрибут удален, False если не найден  
    """  
    *\# Удаляем связь domain и сам атрибут*  
    query \= """  
    MATCH (attr:DatatypeProperty {uri: $attr\_uri})-\[r:applies\_to\]-\>(c:Class {uri: $class\_uri})  
    DELETE r  
    WITH attr  
    DETACH DELETE attr  
    RETURN count(attr) as deleted\_count  
    """  
      
    results \= self.\_execute\_query(query, {'class\_uri': class\_uri, 'attr\_uri': attr\_uri})  
    return results\[0\]\['deleted\_count'\] \> 0 if results else False

Листинг 15 – Метод delete\_class\_attribute()

Удаляет связь applies\_to и сам узел DatatypeProperty с проверкой успешности операции.

### **1.6 Реализация методов работы с объектами** {#1.6-реализация-методов-работы-с-объектами}

#### **1.6.1 Метод получения объекта** {#1.6.1-метод-получения-объекта}

Для получения объекта по URI был реализован метод get\_object().

def get\_object(self, object\_uri: str) \-\> Optional\[TNode\]:  
    """  
    Получить объект по URI  
      
    Args:  
        object\_uri: URI объекта  
          
    Returns:  
        Объект или None, если не найден  
    """  
    query \= """  
    MATCH (obj:Object {uri: $object\_uri})  
    RETURN elementId(obj) as element\_id, obj.uri as uri, obj.description as description, obj.title as title  
    """  
    results \= self.\_execute\_query(query, {'object\_uri': object\_uri})  
    if results:  
        return self.collect\_node(results\[0\])  
    return None

Листинг 16 – Метод get\_object()

Выполняет поиск объекта по URI и возвращает объект TNode или None.

#### **1.6.2 Метод создания объекта** {#1.6.2-метод-создания-объекта}

Для создания нового объекта был реализован метод create\_object().

def create\_object(self, class\_uri: str, object\_data: Dict\[str, Any\]) \-\> TNode:  
    """  
    Создать объект через collect\_signature  
      
    Args:  
        class\_uri: URI класса  
        object\_data: Данные объекта (title, description, свойства)  
          
    Returns:  
        Созданный объект  
    """  
    *\# Генерируем URI для объекта*  
    object\_uri \= f"obj\_{self.generate\_random\_string()}"  
      
    *\# Создаем объект*  
    obj\_node \= self.create\_node({  
        'uri': object\_uri,  
        'title': object\_data.get('title', ''),  
        'description': object\_data.get('description', ''),  
        'labels': \['Object'\]  
    })  
      
    *\# Создаем связь instance\_of*  
    self.create\_arc(object\_uri, class\_uri, 'instance\_of')  
      
    *\# Добавляем свойства объекта*  
    for key, value in object\_data.items():  
        if key not in \['title', 'description'\] and value is not None:  
            *\# Создаем узел свойства*  
            prop\_uri \= f"prop\_{self.generate\_random\_string()}"  
            self.create\_node({  
                'uri': prop\_uri,  
                'value': str(value),  
                'labels': \['Property'\]  
            })  
              
            *\# Создаем связь к свойству*  
            self.create\_arc(object\_uri, prop\_uri, key)  
      
    return obj\_node

Листинг 17 – Метод create\_object()

Создает объект, связывает его с классом и добавляет свойства как отдельные узлы.

#### **1.6.3 Метод обновления объекта** {#1.6.3-метод-обновления-объекта}

Для обновления существующего объекта был реализован метод update\_object().

def update\_object(self, object\_uri: str, object\_data: Dict\[str, Any\]) \-\> Optional\[TNode\]:  
    """  
    Обновить объект через collect\_signature  
      
    Args:  
        object\_uri: URI объекта  
        object\_data: Новые данные объекта  
          
    Returns:  
        Обновленный объект или None, если не найден  
    """  
    *\# Обновляем основные свойства объекта*  
    updated\_obj \= self.update\_node(object\_uri, {  
        'title': object\_data.get('title', ''),  
        'description': object\_data.get('description', '')  
    })  
      
    if not updated\_obj:  
        return None  
      
    *\# Удаляем старые свойства*  
    query \= """  
    MATCH (obj:Object {uri: $object\_uri})-\[r\]-\>(prop:Property)  
    DELETE r, prop  
    """  
    self.\_execute\_query(query, {'object\_uri': object\_uri})  
      
    *\# Добавляем новые свойства*  
    for key, value in object\_data.items():  
        if key not in \['title', 'description'\] and value is not None:  
            *\# Создаем узел свойства*  
            prop\_uri \= f"prop\_{self.generate\_random\_string()}"  
            self.create\_node({  
                'uri': prop\_uri,  
                'value': str(value),  
                'labels': \['Property'\]  
            })  
              
            *\# Создаем связь к свойству*  
            self.create\_arc(object\_uri, prop\_uri, key)  
      
    return updated\_obj

Листинг 18 – Метод update\_object()

Обновляет основные свойства объекта и заменяет все связанные свойства.

### 

### **1.7 Реализация метода сбора signature** {#1.7-реализация-метода-сбора-signature}

#### **1.7.1 Метод collect\_signature** {#1.7.1-метод-collect_signature}

Для сбора всех параметров класса был реализован метод collect\_signature().

def collect\_signature(self, class\_uri: str) \-\> Signature:  
    """  
    Сбор всех (DatatypeProperty) и (ObjectProperty \- range \- Class) узлов у Класса  
      
    Args:  
        class\_uri: URI класса  
          
    Returns:  
        Структура Signature с параметрами класса  
    """  
    *\# Получаем DatatypeProperty (params)*  
    datatype\_query \= """  
    MATCH (c:Class {uri: $class\_uri})\<-\[:applies\_to\]-(dtp:DatatypeProperty)  
    RETURN dtp.uri as uri, dtp.title as title  
    """  
    datatype\_results \= self.\_execute\_query(datatype\_query, {'class\_uri': class\_uri})  
      
    params \= \[SignatureParam(title=result\['title'\], uri=result\['uri'\])   
             for result in datatype\_results\]  
      
    *\# Получаем ObjectProperty (obj\_params)*  
    object\_query \= """  
    MATCH (c:Class {uri: $class\_uri})\<-\[:applies\_to\]-(op:ObjectProperty)-\[:points\_to\]-\>(target:Class)  
    RETURN op.uri as uri, op.title as title, target.uri as target\_class\_uri  
    """  
    object\_results \= self.\_execute\_query(object\_query, {'class\_uri': class\_uri})  
      
    obj\_params \= \[SignatureObjParam(  
        title=result\['title'\],   
        uri=result\['uri'\],   
        target\_class\_uri=result\['target\_class\_uri'\],  
        relation\_direction=1  *\# По умолчанию направление от объекта*  
    ) for result in object\_results\]  
      
    return Signature(params=params, obj\_params=obj\_params)

Листинг 19 – Метод collect\_signature()

Выполняет два запроса для получения DatatypeProperty и ObjectProperty, связанных с классом, и возвращает структуру Signature.

### **1.8 Реализация методов удаления** {#1.8-реализация-методов-удаления}

#### **1.8.1 Метод удаления класса** {#1.8.1-метод-удаления-класса}

Для удаления класса с каскадным удалением был реализован метод delete\_class().

def delete\_class(self, class\_uri: str) \-\> bool:  
    """  
    Удалить класс (его детей, объектов, объектов детей и т.д.)  
      
    Args:  
        class\_uri: URI класса для удаления  
          
    Returns:  
        True если класс удален, False если не найден  
    """  
    *\# Получаем всех потомков класса (рекурсивно)*  
    query \= """  
    MATCH (c:Class {uri: $class\_uri})  
    OPTIONAL MATCH (c)-\[:subclass\_of\*\]-\>(descendant:Class)  
    WITH collect(DISTINCT c) \+ collect(DISTINCT descendant) as classes\_to\_delete  
    UNWIND classes\_to\_delete as class\_to\_delete  
    OPTIONAL MATCH (class\_to\_delete)\<-\[:instance\_of\]-(obj:Object)  
    WITH collect(DISTINCT class\_to\_delete) \+ collect(DISTINCT obj) as nodes\_to\_delete  
    UNWIND nodes\_to\_delete as node\_to\_delete  
    DETACH DELETE node\_to\_delete  
    RETURN count(node\_to\_delete) as deleted\_count  
    """  
      
    results \= self.\_execute\_query(query, {'class\_uri': class\_uri})  
    return results\[0\]\['deleted\_count'\] \> 0 if results else False

Листинг 20 – Метод delete\_class()

Использует рекурсивный поиск для нахождения всех потомков класса и связанных объектов, затем выполняет каскадное удаление.

## **Заключение** {#заключение}

В рамках данного проекта была успешно разработана библиотека OntologyRepository для работы с онтологией в графовой базе данных Neo4j. Основные достижения проекта:

Библиотека готова к использованию в продакшене и может служить основой для более сложных систем, работающих с онтологическими данными. Архитектура системы позволяет легко расширять функциональность и адаптировать под различные бизнес-требования.

## **Список литературы** {#список-литературы}

1. Neo4j Documentation. \[Электронный ресурс\]. URL: [https://neo4j.com/docs/](https://neo4j.com/docs/)  
2. Cypher Query Language Reference. \[Электронный ресурс\]. URL: [https://neo4j.com/docs/cypher-manual/](https://neo4j.com/docs/cypher-manual/)  
3. Python Neo4j Driver Documentation. \[Электронный ресурс\]. URL: [https://neo4j.com/docs/python-manual/](https://neo4j.com/docs/python-manual/)  
4. OWL 2 Web Ontology Language. \[Электронный ресурс\]. URL: [https://www.w3.org/TR/owl2-overview/](https://www.w3.org/TR/owl2-overview/)

