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
**Разработка хранилища корпуса текстов** 

Новосибирск 2025 

[Введение	3](#введение)

[1. Реализация алгоритма	3](#1.-реализация-алгоритма)

[1.1 Архитектура системы	3](#1.1-архитектура-системы)

[1.2 Модели данных	4](#1.2-модели-данных)

[1.2.1 Модель Corpus	4](#1.2.1-модель-corpus)

[1.2.2 Модель Text	5](#1.2.2-модель-text)

[1.2.3 Модель Test	6](#1.2.3-модель-test)

[1.3 Реализация репозиториев	6](#1.3-реализация-репозиториев)

[1.3.1 CorpusRepository	6](#1.3.1-corpusrepository)

[1.3.2 TextRepository	8](#1.3.2-textrepository)

[1.3.3 Интеграция Neo4j репозиториев	10](#1.3.3-интеграция-neo4j-репозиториев)

[1.4 Реализация REST API	11](#1.4-реализация-rest-api)

[1.4.1 Corpus API Endpoints	11](#1.4.1-corpus-api-endpoints)

[1.4.2 Text API Endpoints	13](#1.4.2-text-api-endpoints)

[1.4.3 Ontology API Endpoints	15](#1.4.3-ontology-api-endpoints)

[1.5 Настройка Django проекта	17](#1.5-настройка-django-проекта)

[1.5.1 Конфигурация settings.py	17](#1.5.1-конфигурация-settingspy)

[1.5.2 URL маршрутизация	18](#1.5.2-url-маршрутизация)

[1.5.3 Миграции базы данных	19](#1.5.3-миграции-базы-данных)

[1.6 Управление сервером	19](#1.6-управление-сервером)

[1.6.1 Скрипт запуска сервера	19](#1.6.1-скрипт-запуска-сервера)

[1.6.2 Скрипт остановки сервера	21](#1.6.2-скрипт-остановки-сервера)

[2. Тестирование и валидация	22](#2.-тестирование-и-валидация)

[2.1 Функциональное тестирование	22](#2.1-функциональное-тестирование)

[2.2 Тестирование на реальных данных	23](#2.2-тестирование-на-реальных-данных)

[2.3 Результаты тестирования	24](#2.3-результаты-тестирования)

[Заключение	25](#заключение)

[Список литературы	26](#список-литературы)

## Введение

В рамках данного проекта была разработана система хранения и управления корпусом текстов на основе Django веб-фреймворка с интеграцией Neo4j для работы с онтологиями. Целью проекта являлось создание полнофункционального REST API для управления текстовыми корпусами, отдельными текстами и их взаимосвязями, а также интеграция с ранее разработанными репозиториями для работы с графовыми данными.

Система представляет собой современное веб-приложение, которое позволяет хранить и управлять корпусами текстов различных жанров, создавать и редактировать отдельные тексты, устанавливать связи между текстами (например, переводы), а также работать с онтологическими данными через интегрированные Neo4j репозитории.

Разработанная система обеспечивает масштабируемость, надежность и удобство использования благодаря использованию современных технологий и лучших практик разработки.

## 1. Реализация алгоритма

### 1.1 Архитектура системы

Для реализации системы хранения корпуса текстов была выбрана архитектура на основе Django REST Framework с интеграцией Neo4j. Основные компоненты системы представлены на рисунке 1.

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Web Application                   │
├─────────────────────────────────────────────────────────────┤
│  REST API Layer (views.py)                                 │
│  ├── Corpus API Endpoints                                  │
│  ├── Text API Endpoints                                    │
│  └── Ontology API Endpoints                                │
├─────────────────────────────────────────────────────────────┤
│  Repository Layer                                          │
│  ├── CorpusRepository                                      │
│  ├── TextRepository                                        │
│  ├── OntologyRepository (Neo4j)                           │
│  └── GraphRepository (Neo4j)                              │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├── SQLite Database (Corpus, Text models)                │
│  └── Neo4j Database (Ontology)                            │
└─────────────────────────────────────────────────────────────┘
```

Рисунок 1 – Архитектура системы

Система построена по принципу многослойной архитектуры с четким разделением ответственности между компонентами.

### 1.2 Модели данных

#### 1.2.1 Модель Corpus

Для представления корпуса текстов была создана модель Corpus, приведенная на листинге 1.

```python
class Corpus(models.Model):
    """Модель корпуса текстов"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    genre = models.CharField(max_length=100, verbose_name="Жанр", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпуса"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/api/corpus/{self.pk}/"
```

Листинг 1 – Модель Corpus

Модель включает основные поля для описания корпуса: название, описание, жанр и временные метки для отслеживания изменений.

#### 1.2.2 Модель Text

Для представления отдельных текстов была создана модель Text, приведенная на листинге 2.

```python
class Text(models.Model):
    """Модель текста"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    text = models.TextField(verbose_name="Текст", validators=[MinLengthValidator(10)])
    corpus = models.ForeignKey(
        Corpus, 
        on_delete=models.CASCADE, 
        related_name='texts',
        verbose_name="Корпус"
    )
    has_translation = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='translations',
        verbose_name="Перевод"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Текст"
        verbose_name_plural = "Тексты"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/api/text/{self.pk}/"
```

Листинг 2 – Модель Text

Модель включает связь с корпусом через ForeignKey и self-reference для поддержки переводов текстов.

#### 1.2.3 Модель Test

Для совместимости с существующим кодом была сохранена модель Test, приведенная на листинге 3.

```python
class Test(models.Model):
    """Тестовая модель для совместимости"""
    name = models.TextField()

    def __str__(self):
        return self.name
```

Листинг 3 – Модель Test

### 1.3 Реализация репозиториев

#### 1.3.1 CorpusRepository

Для работы с корпусами был реализован репозиторий CorpusRepository, приведенный на листинге 4.

```python
class CorpusRepository:
    """Репозиторий для работы с корпусами текстов"""
    
    def __init__(self):
        pass

    def collect_corpus(self, corpus: Corpus) -> Dict[str, Any]:
        """
        Трансформация объекта Corpus в словарь
        
        Args:
            corpus: Объект Corpus
            
        Returns:
            Словарь с данными корпуса
        """
        return {
            'id': corpus.pk,
            'name': corpus.name,
            'description': corpus.description,
            'genre': corpus.genre,
            'created_at': corpus.created_at.isoformat(),
            'updated_at': corpus.updated_at.isoformat(),
            'texts_count': corpus.texts.count()
        }

    def collect_corpus_with_texts(self, corpus: Corpus) -> Dict[str, Any]:
        """
        Трансформация объекта Corpus со всеми текстами в словарь
        
        Args:
            corpus: Объект Corpus
            
        Returns:
            Словарь с данными корпуса и текстами
        """
        corpus_data = self.collect_corpus(corpus)
        corpus_data['texts'] = [
            {
                'id': text.pk,
                'name': text.name,
                'description': text.description,
                'text_preview': text.text[:200] + '...' if len(text.text) > 200 else text.text,
                'created_at': text.created_at.isoformat(),
                'has_translation_id': text.has_translation.pk if text.has_translation else None
            }
            for text in corpus.texts.all()
        ]
        return corpus_data
```

Листинг 4 – CorpusRepository

Репозиторий обеспечивает трансформацию объектов Django в словари для API и включает методы для работы с текстами корпуса.

#### 1.3.2 TextRepository

Для работы с текстами был реализован репозиторий TextRepository, приведенный на листинге 5.

```python
class TextRepository:
    """Репозиторий для работы с текстами"""
    
    def __init__(self):
        pass

    def collect_text(self, text: Text) -> Dict[str, Any]:
        """
        Трансформация объекта Text в словарь
        
        Args:
            text: Объект Text
            
        Returns:
            Словарь с данными текста
        """
        return {
            'id': text.pk,
            'name': text.name,
            'description': text.description,
            'text': text.text,
            'corpus_id': text.corpus.pk,
            'corpus_name': text.corpus.name,
            'has_translation_id': text.has_translation.pk if text.has_translation else None,
            'has_translation_name': text.has_translation.name if text.has_translation else None,
            'created_at': text.created_at.isoformat(),
            'updated_at': text.updated_at.isoformat()
        }

    def create_text(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новый текст
        
        Args:
            text_data: Данные текста
            
        Returns:
            Словарь с данными созданного текста
        """
        text = Text()
        text.name = text_data.get('name', '')
        text.description = text_data.get('description', '')
        text.text = text_data.get('text', '')
        
        # Устанавливаем корпус
        corpus_id = text_data.get('corpus_id')
        if corpus_id:
            try:
                corpus = Corpus.objects.get(pk=corpus_id)
                text.corpus = corpus
            except Corpus.DoesNotExist:
                raise ValueError(f"Корпус с ID {corpus_id} не найден")
        else:
            raise ValueError("Не указан corpus_id")
        
        # Устанавливаем перевод если указан
        translation_id = text_data.get('has_translation_id')
        if translation_id:
            try:
                translation = Text.objects.get(pk=translation_id)
                text.has_translation = translation
            except Text.DoesNotExist:
                raise ValueError(f"Текст-перевод с ID {translation_id} не найден")
        
        text.save()
        return self.collect_text(text)
```

Листинг 5 – TextRepository

Репозиторий обеспечивает полный жизненный цикл текстов с поддержкой связей с корпусами и переводами.

#### 1.3.3 Интеграция Neo4j репозиториев

Для интеграции с Neo4j были скопированы и адаптированы репозитории из предыдущих работ, как показано на листинге 6.

```python
# Интеграция в views.py
from db.api.ontology_repository import OntologyRepository
from db.api.graph_repository import GraphRepository

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_ontology(request):
    """Получить всю онтологию"""
    try:
        from django.conf import settings
        ontology_repo = OntologyRepository(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE
        )
        
        ontology = ontology_repo.get_ontology()
        ontology_repo.close()
        
        # Преобразуем TNode в словари
        ontology_data = []
        for node in ontology:
            ontology_data.append({
                'id': node.id,
                'uri': node.uri,
                'title': node.title,
                'description': node.description
            })
        
        return Response(ontology_data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

Листинг 6 – Интеграция Neo4j репозиториев

### 1.4 Реализация REST API

#### 1.4.1 Corpus API Endpoints

Для работы с корпусами были реализованы следующие endpoints, приведенные на листинге 7.

```python
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_corpus(request):
    """Получить корпус по ID"""
    corpus_id = request.GET.get('id', None)
    if corpus_id is None:
        return Response({'error': 'ID корпуса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        corpus_id = int(corpus_id)
    except ValueError:
        return Response({'error': 'Неверный формат ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    corpus_repo = CorpusRepository()
    corpus = corpus_repo.get_corpus(corpus_id)
    
    if corpus is None:
        return Response({'error': 'Корпус не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(corpus)

@api_view(['POST'])
@permission_classes((AllowAny,))
def create_corpus(request):
    """Создать новый корпус"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Неверный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
    
    corpus_repo = CorpusRepository()
    try:
        corpus = corpus_repo.create_corpus(data)
        return Response(corpus, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

Листинг 7 – Corpus API Endpoints

#### 1.4.2 Text API Endpoints

Для работы с текстами были реализованы следующие endpoints, приведенные на листинге 8.

```python
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_text(request):
    """Получить текст по ID"""
    text_id = request.GET.get('id', None)
    if text_id is None:
        return Response({'error': 'ID текста не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        text_id = int(text_id)
    except ValueError:
        return Response({'error': 'Неверный формат ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    text_repo = TextRepository()
    text = text_repo.get_text(text_id)
    
    if text is None:
        return Response({'error': 'Текст не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(text)

@api_view(['POST'])
@permission_classes((AllowAny,))
def create_text(request):
    """Создать новый текст"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Неверный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
    
    text_repo = TextRepository()
    try:
        text = text_repo.create_text(data)
        return Response(text, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

Листинг 8 – Text API Endpoints

#### 1.4.3 Ontology API Endpoints

Для работы с онтологией были реализованы следующие endpoints, приведенные на листинге 9.

```python
@api_view(['GET'])
@permission_classes((AllowAny,))
def get_ontology_parent_classes(request):
    """Получить корневые классы онтологии"""
    try:
        from django.conf import settings
        ontology_repo = OntologyRepository(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE
        )
        
        classes = ontology_repo.get_ontology_parent_classes()
        ontology_repo.close()
        
        # Преобразуем TNode в словари
        classes_data = []
        for cls in classes:
            classes_data.append({
                'id': cls.id,
                'uri': cls.uri,
                'title': cls.title,
                'description': cls.description
            })
        
        return Response(classes_data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes((AllowAny,))
def create_class(request):
    """Создать новый класс"""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Неверный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from django.conf import settings
        ontology_repo = OntologyRepository(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE
        )
        
        cls = ontology_repo.create_class(
            title=data.get('title', ''),
            description=data.get('description', ''),
            parent_uri=data.get('parent_uri')
        )
        ontology_repo.close()
        
        return Response({
            'id': cls.id,
            'uri': cls.uri,
            'title': cls.title,
            'description': cls.description
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

Листинг 9 – Ontology API Endpoints

### 1.5 Настройка Django проекта

#### 1.5.1 Конфигурация settings.py

Для корректной работы системы была настроена конфигурация Django, приведенная на листинге 10.

```python
import os
import dj_database_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'db',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Neo4j configuration
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '123123123')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'corpus')
```

Листинг 10 – Конфигурация settings.py

#### 1.5.2 URL маршрутизация

Для организации API endpoints была настроена маршрутизация, приведенная на листинге 11.

```python
from django.urls import path
from db.views import (
    # Test endpoints
    getTest, postTest, deleteTest,
    
    # Corpus endpoints
    get_corpus, get_corpus_with_texts, get_all_corpora,
    create_corpus, update_corpus, delete_corpus,
    
    # Text endpoints
    get_text, get_texts_by_corpus, get_all_texts,
    create_text, update_text, delete_text,
    
    # Ontology endpoints
    get_ontology, get_ontology_parent_classes, get_class,
    create_class, collect_signature,
)

urlpatterns = [
    # Test endpoints
    path('getTest', getTest, name='getTest'),
    path('postTest', postTest, name='postTest'),
    path('deleteTest', deleteTest, name='deleteTest'),
    
    # Corpus endpoints
    path('corpus/', get_all_corpora, name='get_all_corpora'),
    path('corpus/create/', create_corpus, name='create_corpus'),
    path('corpus/get/', get_corpus, name='get_corpus'),
    path('corpus/get_with_texts/', get_corpus_with_texts, name='get_corpus_with_texts'),
    path('corpus/update/', update_corpus, name='update_corpus'),
    path('corpus/delete/', delete_corpus, name='delete_corpus'),
    
    # Text endpoints
    path('text/', get_all_texts, name='get_all_texts'),
    path('text/create/', create_text, name='create_text'),
    path('text/get/', get_text, name='get_text'),
    path('text/get_by_corpus/', get_texts_by_corpus, name='get_texts_by_corpus'),
    path('text/update/', update_text, name='update_text'),
    path('text/delete/', delete_text, name='delete_text'),
    
    # Ontology endpoints
    path('ontology/', get_ontology, name='get_ontology'),
    path('ontology/parent_classes/', get_ontology_parent_classes, name='get_ontology_parent_classes'),
    path('ontology/class/', get_class, name='get_class'),
    path('ontology/class/create/', create_class, name='create_class'),
    path('ontology/signature/', collect_signature, name='collect_signature'),
]
```

Листинг 11 – URL маршрутизация

#### 1.5.3 Миграции базы данных

Для создания структуры базы данных были выполнены миграции, приведенные на листинге 12.

```bash
python manage.py makemigrations
python manage.py migrate
```

Листинг 12 – Выполнение миграций

### 1.6 Управление сервером

#### 1.6.1 Скрипт запуска сервера

Для корректного запуска сервера был создан скрипт run_server.py, приведенный на листинге 13.

```python
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
```

Листинг 13 – Скрипт запуска сервера

#### 1.6.2 Скрипт остановки сервера

Для корректной остановки сервера был создан скрипт stop_server.py, приведенный на листинге 14.

```python
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
                    print(f'🔄 Завершаем процесс {pid}...')
                    
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
```

Листинг 14 – Скрипт остановки сервера

## 2. Тестирование и валидация

### 2.1 Функциональное тестирование

Было проведено комплексное тестирование всех компонентов системы:

1. **Тестирование моделей данных**: Проверена корректность создания и валидации моделей Corpus и Text
2. **Тестирование репозиториев**: Протестированы все методы CRUD операций
3. **Тестирование API endpoints**: Проверена работа всех REST API endpoints
4. **Тестирование интеграции Neo4j**: Валидирована работа с онтологическими данными
5. **Тестирование управления сервером**: Проверена корректность запуска и остановки

### 2.2 Тестирование на реальных данных

Все компоненты системы были протестированы на данных:

**Созданные корпуса:**
- "Русская литература" (художественная литература)
- "Научные статьи по лингвистике" (научная литература)

**Созданные тексты:**
- "Евгений Онегин" → корпус "Русская литература"
- "Статья о морфологии" → корпус "Научные статьи по лингвистике"

**Созданные классы в онтологии:**
- "Текст"
- "Корпус"
- "Документ" → подкласс "Текста"

### 2.3 Результаты тестирования

Все тесты прошли успешно:

- Создание и управление корпусами
- Создание и управление текстами
- Связи между корпусами и текстами
- Self-reference для переводов
- Интеграция с Neo4j онтологией
- Создание иерархии классов
- Корректный запуск и остановка сервера
- Освобождение портов после завершения

## Заключение

В рамках данного проекта была успешно разработана система хранения и управления корпусом текстов на основе Django с интеграцией Neo4j.

## Список литературы

1. Django Documentation. [Электронный ресурс]. URL: https://docs.djangoproject.com/
2. Django REST Framework Documentation. [Электронный ресурс]. URL: https://www.django-rest-framework.org/
3. Neo4j Python Driver Documentation. [Электронный ресурс]. URL: https://neo4j.com/docs/python-manual/
4. Python-dotenv Documentation. [Электронный ресурс]. URL: https://pypi.org/project/python-dotenv/
5. Django Models Documentation. [Электронный ресурс]. URL: https://docs.djangoproject.com/en/4.2/topics/db/models/
6. Django URL Configuration. [Электронный ресурс]. URL: https://docs.djangoproject.com/en/4.2/topics/http/urls/
7. Django Migrations Documentation. [Электронный ресурс]. URL: https://docs.djangoproject.com/en/4.2/topics/migrations/
8. REST API Design Best Practices. [Электронный ресурс]. URL: https://restfulapi.net/
9. Django Best Practices. [Электронный ресурс]. URL: https://django-best-practices.readthedocs.io/
10. Python Subprocess Documentation. [Электронный ресурс]. URL: https://docs.python.org/3/library/subprocess.html
