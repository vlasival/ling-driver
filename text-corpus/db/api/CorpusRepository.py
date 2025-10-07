from db.models import Corpus, Text
from typing import List, Dict, Any, Optional


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

    def get_corpus(self, corpus_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить корпус по ID
        
        Args:
            corpus_id: ID корпуса
            
        Returns:
            Словарь с данными корпуса или None
        """
        try:
            corpus = Corpus.objects.get(pk=corpus_id)
            return self.collect_corpus(corpus)
        except Corpus.DoesNotExist:
            return None

    def get_corpus_with_texts(self, corpus_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить корпус со всеми текстами по ID
        
        Args:
            corpus_id: ID корпуса
            
        Returns:
            Словарь с данными корпуса и текстами или None
        """
        try:
            corpus = Corpus.objects.get(pk=corpus_id)
            return self.collect_corpus_with_texts(corpus)
        except Corpus.DoesNotExist:
            return None

    def get_all_corpora(self) -> List[Dict[str, Any]]:
        """
        Получить все корпуса
        
        Returns:
            Список словарей с данными корпусов
        """
        corpora = Corpus.objects.all()
        return [self.collect_corpus(corpus) for corpus in corpora]

    def create_corpus(self, corpus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новый корпус
        
        Args:
            corpus_data: Данные корпуса
            
        Returns:
            Словарь с данными созданного корпуса
        """
        corpus = Corpus()
        corpus.name = corpus_data.get('name', '')
        corpus.description = corpus_data.get('description', '')
        corpus.genre = corpus_data.get('genre', '')
        corpus.save()
        return self.collect_corpus(corpus)

    def update_corpus(self, corpus_id: int, corpus_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Обновить корпус
        
        Args:
            corpus_id: ID корпуса
            corpus_data: Новые данные корпуса
            
        Returns:
            Словарь с обновленными данными корпуса или None
        """
        try:
            corpus = Corpus.objects.get(pk=corpus_id)
            corpus.name = corpus_data.get('name', corpus.name)
            corpus.description = corpus_data.get('description', corpus.description)
            corpus.genre = corpus_data.get('genre', corpus.genre)
            corpus.save()
            return self.collect_corpus(corpus)
        except Corpus.DoesNotExist:
            return None

    def delete_corpus(self, corpus_id: int) -> bool:
        """
        Удалить корпус
        
        Args:
            corpus_id: ID корпуса
            
        Returns:
            True если корпус удален, False если не найден
        """
        try:
            corpus = Corpus.objects.get(pk=corpus_id)
            corpus.delete()
            return True
        except Corpus.DoesNotExist:
            return False

    def search_corpora(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск корпусов по названию и описанию
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Список найденных корпусов
        """
        from django.db.models import Q
        
        corpora = Corpus.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(genre__icontains=query)
        )
        return [self.collect_corpus(corpus) for corpus in corpora]
