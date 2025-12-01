from django.db import models
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ValidationError


class MenuItem(models.Model):
    """
    Модель пункта меню с древовидной структурой.
    Использует self-referencing FK для хранения иерархии.
    """
    menu_name = models.CharField(
        max_length=50,
        verbose_name='Имя меню',
        db_index=True,  # Индекс для быстрой фильтрации по имени меню
        help_text='Идентификатор меню (например: main_menu, footer_menu)'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский пункт'
    )
    url = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='URL',
        help_text='Явный URL (например: /about/)'
    )
    named_url = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Named URL',
        help_text='Имя URL из urls.py (например: about)'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок сортировки (меньше = выше)'
    )

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['menu_name', 'order']),  # Составной индекс для сортировки
        ]

    def __str__(self):
        return f'{self.menu_name}: {self.title}'
    
    def clean(self):
        """Валидация модели перед сохранением"""
        # Защита от циклических ссылок
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError({'parent': 'Пункт не может быть родителем самого себя'})
        
        # Родитель должен быть из того же меню
        if self.parent and self.parent.menu_name != self.menu_name:
            raise ValidationError({
                'parent': 'Родительский пункт должен быть из того же меню'
            })
        
        # URL не обязателен - если не указан, будет '#'
        # (валидация не нужна, это нормальное поведение)
    
    def save(self, *args, **kwargs):
        """Переопределяем save для валидации"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_url(self):
        """
        Возвращает URL пункта меню.
        Приоритет: named_url > url > '#'
        """
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                # Если named_url не найден, возвращаем '#'
                # В production можно добавить логирование
                return '#'
        if self.url:
            return self.url
        return '#'
