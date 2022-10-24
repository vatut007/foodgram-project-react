from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from food.models import Recipe, Tag
from users.models import User, Follow
from food.models import Ingredient, IngredientRecipe
from djoser.serializers import UserSerializer
from django.contrib.auth.hashers import make_password
import base64
import webcolors


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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


class CreateIngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all())
    
    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )

    def validate_amount(self, value):
        if int(value) < 1:
            raise serializers.ValidationError('Количество должно быть больше 1')
        return value

    def create(self, validated_data):
        return IngredientRecipe.objects.create(
            ingredients=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(
        read_only=True,
        many=True,
        source='ingridients_recipe')
    tags = TagsSerializer(read_only=True, many=True)

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
            'cooking_time'
        )


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
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Есть задублированные ингредиенты!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0!'
            )
        return data
        
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