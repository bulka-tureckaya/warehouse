from django.urls import path
from .views import (
    home,
    item_list,
    category_list,
    shelf_list,
    search_items,
    add_item,
    withdraw_item,
    account_view,
    add_category,
    manage_shelves, 
    delete_shelf, 
    journal_list,
)

urlpatterns = [
    path('', home, name='home'),
    path('items/', item_list, name='item_list'),
    path('categories/', category_list, name='category_list'),
    path('shelves/', shelf_list, name='shelf_list'),
    path('search/', search_items, name='search_items'),
    path('add-item/', add_item, name='add_item'),
    path('withdraw-item/', withdraw_item, name='withdraw_item'),
    path('add-category/', add_category, name='add_category'),
    path('manage-shelves/', manage_shelves, name='manage_shelves'),
    path('delete-shelf/<int:shelf_id>/', delete_shelf, name='delete_shelf'),
    path('account/', account_view, name='account'),
    path('journal/', journal_list, name='journal_list'),
    
]