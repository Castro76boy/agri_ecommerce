from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from django.core.exceptions import ValidationError
import re
from .utils import format_fcfa
from django.utils import timezone
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='categories/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
        
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

    @property
    def has_children(self):
        return self.children.exists()

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_valid(self):
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text='Prix en FCFA')
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=50, default='kg', help_text='Unité de mesure (kg, g, pièce, etc.)')
    minimum_order = models.PositiveIntegerField(default=1, help_text='Quantité minimum par commande')
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
    
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])

    def get_price_fcfa(self):
        if self.promotion and self.promotion.is_valid:
            if self.promotion.discount_type == 'percentage':
                discount = self.price * (self.promotion.discount_value / 100)
                discounted_price = self.price - discount
                return format_fcfa(discounted_price)
            else:  # montant fixe
                discounted_price = self.price - self.promotion.discount_value
                return format_fcfa(max(0, discounted_price))
        return format_fcfa(self.price)

    def get_discount_percentage(self):
        if self.promotion and self.promotion.is_valid:
            if self.promotion.discount_type == 'percentage':
                return self.promotion.discount_value
            else:
                return round((self.promotion.discount_value / self.price) * 100)
        return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', '-created']

    def __str__(self):
        return f"Image de {self.product.name}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        """Calcule le prix total du panier"""
        return sum(item.total_price() for item in self.items.all())

    def get_total_price_fcfa(self):
        """Retourne le prix total en FCFA formaté"""
        return format_fcfa(self.get_total_price())

    def __str__(self):
        return f"Panier de {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def get_total_price_fcfa(self):
        return format_fcfa(self.total_price)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        """Calcule le prix total de l'item"""
        return self.product.price * self.quantity

    def get_total_price_fcfa(self):
        """Retourne le prix total en FCFA formaté"""
        return format_fcfa(self.total_price())

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente de confirmation'),
        ('CONFIRMED', 'Confirmée'),
        ('PREPARING', 'En préparation'),
        ('SHIPPING', 'En cours de livraison'),
        ('DELIVERED', 'Livrée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PAID', 'Payé'),
        ('FAILED', 'Échoué'),
        ('REFUNDED', 'Remboursé'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('ORANGE_MONEY', 'Orange Money'),
        ('MOOV_MONEY', 'Moov Money'),
        ('CASH', 'Paiement à la livraison'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('HOME', 'Livraison à domicile'),
        ('PICKUP', 'Point de retrait'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, default='HOME')
    
    # Informations de livraison
    shipping_name = models.CharField(max_length=100)
    shipping_address = models.CharField(max_length=250)
    shipping_city = models.CharField(max_length=100)
    shipping_region = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Informations de paiement
    payment_reference = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Informations de livraison
    delivery_notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    # Montants
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, help_text='Sous-total en FCFA')
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=0, help_text='Frais de livraison en FCFA')
    discount = models.DecimalField(max_digits=10, decimal_places=0, help_text='Remise en FCFA')
    total = models.DecimalField(max_digits=10, decimal_places=0, help_text='Total en FCFA')

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f'Commande {self.id}'

    def get_total_price_fcfa(self):
        return format_fcfa(self.total)

    def get_absolute_url(self):
        return reverse('store:order_detail', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.total:
            self.total = self.subtotal + self.delivery_fee - self.discount
        super().save(*args, **kwargs)

    def clean_phone(self):
        phone = self.phone
        # Supprimer tous les caractères non numériques
        phone = re.sub(r'\D', '', phone)
        
        # Vérifier que le numéro commence par un format valide pour le Mali
        if not phone.startswith(('223', '7', '2')):
            if phone.startswith('00223'):
                phone = phone[5:]  # Enlever le 00223
            elif phone.startswith('+223'):
                phone = phone[4:]  # Enlever le +223
            else:
                phone = '223' + phone  # Ajouter 223 si nécessaire
        
        # Vérifier la longueur du numéro
        if len(phone) < 8 or len(phone) > 12:
            raise ValidationError('Le numéro de téléphone doit contenir entre 8 et 12 chiffres.')
        
        return phone

    def can_cancel(self):
        return self.status in ['PENDING', 'CONFIRMED'] and self.payment_status != 'REFUNDED'

    def can_modify(self):
        return self.status == 'PENDING'

    @property
    def is_paid(self):
        return self.payment_status == 'PAID'

    def send_confirmation_email(self):
        subject = f'Confirmation de votre commande #{self.id}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = self.email
        
        context = {
            'order': self,
            'items': self.items.all(),
            'site_name': 'BIO Recolte',
        }
        
        html_message = render_to_string('store/emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )

    def send_status_update_email(self):
        subject = f'Mise à jour de votre commande #{self.id}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = self.email
        
        context = {
            'order': self,
            'status': self.get_status_display(),
            'site_name': 'BIO Recolte',
        }
        
        html_message = render_to_string('store/emails/order_status_update.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text='Prix en FCFA')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'

    def get_price_fcfa(self):
        return format_fcfa(self.price)

    def get_total_price(self):
        return self.price * self.quantity

    def get_total_price_fcfa(self):
        return format_fcfa(self.get_total_price())

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        unique_together = ('product', 'user')  # Un utilisateur ne peut laisser qu'un avis par produit

    def __str__(self):
        return f'Avis de {self.user.username} sur {self.product.name}'

class FarmerProfile(models.Model):
    REGION_CHOICES = [
        ('bamako', 'Bamako'),
        ('kayes', 'Kayes'),
        ('koulikoro', 'Koulikoro'),
        ('sikasso', 'Sikasso'),
        ('segou', 'Ségou'),
        ('mopti', 'Mopti'),
        ('tombouctou', 'Tombouctou'),
        ('gao', 'Gao'),
        ('kidal', 'Kidal'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    
    def clean_phone(self):
        phone = self.phone
        # Validation format malien (8 chiffres commençant par 2, 5, 6, 7)
        if not re.match(r'^[2567]\d{7}$', phone):
            raise ValidationError('Le numéro de téléphone doit être un numéro malien valide (8 chiffres commençant par 2, 5, 6 ou 7)')
        return phone

    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='bamako')
    profile_image = models.ImageField(upload_to='farmers/', blank=True, null=True)
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"

    @property
    def total_sales(self):
        return OrderItem.objects.filter(product__farmer=self.user).aggregate(
            total=Sum('price'))['total'] or 0

class CustomerProfile(models.Model):
    REGION_CHOICES = [
        ('bamako', 'Bamako'),
        ('kayes', 'Kayes'),
        ('koulikoro', 'Koulikoro'),
        ('sikasso', 'Sikasso'),
        ('segou', 'Ségou'),
        ('mopti', 'Mopti'),
        ('tombouctou', 'Tombouctou'),
        ('gao', 'Gao'),
        ('kidal', 'Kidal'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def clean_phone(self):
        phone = self.phone
        # Supprime tous les caractères non numériques
        phone = re.sub(r'\D', '', phone)
        
        # Vérifie si le numéro commence par un indicatif valide
        valid_prefixes = ['223', '20', '70', '75', '76', '77', '78', '79', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99']
        if not any(phone.startswith(prefix) for prefix in valid_prefixes):
            raise ValidationError('Numéro de téléphone invalide. Veuillez utiliser un format valide (ex: 223XXXXXXXX ou 7XXXXXXXX)')
        
        # Vérifie la longueur du numéro
        if len(phone) not in [8, 11]:  # 8 chiffres pour le format local, 11 avec l'indicatif pays
            raise ValidationError('Le numéro doit contenir 8 chiffres (format local) ou 11 chiffres (avec indicatif pays)')
        
        return phone

    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='bamako')
    profile_image = models.ImageField(upload_to='customers/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    def get_total_orders(self):
        return self.user.orders.count()

# Signal pour créer automatiquement un profil client
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil client pour chaque nouvel utilisateur"""
    if created:
        CustomerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    """S'assure que le profil est sauvegardé quand l'utilisateur est sauvegardé"""
    if not hasattr(instance, 'customerprofile'):
        CustomerProfile.objects.create(user=instance)
    instance.customerprofile.save()
