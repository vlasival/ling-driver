from django.urls import path

from db.views import (
    # Web interface views
    dashboard,
    corpus_list,
    text_list,
    ontology_view,
    
    # Test endpoints
    getTest,
    postTest,
    deleteTest,
    
    # Corpus endpoints
    get_corpus,
    get_corpus_with_texts,
    get_all_corpora,
    create_corpus,
    update_corpus,
    delete_corpus,
    
    # Text endpoints
    get_text,
    get_texts_by_corpus,
    get_all_texts,
    create_text,
    update_text,
    delete_text,
    
    # Ontology endpoints
    get_ontology,
    get_ontology_parent_classes,
    get_class,
    create_class,
    collect_signature,
    create_object,
    get_object,
    create_datatype_property,
    create_object_property,
)

urlpatterns = [
    # Web interface
    path('', dashboard, name='dashboard'),
    path('corpus/', corpus_list, name='corpus_list'),
    path('text/', text_list, name='text_list'),
    path('ontology/', ontology_view, name='ontology_view'),
    
    # API endpoints
    path('api/corpus/', get_all_corpora, name='api_corpus_list'),
    path('api/corpus/create/', create_corpus, name='api_corpus_create'),
    path('api/corpus/get/', get_corpus, name='api_corpus_get'),
    path('api/corpus/get_with_texts/', get_corpus_with_texts, name='api_corpus_get_with_texts'),
    path('api/corpus/update/', update_corpus, name='api_corpus_update'),
    path('api/corpus/delete/', delete_corpus, name='api_corpus_delete'),
    
    path('api/text/', get_all_texts, name='api_text_list'),
    path('api/text/create/', create_text, name='api_text_create'),
    path('api/text/get/', get_text, name='api_text_get'),
    path('api/text/by_corpus/', get_texts_by_corpus, name='api_text_by_corpus'),
    path('api/text/update/', update_text, name='api_text_update'),
    path('api/text/delete/', delete_text, name='api_text_delete'),
    
    path('api/ontology/', get_ontology, name='api_ontology_list'),
    path('api/ontology/parent_classes/', get_ontology_parent_classes, name='api_ontology_parent_classes'),
    path('api/ontology/get_class/', get_class, name='api_ontology_get_class'),
    path('api/ontology/create_class/', create_class, name='api_ontology_create_class'),
    path('api/ontology/collect_signature/', collect_signature, name='api_ontology_collect_signature'),
    path('api/ontology/create_object/', create_object, name='api_ontology_create_object'),
    path('api/ontology/get_object/', get_object, name='api_ontology_get_object'),
    path('api/ontology/create_datatype_property/', create_datatype_property, name='api_ontology_create_datatype_property'),
    path('api/ontology/create_object_property/', create_object_property, name='api_ontology_create_object_property'),
    
    # Test endpoints
    path('getTest', getTest, name='getTest'),
    path('postTest', postTest, name='postTest'),
    path('deleteTest', deleteTest, name='deleteTest'),
]