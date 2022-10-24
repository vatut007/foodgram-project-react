# Generated by Django 3.2 on 2022-10-23 17:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='food.IngredientRecipe', to='food.Ingredient', verbose_name='Ингредиенты в рецепте'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='food.Tag'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingridients_recipe', to='food.ingredient', verbose_name='Ингредиенты рецепта'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingridients_recipe', to='food.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='recipe_ingredient_exists'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.CheckConstraint(check=models.Q(amount__gte=1), name='amount_gte_1'),
        ),
    ]
