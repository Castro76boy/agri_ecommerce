"""
URL configuration for agri_ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from store.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
    path('api/', include('store.api.urls')),
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='store/account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='store:product_list'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
