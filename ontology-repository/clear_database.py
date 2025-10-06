#!/usr/bin/env python3
"""
Универсальный скрипт для очистки базы данных Neo4j
Использование: python3 clear_database.py [database_name]
"""

import sys
import os
from dotenv import load_dotenv
from ontology_repository import OntologyRepository

load_dotenv()

def clear_database(database_name=None):
    """
    Очистка базы данных от всех узлов и связей
    
    Args:
        database_name: Название базы данных (по умолчанию из переменной окружения)
    """
    
    # Определяем базу данных
    if database_name:
        db_name = database_name
    else:
        db_name = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    print(f"=== ОЧИСТКА БАЗЫ ДАННЫХ '{db_name}' ===")
    
    repo = OntologyRepository(
        uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        user=os.getenv('NEO4J_USER', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password'),
        database=db_name
    )
    
    try:
        # Получаем статистику до очистки
        count_query = "MATCH (n) RETURN count(n) as node_count"
        result = repo._execute_query(count_query)
        node_count_before = result[0]['node_count'] if result else 0
        
        print(f"Узлов до очистки: {node_count_before}")
        
        if node_count_before == 0:
            print("✅ База данных уже пуста!")
            return
        
        # Подтверждение от пользователя (только в интерактивном режиме)
        if sys.stdin.isatty():
            confirm = input(f"Вы уверены, что хотите удалить все {node_count_before} узлов? (y/N): ")
            if confirm.lower() not in ['y', 'yes', 'да']:
                print("❌ Очистка отменена")
                return
        else:
            print(f"Автоматическая очистка {node_count_before} узлов...")
        
        # Очищаем все узлы и связи
        print("Очистка базы данных...")
        clear_query = "MATCH (n) DETACH DELETE n"
        repo._execute_query(clear_query)
        
        # Проверяем результат
        result = repo._execute_query(count_query)
        node_count_after = result[0]['node_count'] if result else 0
        
        print(f"Узлов после очистки: {node_count_after}")
        
        # Проверяем связи
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
        rel_result = repo._execute_query(rel_count_query)
        rel_count = rel_result[0]['rel_count'] if rel_result else 0
        
        print(f"Связей после очистки: {rel_count}")
        
        if node_count_after == 0 and rel_count == 0:
            print("✅ База данных успешно очищена!")
        else:
            print("❌ Ошибка при очистке базы данных")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке базы данных: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        repo.close()

def show_help():
    """Показать справку по использованию"""
    print("""
Использование:
    python3 clear_database.py [database_name]

Параметры:
    database_name    - Название базы данных для очистки (опционально)

Примеры:
    python3 clear_database.py                    # Очистить базу по умолчанию
    python3 clear_database.py ontology           # Очистить базу 'ontology'
    python3 clear_database.py test_db            # Очистить базу 'test_db'

Переменные окружения (.env файл):
    NEO4J_URI        - URI подключения (по умолчанию: bolt://localhost:7687)
    NEO4J_USER       - Имя пользователя (по умолчанию: neo4j)
    NEO4J_PASSWORD   - Пароль (по умолчанию: password)
    NEO4J_DATABASE   - База данных по умолчанию (по умолчанию: neo4j)
""")

def main():
    """Основная функция"""
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_help()
            return
        else:
            database_name = sys.argv[1]
    else:
        database_name = None
    
    clear_database(database_name)

if __name__ == "__main__":
    main()
