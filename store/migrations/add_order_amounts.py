from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', 'add_payment_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='subtotal',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
            preserve_default=False,
        ),
    ]
