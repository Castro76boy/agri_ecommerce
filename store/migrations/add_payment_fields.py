from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', 'add_contact_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_reference',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_delivery',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
