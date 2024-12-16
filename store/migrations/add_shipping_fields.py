from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', 'manual_add_delivery_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_name',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.CharField(max_length=250, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_city',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_region',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
    ]
