import os
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ecommerce.settings')
django.setup()

from django.utils.text import slugify
from store.models import Category, Product
from django.contrib.auth.models import User

def create_category(name):
    category, created = Category.objects.get_or_create(
        name=name,
        slug=slugify(name)
    )
    return category

def create_product(name, category, description, price, stock=100):
    admin_user = User.objects.get(username='admin')
    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            'category': category,
            'slug': slugify(name),
            'description': description,
            'price': price,
            'stock': stock,
            'available': True,
            'farmer': admin_user
        }
    )
    return product

# Créer les catégories
legumes = create_category("Légumes")
fruits = create_category("Fruits")
epices = create_category("Épices et aromates")

# Descriptions détaillées des produits
products_data = [
    # Légumes
    {
        'name': 'Gombo',
        'category': legumes,
        'description': "Gombo frais et tendre, parfait pour les sauces traditionnelles africaines. Riche en fibres et en vitamines, ce légume polyvalent apporte une texture unique à vos plats.",
        'price': Decimal('2.99')
    },
    {
        'name': 'Aubergine',
        'category': legumes,
        'description': "Aubergines fraîches et brillantes, idéales pour les grillades et les plats mijotés. Chair tendre et savoureuse, cultivée localement.",
        'price': Decimal('1.99')
    },
    {
        'name': 'Tomate',
        'category': legumes,
        'description': "Tomates juteuses et charnues, cultivées en plein soleil. Parfaites pour les sauces, salades ou en accompagnement.",
        'price': Decimal('2.49')
    },
    {
        'name': 'Oignon',
        'category': legumes,
        'description': "Oignons frais et croquants, indispensables dans la cuisine africaine. Saveur prononcée qui rehausse tous vos plats.",
        'price': Decimal('1.79')
    },
    {
        'name': 'Piment',
        'category': legumes,
        'description': "Piments frais aux couleurs vives, parfaits pour ajouter une touche de chaleur à vos plats. Cultivés avec soin pour une saveur optimale.",
        'price': Decimal('1.99')
    },
    {
        'name': 'Salade',
        'category': legumes,
        'description': "Salade fraîche et croquante, idéale pour des repas légers et rafraîchissants. Feuilles tendres cultivées sans pesticides.",
        'price': Decimal('1.49')
    },
    {
        'name': 'Concombre',
        'category': legumes,
        'description': "Concombres frais et croquants, parfaits pour les salades. Cultivés naturellement pour une fraîcheur maximale.",
        'price': Decimal('1.29')
    },
    {
        'name': 'Laitue',
        'category': legumes,
        'description': "Laitue fraîche aux feuilles tendres et croquantes. Idéale pour vos salades et sandwichs.",
        'price': Decimal('1.49')
    },
    {
        'name': 'Poivrons',
        'category': legumes,
        'description': "Poivrons colorés et charnus, excellents en cuisine. Riches en vitamine C et antioxydants.",
        'price': Decimal('2.99')
    },
    {
        'name': 'Patate',
        'category': legumes,
        'description': "Patates douces fraîches à la chair tendre et sucrée. Parfaites pour les purées et les frites.",
        'price': Decimal('1.99')
    },
    {
        'name': 'Pomme de terre',
        'category': legumes,
        'description': "Pommes de terre de qualité supérieure, polyvalentes en cuisine. Chair ferme idéale pour tous types de cuisson.",
        'price': Decimal('1.79')
    },

    # Fruits
    {
        'name': 'Mangue',
        'category': fruits,
        'description': "Mangues juteuses et parfumées, cultivées sous le soleil africain. Chair sucrée et fondante, riche en vitamines.",
        'price': Decimal('3.99')
    },
    {
        'name': 'Papaye',
        'category': fruits,
        'description': "Papayes mûres à point, à la chair orange et sucrée. Excellente source de vitamines et d'enzymes digestives.",
        'price': Decimal('3.49')
    },
    {
        'name': 'Banane',
        'category': fruits,
        'description': "Bananes douces et crémeuses, parfaites comme en-cas ou dans vos desserts. Cultivées naturellement.",
        'price': Decimal('2.49')
    },
    {
        'name': 'Orange',
        'category': fruits,
        'description': "Oranges juteuses et sucrées, gorgées de soleil. Riches en vitamine C, idéales pour vos jus frais.",
        'price': Decimal('2.99')
    },
    {
        'name': 'Citron',
        'category': fruits,
        'description': "Citrons frais et parfumés, indispensables en cuisine. Parfaits pour assaisonner vos plats ou préparer des boissons.",
        'price': Decimal('1.99')
    },
    {
        'name': 'Ananas',
        'category': fruits,
        'description': "Ananas juteux et sucrés, à la chair dorée. Parfaits en dessert ou en jus frais.",
        'price': Decimal('3.99')
    },
    {
        'name': 'Goyave',
        'category': fruits,
        'description': "Goyaves fraîches et parfumées, riches en vitamines. Chair sucrée et parfumée, idéale pour les desserts.",
        'price': Decimal('2.99')
    },
    {
        'name': 'Pastèque',
        'category': fruits,
        'description': "Pastèques juteuses et rafraîchissantes, parfaites pour les chaudes journées. Chair rouge vif et pépins croquants.",
        'price': Decimal('4.99')
    },

    # Épices et aromates
    {
        'name': 'Gingembre',
        'category': epices,
        'description': "Gingembre frais et parfumé, aux notes piquantes et citronnées. Indispensable pour la cuisine et les infusions.",
        'price': Decimal('3.99')
    },
    {
        'name': 'Piments',
        'category': epices,
        'description': "Piments séchés d'une qualité exceptionnelle. Ajoutent une chaleur intense et des saveurs complexes à vos plats.",
        'price': Decimal('2.99')
    },
    {
        'name': 'Curcuma',
        'category': epices,
        'description': "Curcuma frais aux propriétés anti-inflammatoires reconnues. Parfait pour la cuisine et les remèdes traditionnels.",
        'price': Decimal('4.99')
    },
    {
        'name': 'Basilic',
        'category': epices,
        'description': "Basilic frais au parfum intense, cultivé localement. Rehausse vos plats d'une note aromatique unique.",
        'price': Decimal('1.99')
    },
    {
        'name': 'Poivre',
        'category': epices,
        'description': "Poivre noir de qualité supérieure, aux notes chaudes et piquantes. Indispensable dans toute cuisine.",
        'price': Decimal('3.99')
    },
    {
        'name': 'Cannelle',
        'category': epices,
        'description': "Bâtons de cannelle de Ceylan, au parfum doux et complexe. Parfaite pour les desserts et les boissons chaudes.",
        'price': Decimal('4.99')
    },
    {
        'name': 'Néré',
        'category': epices,
        'description': "Graines de Néré traditionnelles pour la préparation du soumbala. Un ingrédient essentiel de la cuisine africaine.",
        'price': Decimal('5.99')
    },
    {
        'name': 'Clou de girofle',
        'category': epices,
        'description': "Clous de girofle entiers au parfum intense. Indispensables pour les marinades et les plats épicés.",
        'price': Decimal('3.99')
    },
    {
        'name': 'Menthe',
        'category': epices,
        'description': "Menthe fraîche et parfumée, idéale pour le thé et la cuisine. Feuilles tendres au goût rafraîchissant.",
        'price': Decimal('1.99')
    },
    {
        'name': 'Coriandre',
        'category': epices,
        'description': "Coriandre fraîche aux feuilles délicates et parfumées. Apporte une touche de fraîcheur à tous vos plats.",
        'price': Decimal('1.99')
    },
]

# Créer tous les produits
for product_data in products_data:
    product = create_product(
        name=product_data['name'],
        category=product_data['category'],
        description=product_data['description'],
        price=product_data['price'],
        stock=random.randint(50, 200)
    )
    print(f"Produit créé : {product.name}")

print("Tous les produits ont été créés avec succès !")
