from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Item, Category, Shelf, JournalEntry
from .forms import ItemEntryForm, ItemWithdrawalForm, CategoryForm, ShelfForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages


def account_view(request):
    user = request.user  # Получаем текущего пользователя

    return render(request, 'inventory/account.html', {
        'user': user,
    })

def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

def shelf_list(request):
    shelves = Shelf.objects.all()
    return render(request, 'inventory/shelf_list.html', {'shelves': shelves})

def search_items(request):
    query = request.GET.get('q')
    items = Item.objects.filter(
        name__icontains=query,
        shelf__isnull=False,
        category__isnull=False
    ) if query else []
    return render(request, 'inventory/search_results.html', {'items': items})

def home(request):
    return render(request, 'inventory/home.html')

def journal_list(request):
    entries = JournalEntry.objects.all().order_by('-timestamp')
    return render(request, 'inventory/journal_list.html', {'entries': entries})

def add_item(request):
    if request.method == 'POST':
        item_form = ItemEntryForm(request.POST)
        shelf_id = request.POST.get('shelf')  # Получаем ID выбранного стеллажа

        if item_form.is_valid():
            item = item_form.save(commit=False)

            # Проверяем соответствие размера стеллажа и товара
            if shelf_id:
                shelf = get_object_or_404(Shelf, id=shelf_id)

                # Проверяем, соответствует ли размер товара размеру стеллажа
                if item.size != shelf.size_limit:
                    return render(request, 'inventory/add_item.html', {
                        'item_form': item_form,
                        'shelves': Shelf.objects.all().order_by('-capacity'),  # Сортируем стеллажи
                        'error': "Размер товара не соответствует размеру стеллажа."  # Передаем ошибку в шаблон
                    })

                # Проверяем доступное место на стеллаже
                if item.quantity > shelf.capacity:
                    return render(request, 'inventory/add_item.html', {
                        'item_form': item_form,
                        'shelves': Shelf.objects.all().order_by('-capacity'),  # Сортируем стеллажи
                        'error': "Недостаточно места на выбранном стеллаже."  # Передаем ошибку в шаблон
                    })

                # Сохраняем товар и обновляем вместимость стеллажа
                shelf.capacity -= item.quantity
                shelf.save()

            item.save()
            JournalEntry.objects.create(
                item_name=item.name,
                quantity=item.quantity,
                operation_type='приход',
                data=f"Товар {item.name} добавлен на стеллаж {shelf.name}"
            )
            return redirect('home')

    else:
        item_form = ItemEntryForm()

    shelves = Shelf.objects.all().order_by('-capacity')  # Получаем все стеллажи для выбора и сортируем их

    return render(request, 'inventory/add_item.html', {
        'item_form': item_form,
        'shelves': shelves,
    })

def withdraw_item(request):
    if request.method == 'POST':
        form = ItemWithdrawalForm(request.POST)

        if form.is_valid():
            item = form.cleaned_data['item']
            quantity = form.cleaned_data['quantity']

            if quantity <= item.quantity:
                # Уменьшаем количество товара
                item.quantity -= quantity

                JournalEntry.objects.create(
                    item_name=item.name,
                    quantity=quantity,
                    operation_type='уход',
                    data=f"Товар {item.name} выдан со склада"
                )

                # Сохраняем изменения в количестве товара
                if item.quantity == 0:
                    item.delete()  # Удаляем товар из базы данных, если его количество стало 0
                else:
                    item.save()  # Сохраняем изменения в количестве товара

                return redirect('home')  # Перенаправляем на главную страницу после успешной выдачи

            else:
                return render(request, 'inventory/withdraw_item.html', {
                    'form': form,
                    'error': "Недостаточно товара на складе."
                })

    else:
        form = ItemWithdrawalForm()

    return render(request, 'inventory/withdraw_item.html', {
        'form': form,
    })

def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('item_list')  # Перенаправляем на список товаров или другую страницу после успешного добавления 
    else:
        category_form = CategoryForm()

    return render(request, 'inventory/add_category.html', {
        'category_form': category_form,
    })

def manage_shelves(request):
    if request.method == 'POST':
        shelf_form = ShelfForm(request.POST)
        if shelf_form.is_valid():
            shelf_form.save()
            return redirect('manage_shelves')  # Перенаправляем на ту же страницу после успешного добавления

    else:
        shelf_form = ShelfForm()

    shelves = Shelf.objects.all()  # Получаем все стеллажи для отображения

    return render(request, 'inventory/manage_shelves.html', {
        'shelf_form': shelf_form,
        'shelves': shelves,
    })

def delete_shelf(request, shelf_id):
    shelf = get_object_or_404(Shelf, id=shelf_id)
    shelf.delete()  # Удаляем стеллаж
    return redirect('manage_shelves')  # Перенаправляем на страницу управления стеллажами