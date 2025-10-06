import json
import random
import string
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from neo4j import GraphDatabase


@dataclass
class TNode:
    """Структура узла графа"""
    id: str  # element ID
    uri: str
    description: str
    title: str
    arcs: Optional[List['TArc']] = None


@dataclass
class TArc:
    """Структура связи графа"""
    id: str  # element ID
    uri: str  # arc.type
    node_uri_from: str
    node_uri_to: str


class GraphRepository:
    """Репозиторий для работы с графовой базой данных Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = None):
        """
        Инициализация репозитория
        
        Args:
            uri: URI подключения к Neo4j
            user: Имя пользователя
            password: Пароль
            database: Название базы данных (по умолчанию используется системная база)
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Выполнение запроса к базе данных
        
        Args:
            query: Cypher запрос
            parameters: Параметры запроса
            
        Returns:
            Список результатов запроса
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def generate_random_string(self, length: int = 10) -> str:
        """
        Генерация случайной строки для URI узла
        
        Args:
            length: Длина генерируемой строки
            
        Returns:
            Случайная строка
        """
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    
    def _build_labels_clause(self, labels: List[str]) -> str:
        """
        Безопасное построение строки меток для Cypher запроса
        
        Args:
            labels: Список меток
            
        Returns:
            Строка меток в формате Cypher
        """
        if not labels:
            return ''
        # Безопасно экранируем метки
        escaped_labels = [f"`{label.replace('`', '``')}`" for label in labels]
        return ':' + ':'.join(escaped_labels)
    
    def collect_node(self, node_data: Dict[str, Any]) -> TNode:
        """
        Трансформация данных узла из БД в объект TNode
        
        Args:
            node_data: Данные узла из базы данных
            
        Returns:
            Объект TNode
        """
        return TNode(
            id=node_data.get('element_id', ''),
            uri=node_data.get('uri', ''),
            description=node_data.get('description', ''),
            title=node_data.get('title', ''),
            arcs=node_data.get('arcs', [])
        )
    
    def collect_arc(self, arc_data: Dict[str, Any]) -> TArc:
        """
        Трансформация данных связи из БД в объект TArc
        
        Args:
            arc_data: Данные связи из базы данных
            
        Returns:
            Объект TArc
        """
        return TArc(
            id=arc_data.get('element_id', ''),
            uri=arc_data.get('uri', ''),
            node_uri_from=arc_data.get('node_uri_from', ''),
            node_uri_to=arc_data.get('node_uri_to', '')
        )
    
    def get_all_nodes(self) -> List[TNode]:
        """
        Получить все узлы графа
        
        Returns:
            Список всех узлов
        """
        query = """
        MATCH (n)
        RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
        """
        results = self._execute_query(query)
        return [self.collect_node(result) for result in results]
    
    def get_all_nodes_and_arcs(self) -> List[TNode]:
        """
        Получить все узлы с их связями
        
        Returns:
            Список узлов с их связями
        """
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
            # Фильтруем пустые связи (когда узел не имеет исходящих связей)
            node.arcs = [self.collect_arc(arc) for arc in result.get('arcs', []) if arc.get('element_id')]
            nodes.append(node)
        return nodes
    
    def get_nodes_by_labels(self, labels: List[str]) -> List[TNode]:
        """
        Получить выборку узлов по их меткам
        
        Args:
            labels: Список меток для поиска
            
        Returns:
            Список узлов с указанными метками
        """
        if not labels:
            return []
        
        labels_clause = self._build_labels_clause(labels)
        query = f"""
        MATCH (n{labels_clause})
        RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
        """
        results = self._execute_query(query)
        return [self.collect_node(result) for result in results]
    
    def get_node_by_uri(self, uri: str) -> Optional[TNode]:
        """
        Получить узел по URI
        
        Args:
            uri: URI узла
            
        Returns:
            Узел или None, если не найден
        """
        query = """
            MATCH (n {uri: $uri})
            RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
        """
        results = self._execute_query(query, {'uri': uri})
        if results:
            return self.collect_node(results[0])
        return None
    
    def create_node(self, params: Dict[str, Any]) -> TNode:
        """
        Создать новый узел
        
        Args:
            params: Параметры узла (title, description, labels и т.д.)
            
        Returns:
            Созданный узел
        """
        # Генерируем URI если не указан
        if 'uri' not in params:
            params['uri'] = f"node_{self.generate_random_string()}"
        
        # Извлекаем метки если есть
        labels = params.pop('labels', [])
        labels_clause = self._build_labels_clause(labels)
        
        # Создаем параметры для безопасного запроса
        query_params = params.copy()
        
        query = f"""
        CREATE (n{labels_clause} $props)
        RETURN elementId(n) as element_id, n.uri as uri, n.description as description, n.title as title
        """
        
        results = self._execute_query(query, {'props': query_params})
        if results:
            return self.collect_node(results[0])
        raise Exception("Не удалось создать узел")
    
    def create_arc(self, node1_uri: str, node2_uri: str, arc_type: str = "RELATES_TO", properties: Dict[str, Any] = None) -> TArc:
        """
        Создать связь между узлами
        
        Args:
            node1_uri: URI первого узла
            node2_uri: URI второго узла
            arc_type: Тип связи
            properties: Дополнительные свойства связи
            
        Returns:
            Созданная связь
        """
        # Безопасно экранируем тип связи
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
    
    def delete_node_by_uri(self, uri: str) -> bool:
        """
        Удалить узел по URI
        
        Args:
            uri: URI узла для удаления
            
        Returns:
            True если узел удален, False если не найден
        """
        query = """
        MATCH (n {uri: $uri})
        DETACH DELETE n
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, {'uri': uri})
            # Получаем статистику выполнения запроса
            summary = result.consume()
            return summary.counters.nodes_deleted > 0
    
    def delete_arc_by_id(self, arc_id: str) -> bool:
        """
        Удалить связь по element ID
        
        Args:
            arc_id: Element ID связи для удаления
            
        Returns:
            True если связь удалена, False если не найдена
        """
        query = """
        MATCH ()-[r]->()
        WHERE elementId(r) = $arc_id
        DELETE r
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, {'arc_id': arc_id})
            # Получаем статистику выполнения запроса
            summary = result.consume()
            return summary.counters.relationships_deleted > 0
    
    def update_node(self, uri: str, params: Dict[str, Any]) -> Optional[TNode]:
        """
        Обновить узел
        
        Args:
            uri: URI узла для обновления
            params: Новые параметры узла
            
        Returns:
            Обновленный узел или None если не найден
        """
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
    
    def run_custom_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Выполнение произвольного запроса Cypher
        
        Args:
            query: Cypher запрос
            parameters: Параметры запроса
            
        Returns:
            Результаты запроса
        """
        return self._execute_query(query, parameters)
