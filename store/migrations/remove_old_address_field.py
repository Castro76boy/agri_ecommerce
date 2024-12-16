from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('store', 'add_order_amounts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='address',
        ),
    ]
