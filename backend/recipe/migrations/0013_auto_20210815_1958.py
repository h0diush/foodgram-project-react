# Generated by Django 3.0.5 on 2021-08-15 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0012_auto_20210815_1951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoplist',
            name='shop_list',
        ),
        migrations.AddField(
            model_name='shoplist',
            name='shop_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shops_list', to='recipe.Recipe', verbose_name='Рецепты'),
        ),
    ]
