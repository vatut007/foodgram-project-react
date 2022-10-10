from rest_framework import serializers
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from food.models import Recipe, Tag
from users.models import User
from food.models import Ingredient, IngredientRecipe

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name'
        )

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields= (
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
class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True,source='ingridients_recipe' )
    tags = TagsSerializer(read_only=True,many=True)
    class Meta:
        model= Recipe
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