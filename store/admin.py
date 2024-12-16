from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.utils import timezone
from .models import (
    Category, Product, Order, OrderItem,
    FarmerProfile, CustomerProfile, Tag, Promotion
)
from .utils import format_fcfa

# Désactiver l'administration des groupes
from django.contrib.auth.models import Group
admin.site.unregister(Group)

# Personnaliser l'interface d'administration
admin.site.site_header = 'Administration BIO Recolte'
admin.site.site_title = 'BIO Recolte'
admin.site.index_title = 'Tableau de bord'

class ProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name = 'Profil Client'
    verbose_name_plural = 'Profil Client'

class FarmerProfileInline(admin.StackedInline):
    model = FarmerProfile
    can_delete = False
    verbose_name = 'Profil Agriculteur'
    verbose_name_plural = 'Profil Agriculteur'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_date_joined', 'last_login')
    list_filter = ('is_staff', 'date_joined', 'last_login', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [ProfileInline, FarmerProfileInline]
    
    def get_date_joined(self, obj):
        return timezone.localtime(obj.date_joined).strftime("%d/%m/%Y %H:%M")
    get_date_joined.short_description = "Date d'inscription"
    get_date_joined.admin_order_field = 'date_joined'

# Réenregistrer l'admin User avec notre version personnalisée
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def get_list_display(self, request):
        return ['name', 'parent']

    def name(self, obj):
        return obj.name
    name.short_description = 'Nom'

    def parent(self, obj):
        return obj.parent if obj.parent else '-'
    parent.short_description = 'Catégorie parente'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'get_price_fcfa', 'get_total_fcfa']
    readonly_fields = ['get_price_fcfa', 'get_total_fcfa']
    
    def get_price_fcfa(self, obj):
        if obj.price:
            return format_fcfa(obj.price)
        return '-'
    get_price_fcfa.short_description = 'Prix (FCFA)'

    def get_total_fcfa(self, obj):
        if obj.price and obj.quantity:
            total = obj.price * obj.quantity
            return format_fcfa(total)
        return '-'
    get_total_fcfa.short_description = 'Total (FCFA)'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'get_price_fcfa', 'stock', 'available', 'farmer', 'get_orders_count']
    list_filter = ['available', 'category', 'created', 'updated']
    list_editable = ['stock', 'available']
    search_fields = ['name', 'farmer__username', 'description']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['category', 'farmer']
    actions = ['make_available', 'make_unavailable']
    
    def get_price_fcfa(self, obj):
        return format_fcfa(obj.price)
    get_price_fcfa.short_description = 'Prix (FCFA)'
    
    def get_orders_count(self, obj):
        return obj.orderitem_set.count()
    get_orders_count.short_description = 'Nombre de commandes'
    
    def make_available(self, request, queryset):
        queryset.update(available=True)
    make_available.short_description = "Marquer les produits comme disponibles"
    
    def make_unavailable(self, request, queryset):
        queryset.update(available=False)
    make_unavailable.short_description = "Marquer les produits comme indisponibles"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'farmer')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'shipping_name', 'status', 'payment_status', 'get_total_fcfa', 'get_created', 'get_items_count']
    list_filter = ['status', 'payment_status', 'created', 'updated']
    search_fields = ['shipping_name', 'email', 'phone', 'shipping_address']
    readonly_fields = ['created', 'updated', 'get_total_fcfa']
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_delivered']
    ordering = ['-created']
    
    def get_created(self, obj):
        return timezone.localtime(obj.created).strftime("%d/%m/%Y %H:%M")
    get_created.short_description = "Date de création"
    get_created.admin_order_field = 'created'
    
    def get_total_fcfa(self, obj):
        return format_fcfa(obj.total)
    get_total_fcfa.short_description = 'Total (FCFA)'
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = "Nombre d'articles"
    
    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='paid')
    mark_as_paid.short_description = "Marquer comme payé"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Marquer comme livré"
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        translations = {
            'name': 'Nom'
        }
        return [translations.get(x, x) for x in list_display]

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'discount_value', 'active']
    list_filter = ['active']
    search_fields = ['name']
    list_editable = ['active']
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        translations = {
            'name': 'Nom',
            'discount_type': 'Type de remise',
            'discount_value': 'Valeur de remise',
            'active': 'Actif'
        }
        return [translations.get(x, x) for x in list_display]

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'region']
    list_filter = ['region']
    search_fields = ['user__username', 'phone']
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        translations = {
            'user': 'Utilisateur',
            'phone': 'Téléphone',
            'region': 'Région'
        }
        return [translations.get(x, x) for x in list_display]

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'region']
    list_filter = ['region']
    search_fields = ['user__username', 'phone']
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        translations = {
            'user': 'Utilisateur',
            'phone': 'Téléphone',
            'region': 'Région'
        }
        return [translations.get(x, x) for x in list_display]
