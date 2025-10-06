#!/usr/bin/env python3
"""
Пример использования OntologyRepository для работы с онтологией
"""

import os
from dotenv import load_dotenv
from ontology_repository import OntologyRepository, Signature

load_dotenv()

def main():
    """Основная функция демонстрации работы с онтологией"""
    
    # Инициализация репозитория
    # Замените параметры подключения на ваши
    repo = OntologyRepository(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password'),
        database="ontology"
    )
    
    try:
        print("=== ДЕМОНСТРАЦИЯ РАБОТЫ С ОНТОЛОГИЕЙ ===\n")
        
        # 1. Создание классов
        print("1. Создание классов...")
        
        # Создаем корневой класс "Персона"
        person_class = repo.create_class(
            title="Персона",
            description="Базовый класс для всех персон"
        )
        print(f"Создан класс: {person_class.title} (URI: {person_class.uri})")
        
        # Создаем класс "Автор" как подкласс "Персоны"
        author_class = repo.create_class(
            title="Автор",
            description="Класс для авторов произведений",
            parent_uri=person_class.uri
        )
        print(f"Создан класс: {author_class.title} (URI: {author_class.uri})")
        
        # Создаем класс "Город"
        city_class = repo.create_class(
            title="Город",
            description="Класс для городов"
        )
        print(f"Создан класс: {city_class.title} (URI: {city_class.uri})")
        
        print()
        
        # 2. Добавление атрибутов к классам
        print("2. Добавление атрибутов к классам...")
        
        # Добавляем DatatypeProperty к классу "Автор"
        name_attr = repo.add_class_attribute(
            class_uri=author_class.uri,
            attr_name="имя",
            attr_uri="author_name"
        )
        print(f"Добавлен атрибут: {name_attr.title} (URI: {name_attr.uri})")
        
        age_attr = repo.add_class_attribute(
            class_uri=author_class.uri,
            attr_name="возраст",
            attr_uri="author_age"
        )
        print(f"Добавлен атрибут: {age_attr.title} (URI: {age_attr.uri})")
        
        # Добавляем ObjectProperty к классу "Автор"
        born_in_attr = repo.add_class_object_attribute(
            class_uri=author_class.uri,
            attr_name="родился в",
            range_class_uri=city_class.uri
        )
        print(f"Добавлен объектный атрибут: {born_in_attr.title} (URI: {born_in_attr.uri})")
        
        print()
        
        # 3. Сбор signature класса
        print("3. Сбор signature класса 'Автор'...")
        signature = repo.collect_signature(author_class.uri)
        
        print("DatatypeProperty (params):")
        for param in signature.params:
            print(f"  - {param.title} (URI: {param.uri})")
        
        print("ObjectProperty (obj_params):")
        for obj_param in signature.obj_params:
            print(f"  - {obj_param.title} (URI: {obj_param.uri}, target: {obj_param.target_class_uri})")
        
        print()
        
        # 4. Создание объектов
        print("4. Создание объектов...")
        
        # Создаем объект города
        moscow_obj = repo.create_object(
            class_uri=city_class.uri,
            object_data={
                'title': 'Москва',
                'description': 'Столица России'
            }
        )
        print(f"Создан объект: {moscow_obj.title} (URI: {moscow_obj.uri})")
        
        # Создаем объект автора
        pushkin_obj = repo.create_object(
            class_uri=author_class.uri,
            object_data={
                'title': 'Александр Пушкин',
                'description': 'Русский поэт',
                'имя': 'Александр Сергеевич Пушкин',
                'возраст': '37',
                'родился в': moscow_obj.uri
            }
        )
        print(f"Создан объект: {pushkin_obj.title} (URI: {pushkin_obj.uri})")
        
        print()
        
        # 5. Получение информации о классах
        print("5. Получение информации о классах...")
        
        # Получаем корневые классы
        root_classes = repo.get_ontology_parent_classes()
        print("Корневые классы:")
        for cls in root_classes:
            print(f"  - {cls.title} (URI: {cls.uri})")
        
        # Получаем потомков класса "Персона"
        children = repo.get_class_children(person_class.uri)
        print(f"\nПотомки класса '{person_class.title}':")
        for child in children:
            print(f"  - {child.title} (URI: {child.uri})")
        
        # Получаем объекты класса "Автор"
        author_objects = repo.get_class_objects(author_class.uri)
        print(f"\nОбъекты класса '{author_class.title}':")
        for obj in author_objects:
            print(f"  - {obj.title} (URI: {obj.uri})")
        
        print()
        
        # 6. Обновление класса
        print("6. Обновление класса...")
        updated_author = repo.update_class(
            class_uri=author_class.uri,
            title="Автор произведений",
            description="Класс для авторов литературных произведений"
        )
        if updated_author:
            print(f"Обновлен класс: {updated_author.title} - {updated_author.description}")
        
        print()
        
        # 7. Получение всей онтологии
        print("7. Получение всей онтологии...")
        ontology = repo.get_ontology()
        print(f"Всего узлов в онтологии: {len(ontology)}")
        
        # Группируем по типам
        classes = []
        objects = []
        properties = []
        
        for node in ontology:
            # Получаем метки узла
            query = 'MATCH (n {uri: $uri}) RETURN labels(n) as labels'
            result = repo._execute_query(query, {'uri': node.uri})
            if result:
                labels = result[0]['labels']
                if 'Class' in labels:
                    classes.append(node)
                elif 'Object' in labels:
                    objects.append(node)
                elif 'DatatypeProperty' in labels or 'ObjectProperty' in labels:
                    properties.append(node)
        
        print(f"  - Классов: {len(classes)}")
        print(f"  - Объектов: {len(objects)}")
        print(f"  - Свойств: {len(properties)}")
        
        print("\n=== ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Закрываем соединение
        repo.close()


if __name__ == "__main__":
    main()
