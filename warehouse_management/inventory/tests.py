from django.test import TestCase
from .models import Category, Item, Shelf, JournalEntry

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Электроника", description="Электронные товары")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Электроника")

    def test_category_verbose_name(self):
        category = Category.objects.get(id=1)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'Название')

    def test_category_verbose_name_plural(self):
        self.assertEqual(Category._meta.verbose_name_plural, 'Категории')

class ItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Электроника", description="Электронные товары")
        self.shelf = Shelf.objects.create(name="A1", description="Стеллаж A1", capacity=100, max_capacity=200, size_limit="large")
        self.item = Item.objects.create(name="Телефон", description="Смартфон", category=self.category, quantity=10, size="small", shelf=self.shelf)

    def test_item_str(self):
        self.assertEqual(str(self.item), "Телефон")

    def test_item_save_decreases_shelf_capacity(self):
        initial_capacity = self.shelf.capacity
        self.item.save()
        self.shelf.refresh_from_db()
        self.assertEqual(self.shelf.capacity, initial_capacity)

    def test_item_delete_increases_shelf_capacity(self):
        self.item.save()
        self.item.delete()
        self.shelf.refresh_from_db()
        self.assertEqual(self.shelf.capacity, self.shelf.capacity)

    def test_item_delete_if_quantity_zero(self):
        self.item.quantity = 0
        self.item.save()
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(id=self.item.id)

class ShelfModelTest(TestCase):
    def setUp(self):
        self.shelf = Shelf.objects.create(name="A1", description="Стеллаж A1", capacity=100, max_capacity=200, size_limit="large")

    def test_shelf_str(self):
        self.assertEqual(str(self.shelf), "A1 (Текущая: 100, Максимальная: 200, Размер: large)")

    def test_shelf_verbose_name(self):
        shelf = Shelf.objects.get(id=1)
        field_label = shelf._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'Название')

    def test_shelf_verbose_name_plural(self):
        self.assertEqual(Shelf._meta.verbose_name_plural, 'Стеллажи')

class JournalEntryModelTest(TestCase):
    def setUp(self):
        self.journal_entry = JournalEntry.objects.create(item_name="Телефон", quantity=10, operation_type="приход", data="{}")

    def test_journal_entry_str(self):
        self.assertIn(self.journal_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'), str(self.journal_entry))
        self.assertIn("Телефон", str(self.journal_entry))
        self.assertIn("10", str(self.journal_entry))
        self.assertIn("приход", str(self.journal_entry))

    def test_journal_entry_verbose_name(self):
        journal_entry = JournalEntry.objects.get(id=1)
        field_label = journal_entry._meta.get_field('timestamp').verbose_name
        self.assertEqual(field_label, 'timestamp')
