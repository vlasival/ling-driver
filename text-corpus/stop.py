#!/usr/bin/env python3
"""
Остановка всех серверов
"""

import subprocess
import sys
import time
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('config.env')

def stop_server(port):
    """Корректно останавливает сервер на указанном порту"""
    
    print(f'Останавливаем сервер на порту {port}...')
    
    try:
        # Находим процессы на указанном порту
        result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        
        if not result.stdout.strip():
            print(f'Порт {port} уже свободен')
            return True
        
        pids = result.stdout.strip().split('\n')
        
        for pid in pids:
            if pid:
                try:
                    print(f'Завершаем процесс {pid}...')
                    
                    # Сначала пробуем мягкое завершение
                    subprocess.run(['kill', '-TERM', pid], check=True)
                    time.sleep(2)
                    
                    # Проверяем, завершился ли процесс
                    check_result = subprocess.run(['kill', '-0', pid], capture_output=True)
                    if check_result.returncode == 0:
                        # Процесс все еще работает, принудительно завершаем
                        print(f'Принудительно завершаем процесс {pid}...')
                        subprocess.run(['kill', '-9', pid], check=True)
                    
                    print(f'Процесс {pid} завершен')
                    
                except subprocess.CalledProcessError as e:
                    print(f'Ошибка при завершении процесса {pid}: {e}')
        
        # Финальная проверка
        time.sleep(1)
        final_check = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        
        if not final_check.stdout.strip():
            print(f'Сервер на порту {port} успешно остановлен')
            return True
        else:
            print(f'Порт {port} все еще занят')
            return False
            
    except Exception as e:
        print(f'Ошибка при остановке сервера на порту {port}: {e}')
        return False

def main():
    """Основная функция"""
    
    print('Останавливаем все серверы...')
    
    # Останавливаем бэкенд
    backend_port = int(os.getenv('DJANGO_SERVER_PORT', 8000))
    stop_server(backend_port)
    
    # Останавливаем фронтенд
    frontend_port = int(os.getenv('WEB_INTERFACE_PORT', 8001))
    stop_server(frontend_port)
    
    print('Все серверы остановлены')

if __name__ == '__main__':
    main()

