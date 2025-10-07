from django.db import models
from django.core.validators import MinLengthValidator


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


class Test(models.Model):
    """Тестовая модель для совместимости"""
    name = models.TextField()

    def __str__(self):
        return self.name