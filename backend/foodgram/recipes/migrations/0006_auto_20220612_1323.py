# Generated by Django 2.2.19 on 2022-06-12 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20220605_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=100, verbose_name='название рецепта'),
        ),
    ]
