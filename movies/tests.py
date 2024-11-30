from django.test import TestCase
from django.core.management import call_command
from django.db.models import Count

from movies.models import Movie

# Create your tests here.

class TestCommand(TestCase):
    def test_mycommand(self):
        " Test my custom command."

        args = ['test_data.tsv',]
        opts = {}
        call_command('load_csv', *args, **opts)
        
        
        duplicates = (
            Movie.objects.values('title','year','imdb_id')
            .annotate(title_count=Count('title'),year_count=Count('year'),id_count=('imdb_id'))
            .filter(title_count__gt=1, year_count__gt=1, id_count__gt=1)
        )
        
        print(duplicates)
        
        self.assertEqual(len(duplicates), 0)
        
        args = ['test_data2.tsv',]
        call_command('load_csv', *args, **opts)
        
        duplicates = (
            Movie.objects.values('title','year','imdb_id')
            .annotate(title_count=Count('title'),year_count=Count('year'))
            .filter(title_count__gt=1, year_count__gt=1)
        )
        
        print(duplicates)

        self.assertEqual(len(duplicates), 0)
        
        for row in Movie.objects.all():
            print(row.pk)