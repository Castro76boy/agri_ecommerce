from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0010_add_order_status'),  # Mise à jour avec la dernière migration
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(
                choices=[('HOME', 'Livraison à domicile'), ('PICKUP', 'Point de retrait')],
                default='HOME',
                max_length=20
            ),
        ),
    ]
