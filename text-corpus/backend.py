#!/usr/bin/env python3
"""
Запуск бэкенда (API сервер)
"""

import os
import sys
import signal
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('config.env')

def signal_handler(sig, frame, port):
    """Обработчик сигналов для корректного завершения"""
    print('\nПолучен сигнал завершения, останавливаем бэкенд...')
    
    try:
        result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f'Завершаем процесс {pid}')
                    subprocess.run(['kill', '-TERM', pid], check=False)
                    time.sleep(1)
                    subprocess.run(['kill', '-9', pid], check=False)
    except Exception as e:
        print(f'Ошибка при завершении процессов: {e}')
    
    print('Бэкенд корректно остановлен')
    sys.exit(0)

def main():
    """Основная функция запуска бэкенда"""
    
    # Получаем порт из переменных окружения
    port = int(os.getenv('DJANGO_SERVER_PORT', 8000))
    
    # Устанавливаем обработчики сигналов
    def handler(sig, frame):
        signal_handler(sig, frame, port)
    
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    # Проверяем, что мы в правильной директории
    if not Path('manage.py').exists():
        print('Файл manage.py не найден. Запустите скрипт из директории Django проекта.')
        sys.exit(1)
    
    # Проверяем, свободен ли порт
    try:
        result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            print(f'Порт {port} занят, освобождаем...')
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], check=False)
            time.sleep(2)
    except Exception:
        pass
    
    print(f'Запускаем бэкенд (API сервер) на порту {port}...')
    print('Для остановки используйте Ctrl+C')
    print('=' * 50)
    
    try:
        # Запускаем Django сервер
        process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', str(port)
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Выводим логи в реальном времени
        for line in process.stdout:
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print('\nПолучен сигнал прерывания')
    except Exception as e:
        print(f'Ошибка запуска бэкенда: {e}')
    finally:
        # Корректно завершаем процесс
        if 'process' in locals():
            print('Завершаем процесс бэкенда...')
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        # Дополнительная очистка порта
        try:
            result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
        except Exception:
            pass
        
        print('Бэкенд корректно остановлен, порт освобожден')

if __name__ == '__main__':
    main()

