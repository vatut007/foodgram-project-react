# Generated by Django 3.2 on 2022-10-23 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientrecipe',
            name='recipe_ingredient_exists',
        ),
        migrations.RenameField(
            model_name='ingredientrecipe',
            old_name='ingredients',
            new_name='ingredient',
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='recipe_ingredient_exists'),
        ),
    ]
