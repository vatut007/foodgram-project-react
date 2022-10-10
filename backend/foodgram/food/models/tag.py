from django.db import models

class Tag (models.Model):
    '''Модель Тег.'''
    name= models.CharField(max_length=200)
    color = models.CharField(max_length=16)
    slug = models.SlugField(unique=True)

    def __str__(self): 
        return self.name 
