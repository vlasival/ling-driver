import json
import sys
import os
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

# Добавляем путь к папке neo4j-driver для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'neo4j-driver'))
from graph_repository import GraphRepository, TNode, TArc


@dataclass
class SignatureParam:
    """Параметр DatatypeProperty в signature"""
    title: str
    uri: str


@dataclass
class SignatureObjParam:
    """Параметр ObjectProperty в signature"""
    title: str
    uri: str
    target_class_uri: str
    relation_direction: int  # 1 - от объекта, -1 - к объекту


@dataclass
class Signature:
    """Структура signature для класса"""
    params: List[SignatureParam]  # DatatypeProperty
    obj_params: List[SignatureObjParam]  # ObjectProperty


class OntologyRepository(GraphRepository):
    """Репозиторий для работы с онтологией в графовой базе данных Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = None):
        """
        Инициализация репозитория онтологии
        
        Args:
            uri: URI подключения к Neo4j
            user: Имя пользователя
            password: Пароль
            database: Название базы данных
        """
        super().__init__(uri, user, password, database)
    
    # ==================== ОСНОВНЫЕ МЕТОДЫ ОНТОЛОГИИ ====================
    
    def get_ontology(self) -> List[TNode]:
        """
        Получить всю онтологию (все узлы с метками Class, Object, DatatypeProperty, ObjectProperty)
        
        Returns:
            Список всех узлов онтологии
        """
        return self.get_all_nodes()
    
    def get_ontology_parent_classes(self) -> List[TNode]:
        """
        Получить классы онтологии, у которых нет родителей
        
        Returns:
            Список корневых классов
        """
        query = """
        MATCH (c:Class)
        WHERE NOT (c)-[:subclass_of]->()
        RETURN elementId(c) as element_id, c.uri as uri, c.description as description, c.title as title
        """
        results = self._execute_query(query)
        return [self.collect_node(result) for result in results]
    
    # ==================== МЕТОДЫ РАБОТЫ С КЛАССАМИ ====================
    
    def get_class(self, class_uri: str) -> Optional[TNode]:
        """
        Получить класс по URI
        
        Args:
            class_uri: URI класса
            
        Returns:
            Класс или None, если не найден
        """
        query = """
        MATCH (c:Class {uri: $class_uri})
        RETURN elementId(c) as element_id, c.uri as uri, c.description as description, c.title as title
        """
        results = self._execute_query(query, {'class_uri': class_uri})
        if results:
            return self.collect_node(results[0])
        return None
    
    def get_class_parents(self, class_uri: str) -> List[TNode]:
        """
        Получить родителей класса
        
        Args:
            class_uri: URI класса
            
        Returns:
            Список родительских классов
        """
        query = """
        MATCH (c:Class {uri: $class_uri})-[:subclass_of]->(parent:Class)
        RETURN elementId(parent) as element_id, parent.uri as uri, parent.description as description, parent.title as title
        """
        results = self._execute_query(query, {'class_uri': class_uri})
        return [self.collect_node(result) for result in results]
    
    def get_class_children(self, class_uri: str) -> List[TNode]:
        """
        Получить потомков класса
        
        Args:
            class_uri: URI класса
            
        Returns:
            Список дочерних классов
        """
        query = """
        MATCH (c:Class {uri: $class_uri})<-[:subclass_of]-(child:Class)
        RETURN elementId(child) as element_id, child.uri as uri, child.description as description, child.title as title
        """
        results = self._execute_query(query, {'class_uri': class_uri})
        return [self.collect_node(result) for result in results]
    
    def get_class_objects(self, class_uri: str) -> List[TNode]:
        """
        Получить объекты класса
        
        Args:
            class_uri: URI класса
            
        Returns:
            Список объектов класса
        """
        query = """
        MATCH (c:Class {uri: $class_uri})<-[:instance_of]-(obj:Object)
        RETURN elementId(obj) as element_id, obj.uri as uri, obj.description as description, obj.title as title
        """
        results = self._execute_query(query, {'class_uri': class_uri})
        return [self.collect_node(result) for result in results]
    
    def update_class(self, class_uri: str, title: str, description: str) -> Optional[TNode]:
        """
        Обновить класс (имя и описание)
        
        Args:
            class_uri: URI класса
            title: Новое название
            description: Новое описание
            
        Returns:
            Обновленный класс или None, если не найден
        """
        return self.update_node(class_uri, {'title': title, 'description': description})
    
    def create_class(self, title: str, description: str, parent_uri: Optional[str] = None) -> TNode:
        """
        Создать класс (имя, описание, родитель)
        
        Args:
            title: Название класса
            description: Описание класса
            parent_uri: URI родительского класса (опционально)
            
        Returns:
            Созданный класс
        """
        # Генерируем URI для класса
        class_uri = f"class_{self.generate_random_string()}"
        
        # Создаем класс
        class_node = self.create_node({
            'uri': class_uri,
            'title': title,
            'description': description,
            'labels': ['Class']
        })
        
        # Если указан родитель, создаем связь
        if parent_uri:
            self.create_arc(class_uri, parent_uri, 'subclass_of')
        
        return class_node
    
    def delete_class(self, class_uri: str) -> bool:
        """
        Удалить класс (его детей, объектов, объектов детей и т.д.)
        
        Args:
            class_uri: URI класса для удаления
            
        Returns:
            True если класс удален, False если не найден
        """
        # Получаем всех потомков класса (рекурсивно)
        query = """
        MATCH (c:Class {uri: $class_uri})
        OPTIONAL MATCH (c)-[:subclass_of*]->(descendant:Class)
        WITH collect(DISTINCT c) + collect(DISTINCT descendant) as classes_to_delete
        UNWIND classes_to_delete as class_to_delete
        OPTIONAL MATCH (class_to_delete)<-[:instance_of]-(obj:Object)
        WITH collect(DISTINCT class_to_delete) + collect(DISTINCT obj) as nodes_to_delete
        UNWIND nodes_to_delete as node_to_delete
        DETACH DELETE node_to_delete
        RETURN count(node_to_delete) as deleted_count
        """
        
        results = self._execute_query(query, {'class_uri': class_uri})
        return results[0]['deleted_count'] > 0 if results else False
    
    # ==================== МЕТОДЫ РАБОТЫ С АТРИБУТАМИ КЛАССОВ ====================
    
    def add_class_attribute(self, class_uri: str, attr_name: str, attr_uri: Optional[str] = None) -> TNode:
        """
        Добавить DatatypeProperty к классу
        
        Args:
            class_uri: URI класса
            attr_name: Название атрибута
            attr_uri: URI атрибута (если не указан, генерируется автоматически)
            
        Returns:
            Созданный DatatypeProperty
        """
        if not attr_uri:
            attr_uri = f"attr_{self.generate_random_string()}"
        
        # Создаем DatatypeProperty
        attr_node = self.create_node({
            'uri': attr_uri,
            'title': attr_name,
            'description': f"DatatypeProperty for {attr_name}",
            'labels': ['DatatypeProperty']
        })
        
        # Создаем связь domain
        self.create_arc(attr_uri, class_uri, 'applies_to')
        
        return attr_node
    
    def delete_class_attribute(self, class_uri: str, attr_uri: str) -> bool:
        """
        Удалить DatatypeProperty у класса
        
        Args:
            class_uri: URI класса
            attr_uri: URI атрибута
            
        Returns:
            True если атрибут удален, False если не найден
        """
        # Удаляем связь domain и сам атрибут
        query = """
        MATCH (attr:DatatypeProperty {uri: $attr_uri})-[r:applies_to]->(c:Class {uri: $class_uri})
        DELETE r
        WITH attr
        DETACH DELETE attr
        RETURN count(attr) as deleted_count
        """
        
        results = self._execute_query(query, {'class_uri': class_uri, 'attr_uri': attr_uri})
        return results[0]['deleted_count'] > 0 if results else False
    
    def add_class_object_attribute(self, class_uri: str, attr_name: str, range_class_uri: str) -> TNode:
        """
        Добавить ObjectProperty к классу
        
        Args:
            class_uri: URI класса
            attr_name: Название атрибута
            range_class_uri: URI класса-диапазона
            
        Returns:
            Созданный ObjectProperty
        """
        attr_uri = f"obj_attr_{self.generate_random_string()}"
        
        # Создаем ObjectProperty
        attr_node = self.create_node({
            'uri': attr_uri,
            'title': attr_name,
            'description': f"ObjectProperty for {attr_name}",
            'labels': ['ObjectProperty']
        })
        
        # Создаем связь domain
        self.create_arc(attr_uri, class_uri, 'applies_to')
        
        # Создаем связь range
        self.create_arc(attr_uri, range_class_uri, 'points_to')
        
        return attr_node
    
    def delete_class_object_attribute(self, object_property_uri: str) -> bool:
        """
        Удалить ObjectProperty
        
        Args:
            object_property_uri: URI ObjectProperty
            
        Returns:
            True если атрибут удален, False если не найден
        """
        return self.delete_node_by_uri(object_property_uri)
    
    def add_class_parent(self, parent_uri: str, target_uri: str) -> bool:
        """
        Присоединить родителя к классу (без создания родителя, из существующих классов)
        
        Args:
            parent_uri: URI родительского класса
            target_uri: URI целевого класса
            
        Returns:
            True если связь создана, False если классы не найдены
        """
        try:
            self.create_arc(target_uri, parent_uri, 'subclass_of')
            return True
        except Exception:
            return False
    
    # ==================== МЕТОДЫ РАБОТЫ С ОБЪЕКТАМИ ====================
    
    def get_object(self, object_uri: str) -> Optional[TNode]:
        """
        Получить объект по URI
        
        Args:
            object_uri: URI объекта
            
        Returns:
            Объект или None, если не найден
        """
        query = """
        MATCH (obj:Object {uri: $object_uri})
        RETURN elementId(obj) as element_id, obj.uri as uri, obj.description as description, obj.title as title
        """
        results = self._execute_query(query, {'object_uri': object_uri})
        if results:
            return self.collect_node(results[0])
        return None
    
    def delete_object(self, object_uri: str) -> bool:
        """
        Удалить объект
        
        Args:
            object_uri: URI объекта
            
        Returns:
            True если объект удален, False если не найден
        """
        return self.delete_node_by_uri(object_uri)
    
    def create_object(self, class_uri: str, object_data: Dict[str, Any]) -> TNode:
        """
        Создать объект через collect_signature
        
        Args:
            class_uri: URI класса
            object_data: Данные объекта (title, description, свойства)
            
        Returns:
            Созданный объект
        """
        # Генерируем URI для объекта
        object_uri = f"obj_{self.generate_random_string()}"
        
        # Создаем объект
        obj_node = self.create_node({
            'uri': object_uri,
            'title': object_data.get('title', ''),
            'description': object_data.get('description', ''),
            'labels': ['Object']
        })
        
        # Создаем связь instance_of
        self.create_arc(object_uri, class_uri, 'instance_of')
        
        # Добавляем свойства объекта
        for key, value in object_data.items():
            if key not in ['title', 'description'] and value is not None:
                # Создаем узел свойства
                prop_uri = f"prop_{self.generate_random_string()}"
                self.create_node({
                    'uri': prop_uri,
                    'value': str(value),
                    'labels': ['Property']
                })
                
                # Создаем связь к свойству
                self.create_arc(object_uri, prop_uri, key)
        
        return obj_node
    
    def update_object(self, object_uri: str, object_data: Dict[str, Any]) -> Optional[TNode]:
        """
        Обновить объект через collect_signature
        
        Args:
            object_uri: URI объекта
            object_data: Новые данные объекта
            
        Returns:
            Обновленный объект или None, если не найден
        """
        # Обновляем основные свойства объекта
        updated_obj = self.update_node(object_uri, {
            'title': object_data.get('title', ''),
            'description': object_data.get('description', '')
        })
        
        if not updated_obj:
            return None
        
        # Удаляем старые свойства
        query = """
        MATCH (obj:Object {uri: $object_uri})-[r]->(prop:Property)
        DELETE r, prop
        """
        self._execute_query(query, {'object_uri': object_uri})
        
        # Добавляем новые свойства
        for key, value in object_data.items():
            if key not in ['title', 'description'] and value is not None:
                # Создаем узел свойства
                prop_uri = f"prop_{self.generate_random_string()}"
                self.create_node({
                    'uri': prop_uri,
                    'value': str(value),
                    'labels': ['Property']
                })
                
                # Создаем связь к свойству
                self.create_arc(object_uri, prop_uri, key)
        
        return updated_obj
    
    # ==================== МЕТОД СБОРА SIGNATURE ====================
    
    def collect_signature(self, class_uri: str) -> Signature:
        """
        Сбор всех (DatatypeProperty) и (ObjectProperty - range - Class) узлов у Класса
        
        Args:
            class_uri: URI класса
            
        Returns:
            Структура Signature с параметрами класса
        """
        # Получаем DatatypeProperty (params)
        datatype_query = """
        MATCH (c:Class {uri: $class_uri})<-[:applies_to]-(dtp:DatatypeProperty)
        RETURN dtp.uri as uri, dtp.title as title
        """
        datatype_results = self._execute_query(datatype_query, {'class_uri': class_uri})
        
        params = [SignatureParam(title=result['title'], uri=result['uri']) 
                 for result in datatype_results]
        
        # Получаем ObjectProperty (obj_params)
        object_query = """
        MATCH (c:Class {uri: $class_uri})<-[:applies_to]-(op:ObjectProperty)-[:points_to]->(target:Class)
        RETURN op.uri as uri, op.title as title, target.uri as target_class_uri
        """
        object_results = self._execute_query(object_query, {'class_uri': class_uri})
        
        obj_params = [SignatureObjParam(
            title=result['title'], 
            uri=result['uri'], 
            target_class_uri=result['target_class_uri'],
            relation_direction=1  # По умолчанию направление от объекта
        ) for result in object_results]
        
        return Signature(params=params, obj_params=obj_params)
