from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetail.as_view(), name='product-detail'),
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetail.as_view(), name='category-detail'),
]
