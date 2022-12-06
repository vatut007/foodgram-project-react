from django.core.validators import MinValueValidator
from django.db import models

from users.models import User
from .ingredient import Ingredient
from .tag import Tag


class Recipe (models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(
        'Картинка',
        upload_to='recipe/',
        blank=True
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты в рецепте'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин.'
    )

    def __str__(self):
        return self.text


class IngredientRecipe(models.Model):
    """Ингредиент в рецепте"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиента')

    class Meta:
        default_related_name = 'ingridients_recipe'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='recipe_ingredient_exists'),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'),
        )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} – {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorites',
            ),
        )


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Корзина рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_cart',
            ),
        )
