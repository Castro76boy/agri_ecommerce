from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0009_promotion_tag_category_description_category_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'En attente de confirmation'),
                    ('CONFIRMED', 'Confirmée'),
                    ('PREPARING', 'En préparation'),
                    ('SHIPPING', 'En cours de livraison'),
                    ('DELIVERED', 'Livrée'),
                    ('CANCELLED', 'Annulée'),
                ],
                default='PENDING',
                max_length=20
            ),
        ),
    ]
