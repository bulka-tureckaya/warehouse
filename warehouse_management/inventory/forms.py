from django import forms
from .models import Item, Shelf, JournalEntry, Category

class ItemEntryForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity', 'size', 'category', 'shelf']  # Убедитесь, что shelf включен
        widgets = {
            'shelf': forms.Select(),  # Убедитесь, что это выпадающий список
        }

class ShelfAssignmentForm(forms.Form):
    shelf = forms.ModelChoiceField(queryset=Shelf.objects.all(), empty_label="Выберите стеллаж")

class ItemWithdrawalForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), label="Товар")
    quantity = forms.IntegerField(min_value=1)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['name', 'description', 'capacity', 'max_capacity', 'size_limit']  # Добавляем поле size_limit
