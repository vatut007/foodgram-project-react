import webcolors
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from food.models import (Cart, Favorite, Ingredient, IngredientRecipe, Recipe,
                         Tag)
from users.models import Follow, User
from .fields import Base64ImageField


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagsSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()


class CustomRegUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
    validate_password = make_password


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
        )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit'
        )


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "is_favorited",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_in_shopping_cart",
        )

    @staticmethod
    def get_ingredients(obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data


class CreateIngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше 1'
                )
        return value

    def create(self, validated_data):
        return Ingredient.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        read_only=True,
        many=True,
        source='ingridients_recipe')
    tags = TagsSerializer(read_only=True, many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'pub_date',
            'tags',
            'cooking_time',
            'is_in_shopping_cart',
            'is_favorited'
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            recipe=obj, user=request.user
        ).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient.get('id'),
            ) for ingredient in ingredients
        ])

    def validate(self, ingredients_):
        if not ingredients_['ingredients'] or not ingredients_['tags']:
            raise ValidationError(
                'Добавьте ингредиенты и укажите тег для рецепта!'
            )
        ingredients = ingredients_['ingredients']
        min_ingredients = 2
        if len(ingredients) < min_ingredients:
            raise ValidationError(
                'Ингредиентов должно быть два или больше!'
            )
        data = []
        for ingredient in ingredients:
            data.append(ingredient['id'])
            if ingredient['amount'] <= 0:
                ingredient_incorrect = ingredient['id']
                raise ValidationError(
                    f'ЕИ - ингредиента "{ingredient_incorrect}" не'
                    'должна быть равна нулю или отрицательным числом!'
                )
        check_unique = set(data)
        if len(check_unique) != len(data):
            raise ValidationError(
                'Ингредиенты повторяются, объедините их или выберите другие!'
            )
        if ingredients_['cooking_time'] <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше нуля!'
            )
        return ingredients_

    def create(self, validate_data):
        request = self.context.get('request')
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validate_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'user',
            'author'
        )

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'errors': 'Ты не пожешь подписаться на себя.'
            })
        if Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
        ):
            raise ValidationError({
                'errors': 'Уже подписан.'
            })
        return data


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowListSerializer(serializers.ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortInfoSerializer(
                Recipe.objects.filter(author=author),
                many=True, context={'request': queryset}
            ).data
        return RecipeShortInfoSerializer(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={'request': queryset}
        ).data

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError({
                'errors': 'Уже есть в избранном.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfoSerializer(
            instance.recipe, context=context).data


class CartSerializer(ModelSerializer):
    class Meta:
        fields = ['recipe', 'user']
        model = Cart

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if Cart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Данный рецепт уже есть в корзине.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfoSerializer(instance.recipe, context=context).data
