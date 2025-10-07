#!/usr/bin/env python3
"""
Скрипт для корректной остановки Django сервера
"""

import subprocess
import sys
import time

def stop_server(port=8000):
    """Корректно останавливает Django сервер"""
    
    print(f'Останавливаем Django сервер на порту {port}...')
    
    try:
        # Находим процессы на указанном порту
        result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        
        if not result.stdout.strip():
            print(f'Порт {port} уже свободен')
            return True
        
        pids = result.stdout.strip().split('\n')
        stopped_count = 0
        
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
                    
                    stopped_count += 1
                    print(f'Процесс {pid} завершен')
                    
                except subprocess.CalledProcessError as e:
                    print(f'Ошибка при завершении процесса {pid}: {e}')
        
        # Финальная проверка
        time.sleep(1)
        final_check = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        
        if not final_check.stdout.strip():
            print(f'Сервер успешно остановлен, порт {port} освобожден')
            return True
        else:
            print(f'Порт {port} все еще занят')
            return False
            
    except Exception as e:
        print(f'Ошибка при остановке сервера: {e}')
        return False

def main():
    """Основная функция"""
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print('Неверный номер порта')
            sys.exit(1)
    else:
        port = 8000
    
    success = stop_server(port)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
