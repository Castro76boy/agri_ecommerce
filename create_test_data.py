import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ecommerce.settings')
django.setup()

from store.models import Category, Product
from django.contrib.auth.models import User

def create_test_data():
    # Créer les catégories
    categories = [
        {'name': 'Fruits', 'slug': 'fruits'},
        {'name': 'Légumes', 'slug': 'legumes'},
        {'name': 'Produits laitiers', 'slug': 'produits-laitiers'},
        {'name': 'Viandes', 'slug': 'viandes'},
    ]
    
    for cat_data in categories:
        Category.objects.get_or_create(**cat_data)
    
    # Créer un agriculteur de test
    farmer, _ = User.objects.get_or_create(
        username='farmer1',
        defaults={
            'email': 'farmer1@example.com',
            'is_staff': True
        }
    )
    farmer.set_password('farmer123')
    farmer.save()
    
    # Créer des produits
    products = [
        {
            'category': 'fruits',
            'name': 'Pommes Bio',
            'slug': 'pommes-bio',
            'description': 'Pommes biologiques fraîchement cueillies',
            'price': Decimal('1800'),
            'stock': 100
        },
        {
            'category': 'legumes',
            'name': 'Carottes',
            'slug': 'carottes',
            'description': 'Carottes fraîches de saison',
            'price': Decimal('1200'),
            'stock': 150
        },
        {
            'category': 'produits-laitiers',
            'name': 'Fromage de chèvre',
            'slug': 'fromage-de-chevre',
            'description': 'Fromage de chèvre artisanal',
            'price': Decimal('3000'),
            'stock': 50
        },
        {
            'category': 'viandes',
            'name': 'Poulet fermier',
            'slug': 'poulet-fermier',
            'description': 'Poulet élevé en plein air',
            'price': Decimal('7500'),
            'stock': 30
        },
    ]
    
    for prod_data in products:
        category = Category.objects.get(slug=prod_data['category'])
        Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'category': category,
                'slug': prod_data['slug'],
                'description': prod_data['description'],
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'farmer': farmer
            }
        )

if __name__ == '__main__':
    create_test_data()
    print('Données de test créées avec succès')
