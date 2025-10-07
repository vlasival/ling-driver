from db.models import Text, Corpus
from typing import List, Dict, Any, Optional


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

    def get_text(self, text_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить текст по ID
        
        Args:
            text_id: ID текста
            
        Returns:
            Словарь с данными текста или None
        """
        try:
            text = Text.objects.get(pk=text_id)
            return self.collect_text(text)
        except Text.DoesNotExist:
            return None

    def get_texts_by_corpus(self, corpus_id: int) -> List[Dict[str, Any]]:
        """
        Получить все тексты корпуса
        
        Args:
            corpus_id: ID корпуса
            
        Returns:
            Список словарей с данными текстов
        """
        try:
            corpus = Corpus.objects.get(pk=corpus_id)
            texts = corpus.texts.all()
            return [self.collect_text(text) for text in texts]
        except Corpus.DoesNotExist:
            return []

    def get_all_texts(self) -> List[Dict[str, Any]]:
        """
        Получить все тексты
        
        Returns:
            Список словарей с данными текстов
        """
        texts = Text.objects.all()
        return [self.collect_text(text) for text in texts]

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

    def update_text(self, text_id: int, text_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Обновить текст
        
        Args:
            text_id: ID текста
            text_data: Новые данные текста
            
        Returns:
            Словарь с обновленными данными текста или None
        """
        try:
            text = Text.objects.get(pk=text_id)
            text.name = text_data.get('name', text.name)
            text.description = text_data.get('description', text.description)
            text.text = text_data.get('text', text.text)
            
            # Обновляем корпус если указан
            corpus_id = text_data.get('corpus_id')
            if corpus_id:
                try:
                    corpus = Corpus.objects.get(pk=corpus_id)
                    text.corpus = corpus
                except Corpus.DoesNotExist:
                    raise ValueError(f"Корпус с ID {corpus_id} не найден")
            
            # Обновляем перевод если указан
            translation_id = text_data.get('has_translation_id')
            if translation_id is not None:  # Может быть None для удаления связи
                if translation_id:
                    try:
                        translation = Text.objects.get(pk=translation_id)
                        text.has_translation = translation
                    except Text.DoesNotExist:
                        raise ValueError(f"Текст-перевод с ID {translation_id} не найден")
                else:
                    text.has_translation = None
            
            text.save()
            return self.collect_text(text)
        except Text.DoesNotExist:
            return None

    def delete_text(self, text_id: int) -> bool:
        """
        Удалить текст
        
        Args:
            text_id: ID текста
            
        Returns:
            True если текст удален, False если не найден
        """
        try:
            text = Text.objects.get(pk=text_id)
            text.delete()
            return True
        except Text.DoesNotExist:
            return False

    def search_texts(self, query: str, corpus_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Поиск текстов по содержимому
        
        Args:
            query: Поисковый запрос
            corpus_id: ID корпуса для ограничения поиска (опционально)
            
        Returns:
            Список найденных текстов
        """
        from django.db.models import Q
        
        texts = Text.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(text__icontains=query)
        )
        
        if corpus_id:
            texts = texts.filter(corpus_id=corpus_id)
        
        return [self.collect_text(text) for text in texts]

    def get_texts_with_translations(self) -> List[Dict[str, Any]]:
        """
        Получить тексты с переводами
        
        Returns:
            Список текстов с информацией о переводах
        """
        texts = Text.objects.filter(has_translation__isnull=False)
        return [self.collect_text(text) for text in texts]

    def get_texts_without_translations(self) -> List[Dict[str, Any]]:
        """
        Получить тексты без переводов
        
        Returns:
            Список текстов без переводов
        """
        texts = Text.objects.filter(has_translation__isnull=True)
        return [self.collect_text(text) for text in texts]
