from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import CustomerProfile

class Command(BaseCommand):
    help = 'Crée des profils clients pour les utilisateurs qui n\'en ont pas'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(customerprofile__isnull=True)
        created_count = 0

        for user in users_without_profile:
            CustomerProfile.objects.create(user=user)
            created_count += 1
            self.stdout.write(f'Profil créé pour {user.username}')

        self.stdout.write(
            self.style.SUCCESS(
                f'{created_count} profil(s) client(s) créé(s) avec succès!'
            )
        )
