from django.urls import include, path
from rest_framework import routers


from .views import (IngredientViewSet, RecipeViewSet, CustomUserViewSet, TagsViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet)
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
