from csv import DictReader
from os.path import exists
from django.core.management import BaseCommand
from food.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = 'static/data/ingredients.csv'
        if exists(csv_file):
            for row in DictReader(open(csv_file, encoding='utf-8')):
                Ingredient.objects.create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                    )
        else:
            print(
                'Файл Ingredient.csv для заполнения '
                f'{Ingredient.__name__} отсутвует.'
                )
        print(f'{Ingredient.__name__}: новые объекты добавлены.')
