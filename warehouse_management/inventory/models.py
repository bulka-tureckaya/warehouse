from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import json

class BaseModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(verbose_name=_("Описание"))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name  # Возвращаем название для всех моделей, наследующих BaseModel

class Category(BaseModel):
    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

class Item(BaseModel):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    SIZE_CHOICES = [
        (SMALL, 'Маленький'),
        (MEDIUM, 'Средний'),
        (LARGE, 'Большой'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name=_("Категория"))
    quantity = models.PositiveIntegerField(verbose_name=_("Количество"))
    size = models.CharField(max_length=6, choices=SIZE_CHOICES, default=SMALL, verbose_name=_("Размер"))
    shelf = models.ForeignKey('Shelf', on_delete=models.SET_NULL, related_name='items', verbose_name=_("Стеллаж"), null=True)

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.delete()
            return
        
        if self.pk is None:  # Проверяем, является ли это новым объектом
            if self.shelf:
                self.shelf.capacity -= self.quantity  # Уменьшаем вместимость стеллажа
                self.shelf.save()  # Сохраняем изменения в стеллаже

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # При удалении товара увеличиваем вместимость стеллажа
        if self.shelf:
            self.shelf.capacity += self.quantity  # Увеличиваем вместимость стеллажа
            self.shelf.save()  # Сохраняем изменения в стеллаже
            
        super().delete(*args, **kwargs)

class Shelf(BaseModel):
    capacity = models.PositiveIntegerField(verbose_name=_("Текущая вместимость"))
    max_capacity = models.PositiveIntegerField(verbose_name=_("Максимальная вместимость"))
    size_limit = models.CharField(max_length=6, choices=Item.SIZE_CHOICES, default=Item.SMALL, verbose_name=_("Размер стеллажа"))

    class Meta:
        verbose_name = _("Стеллаж")
        verbose_name_plural = _("Стеллажи")

    def __str__(self):
        return f"{self.name} (Текущая: {self.capacity}, Максимальная: {self.max_capacity}, Размер: {self.size_limit})"

class JournalEntry(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    item_name = models.CharField(max_length=255, null=True, blank=True)  # Разрешите NULL и пустые значения
    quantity = models.IntegerField(null=True, blank=True)  # Разрешите NULL и пустые значения
    operation_type = models.CharField(max_length=10, choices=[('приход', 'приход'), ('уход', 'уход')], default='приход') 
    data = models.TextField()  # Хранение данных в виде строки

    def __str__(self):
        return f"{self.timestamp} - {self.item_name} - {self.quantity} - {self.operation_type}"
