from django.contrib import admin

from .models import Recipe, Tag, Ingredient, IngredientRecipe

class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author') 
    search_fields = ('text',) 
    list_filter = ('pub_date',) 
    empty_value_display = '-пусто-'  

admin.site.register(Recipe, PostAdmin)
admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(Ingredient)

