#!/usr/bin/env python3
"""
Скрипт для корректного запуска Django сервера с graceful shutdown
"""

import os
import sys
import signal
import subprocess
import time
from pathlib import Path

def signal_handler(sig, frame):
    """Обработчик сигналов для корректного завершения"""
    print('\nПолучен сигнал завершения, останавливаем сервер...')
    
    # Находим и завершаем процесс Django сервера
    try:
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f'Завершаем процесс {pid}')
                    subprocess.run(['kill', '-TERM', pid], check=False)
                    time.sleep(1)
                    # Если процесс не завершился, принудительно
                    subprocess.run(['kill', '-9', pid], check=False)
    except Exception as e:
        print(f'Ошибка при завершении процессов: {e}')
    
    print('Сервер корректно остановлен')
    sys.exit(0)

def main():
    """Основная функция запуска сервера"""
    
    # Устанавливаем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Проверяем, что мы в правильной директории
    if not Path('manage.py').exists():
        print('Файл manage.py не найден. Запустите скрипт из директории Django проекта.')
        sys.exit(1)
    
    # Проверяем, свободен ли порт
    try:
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.stdout.strip():
            print('Порт 8000 занят, освобождаем...')
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], check=False)
            time.sleep(2)
    except Exception:
        pass
    
    print('Запускаем Django сервер на порту 8000...')
    print('Для остановки используйте Ctrl+C')
    print('=' * 50)
    
    try:
        # Запускаем Django сервер
        process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '8000'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Выводим логи в реальном времени
        for line in process.stdout:
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print('\nПолучен сигнал прерывания')
    except Exception as e:
        print(f'Ошибка запуска сервера: {e}')
    finally:
        # Корректно завершаем процесс
        if 'process' in locals():
            print('Завершаем процесс сервера...')
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        # Дополнительная очистка порта
        try:
            result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
        except Exception:
            pass
        
        print('Сервер корректно остановлен, порт освобожден')

if __name__ == '__main__':
    main()
