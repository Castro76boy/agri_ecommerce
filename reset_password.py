import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ecommerce.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print('Password reset successfully')
except User.DoesNotExist:
    print('User does not exist')
