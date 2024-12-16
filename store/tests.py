from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, CustomerProfile
from decimal import Decimal

class StoreTestCase(TestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        
        # Créer une catégorie de test
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Créer un produit de test
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            price=Decimal('10.00'),
            stock=10,
            description='Test description'
        )
        
        # Créer un profil client
        self.profile = CustomerProfile.objects.create(
            user=self.user,
            phone='1234567890',
            address='Test Address'
        )

    def test_product_list_view(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product/list.html')
        self.assertContains(response, 'Test Product')

    def test_product_detail_view(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product/detail.html')
        self.assertContains(response, self.product.name)

    def test_cart_add(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('store:cart_add'),
            {'product_id': self.product.id, 'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)  # Redirection après ajout

    def test_order_create(self):
        self.client.login(username='testuser', password='testpass123')
        # Ajouter un produit au panier d'abord
        self.client.post(
            reverse('store:cart_add'),
            {'product_id': self.product.id, 'quantity': 1}
        )
        # Créer la commande
        response = self.client.post(
            reverse('store:order_create'),
            {
                'address': 'Test Address',
                'phone': '1234567890'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirection après création
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après inscription
        self.assertTrue(User.objects.filter(username='newuser').exists())
