from django.core.management.base import BaseCommand
from store.models import Product, Order, OrderItem
from store.utils import convert_to_fcfa
from decimal import Decimal

class Command(BaseCommand):
    help = 'Convertit tous les prix de EUR en FCFA'

    def handle(self, *args, **kwargs):
        # Conversion des prix des produits
        products = Product.objects.all()
        self.stdout.write('Conversion des prix des produits...')
        for product in products:
            old_price = product.price
            product.price = convert_to_fcfa(old_price)
            product.save()
            self.stdout.write(f'Produit {product.name}: {old_price} EUR -> {product.price} FCFA')

        # Conversion des prix des commandes
        orders = Order.objects.all()
        self.stdout.write('\nConversion des prix des commandes...')
        for order in orders:
            # Conversion du total
            old_total = order.total
            order.total = convert_to_fcfa(old_total)
            
            # Conversion des autres montants
            order.subtotal = convert_to_fcfa(order.subtotal)
            order.delivery_fee = convert_to_fcfa(order.delivery_fee)
            order.discount = convert_to_fcfa(order.discount)
            
            order.save()
            self.stdout.write(f'Commande #{order.id}: {old_total} EUR -> {order.total} FCFA')

        # Conversion des prix des éléments de commande
        order_items = OrderItem.objects.all()
        self.stdout.write('\nConversion des prix des éléments de commande...')
        for item in order_items:
            old_price = item.price
            item.price = convert_to_fcfa(old_price)
            item.save()
            self.stdout.write(f'Élément de commande #{item.id}: {old_price} EUR -> {item.price} FCFA')

        self.stdout.write(self.style.SUCCESS('\nConversion terminée avec succès!'))
