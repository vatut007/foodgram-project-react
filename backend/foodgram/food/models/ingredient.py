from django.db import models

class Ingredient(models.Model):
    '''Модель ингредиента.'''
    name= models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        db_index=True)
    measurement_unit= models.CharField (
        max_length=200,
        verbose_name='Единица измерения')
    
    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


