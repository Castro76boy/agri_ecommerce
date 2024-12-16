from django.test import TestCase
from django.contrib.auth import get_user_model
from store.models import Product, Category

class TestModels(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='Test Description',
            price=99.99,
            category=self.category,
            stock=10
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_product_price(self):
        self.assertEqual(self.product.price, 99.99)

    def test_product_stock(self):
        self.assertEqual(self.product.stock, 10)
