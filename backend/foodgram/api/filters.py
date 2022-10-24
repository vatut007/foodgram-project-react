from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (AllValuesMultipleFilter,
                                                   BooleanFilter)
from rest_framework.filters import SearchFilter

from food.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilterSet(FilterSet):
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')