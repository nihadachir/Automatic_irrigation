# Generated by Django 4.1.7 on 2023-05-02 19:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_irr', '0021_remove_proprietaire_terrain_prop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proprietaire_terrain',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userprofile', to=settings.AUTH_USER_MODEL),
        ),
    ]
