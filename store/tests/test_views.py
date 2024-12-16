from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Product, Category

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_home_view(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/home.html')

    def test_product_detail_view(self):
        response = self.client.get(
            reverse('store:product_detail', args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_detail.html')

    def test_category_list_view(self):
        response = self.client.get(
            reverse('store:category_list', args=[self.category.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/category.html')
