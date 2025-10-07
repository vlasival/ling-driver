#!/usr/bin/env python3
"""
Скрипт для запуска веб-интерфейса Text Corpus Management
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("Запуск веб-интерфейса Text Corpus Management...")
    
    # Проверяем, что мы в правильной директории
    if not os.path.exists('manage.py'):
        print("Ошибка: manage.py не найден. Запустите скрипт из директории text-corpus/")
        sys.exit(1)
    
    # Проверяем наличие шаблонов
    if not os.path.exists('db/templates'):
        print("Ошибка: директория db/templates не найдена")
        sys.exit(1)
    
    print("Проверки пройдены")
    print("Запускаем Django сервер...")
    
    # Запускаем сервер
    try:
        # Используем наш кастомный скрипт для запуска сервера
        subprocess.run([sys.executable, 'run_server.py', '8000'], check=True)
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска сервера: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
