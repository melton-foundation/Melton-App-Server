# Generated by Django 3.0.3 on 2020-07-04 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0013_auto_20200704_1646"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="work",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
