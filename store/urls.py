from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

app_name = 'store'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Pages légales
    path('terms/', TemplateView.as_view(template_name='store/legal/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='store/legal/privacy.html'), name='privacy'),
    
    # Authentification et compte utilisateur
    path('accounts/login/', auth_views.LoginView.as_view(template_name='store/account/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='store:home'), name='logout'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Produits et catégories
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Panier et commandes
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Avis et évaluations
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # Espace vendeur
    path('become-farmer/', views.become_farmer, name='become_farmer'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
]
