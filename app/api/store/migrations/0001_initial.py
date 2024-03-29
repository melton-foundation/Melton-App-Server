# Generated by Django 3.0.3 on 2020-05-02 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StoreItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(max_length=500)),
                ("points", models.PositiveIntegerField(blank=False)),
                ("active", models.BooleanField(default=True)),
            ],
        ),
    ]
