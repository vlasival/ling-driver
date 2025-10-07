from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from django.db.models import Q
from .onthology_namespace import *
from .models import Test, Corpus, Text
from core.settings import *

# Web interface views
def dashboard(request):
    """Главная страница с дашбордом"""
    return render(request, 'dashboard.html')

def corpus_list(request):
    """Страница управления корпусами"""
    return render(request, 'corpus_list.html')

def text_list(request):
    """Страница управления текстами"""
    return render(request, 'text_list.html')

def ontology_view(request):
    """Страница управления онтологией"""
    return render(request, 'ontology_view.html')

# API IMPORTS
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

# REPO IMPORTS
from db.api.TestRepository import TestRepository
from db.api.CorpusRepository import CorpusRepository
from db.api.TextRepository import TextRepository
from db.api.ontology_repository import OntologyRepository
from db.api.graph_repository import GraphRepository

@api_view(['GET', ])
@permission_classes((AllowAny,))
def getTest(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=400)
    
    testRepo = TestRepository()
    result = testRepo.getTest(id = id)
    return Response(result)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def postTest(request):
    data = json.loads(request.body.decode('utf-8'))
    testRepo = TestRepository()
    test = testRepo.postTest(test_data = data)
    return JsonResponse(test)

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def deleteTest(request):
    id = request.GET.get('id', None)
    if id is None:
        return HttpResponse(status=400)
    
    testRepo = TestRepository()
    result = testRepo.deleteTest(id = id)
    return Response(result)


# ==================== CORPUS API ENDPOINTS ====================

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


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_corpus_with_texts(request):
    """Получить корпус со всеми текстами"""
    corpus_id = request.GET.get('id', None)
    if corpus_id is None:
        return Response({'error': 'ID корпуса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        corpus_id = int(corpus_id)
    except ValueError:
        return Response({'error': 'Неверный формат ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    corpus_repo = CorpusRepository()
    corpus = corpus_repo.get_corpus_with_texts(corpus_id)
    
    if corpus is None:
        return Response({'error': 'Корпус не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(corpus)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_all_corpora(request):
    """Получить все корпуса"""
    corpus_repo = CorpusRepository()
    corpora = corpus_repo.get_all_corpora()
    return Response(corpora)


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


@api_view(['PUT'])
@permission_classes((AllowAny,))
def update_corpus(request):
    """Обновить корпус"""
    corpus_id = request.GET.get('id', None)
    if corpus_id is None:
        return Response({'error': 'ID корпуса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        corpus_id = int(corpus_id)
        data = json.loads(request.body.decode('utf-8'))
    except (ValueError, json.JSONDecodeError):
        return Response({'error': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)
    
    corpus_repo = CorpusRepository()
    try:
        corpus = corpus_repo.update_corpus(corpus_id, data)
        if corpus is None:
            return Response({'error': 'Корпус не найден'}, status=status.HTTP_404_NOT_FOUND)
        return Response(corpus)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes((AllowAny,))
def delete_corpus(request):
    """Удалить корпус"""
    corpus_id = request.GET.get('id', None)
    if corpus_id is None:
        return Response({'error': 'ID корпуса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        corpus_id = int(corpus_id)
    except ValueError:
        return Response({'error': 'Неверный формат ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    corpus_repo = CorpusRepository()
    success = corpus_repo.delete_corpus(corpus_id)
    
    if not success:
        return Response({'error': 'Корпус не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'message': 'Корпус успешно удален'})


# ==================== TEXT API ENDPOINTS ====================

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


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_texts_by_corpus(request):
    """Получить тексты корпуса"""
    corpus_id = request.GET.get('corpus_id', None)
    if corpus_id is None:
        return Response({'error': 'ID корпуса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        corpus_id = int(corpus_id)
    except ValueError:
        return Response({'error': 'Неверный формат ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    text_repo = TextRepository()
    texts = text_repo.get_texts_by_corpus(corpus_id)
    return Response(texts)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_all_texts(request):
    """Получить все тексты"""
    text_repo = TextRepository()
    texts = text_repo.get_all_texts()
    return Response(texts)


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


@api_view(['PUT'])
@permission_classes((AllowAny,))
def update_text(request):
    """Обновить текст"""
    text_id = request.GET.get('id', None)
    if text_id is None:
        return Response({'error': 'ID текста не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        text_id = int(text_id)
        data = json.loads(request.body.decode('utf-8'))
    except (ValueError, json.JSONDecodeError):
        return Response({'error': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)
    
    text_repo = TextRepository()
    try:
        text = text_repo.update_text(text_id, data)
        if text is None:
            return Response({'error': 'Текст не найден'}, status=status.HTTP_404_NOT_FOUND)
        return Response(text)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes((AllowAny,))
def delete_text(request):
    """Удалить текст"""
    text_id = request.GET.get('id', None)
    if text_id is None:
        return Response({'error': 'ID текста не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        text_id = int(text_id)
    except ValueError:
        return Response({'error': 'Неверный формат ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    text_repo = TextRepository()
    success = text_repo.delete_text(text_id)
    
    if not success:
        return Response({'error': 'Текст не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'message': 'Текст успешно удален'})


# ==================== ONTOLOGY API ENDPOINTS ====================

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


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_class(request):
    """Получить класс по URI"""
    class_uri = request.GET.get('uri', None)
    if class_uri is None:
        return Response({'error': 'URI класса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from django.conf import settings
        ontology_repo = OntologyRepository(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE
        )
        
        cls = ontology_repo.get_class(class_uri)
        ontology_repo.close()
        
        if cls is None:
            return Response({'error': 'Класс не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': cls.id,
            'uri': cls.uri,
            'title': cls.title,
            'description': cls.description
        })
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


@api_view(['GET'])
@permission_classes((AllowAny,))
def collect_signature(request):
    """Собрать signature класса"""
    class_uri = request.GET.get('uri', None)
    if class_uri is None:
        return Response({'error': 'URI класса не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from django.conf import settings
        ontology_repo = OntologyRepository(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE
        )
        
        signature = ontology_repo.collect_signature(class_uri)
        ontology_repo.close()
        
        return Response({
            'params': [
                {'title': param.title, 'uri': param.uri}
                for param in signature.params
            ],
            'obj_params': [
                {
                    'title': obj_param.title,
                    'uri': obj_param.uri,
                    'target_class_uri': obj_param.target_class_uri,
                    'relation_direction': obj_param.relation_direction
                }
                for obj_param in signature.obj_params
            ]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_object(request):
    """Создать новый объект"""
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
        
        obj = ontology_repo.create_object(
            uri=data.get('uri', ''),
            class_uri=data.get('class_uri', '')
        )
        ontology_repo.close()
        
        return Response({
            'id': obj.id,
            'uri': obj.uri
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_object(request):
    """Получить объект по URI"""
    obj_uri = request.GET.get('uri', None)
    if obj_uri is None:
        return Response({'error': 'URI объекта не указан'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from django.conf import settings
        ontology_repo = OntologyRepository(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE
        )
        
        obj = ontology_repo.get_object(obj_uri)
        ontology_repo.close()
        
        if obj:
            return Response({
                'id': obj.id,
                'uri': obj.uri
            })
        else:
            return Response({'error': 'Объект не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_datatype_property(request):
    """Создать новое DatatypeProperty"""
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
        
        prop = ontology_repo.create_datatype_property(
            uri=data.get('uri', ''),
            domain_uri=data.get('domain_uri', ''),
            range_type=data.get('range_type', '')
        )
        ontology_repo.close()
        
        return Response({
            'id': prop.id,
            'uri': prop.uri,
            'domain_uri': prop.domain_uri,
            'range_type': prop.range_type
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_object_property(request):
    """Создать новое ObjectProperty"""
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
        
        prop = ontology_repo.create_object_property(
            uri=data.get('uri', ''),
            domain_uri=data.get('domain_uri', ''),
            range_uri=data.get('range_uri', '')
        )
        ontology_repo.close()
        
        return Response({
            'id': prop.id,
            'uri': prop.uri,
            'domain_uri': prop.domain_uri,
            'range_uri': prop.range_uri
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)