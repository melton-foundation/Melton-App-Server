# Generated by Django 3.0.7 on 2020-09-23 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeitem',
            name='preview_image',
            field=models.ImageField(blank=True, upload_to='store-items'),
        ),
    ]
