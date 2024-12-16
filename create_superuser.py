import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ecommerce.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError

try:
    superuser = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('Superuser created successfully')
except IntegrityError:
    print('Superuser already exists')
