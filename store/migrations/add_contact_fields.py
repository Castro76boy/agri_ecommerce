from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', 'add_shipping_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(max_length=254, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(max_length=20, default=''),
            preserve_default=False,
        ),
    ]
