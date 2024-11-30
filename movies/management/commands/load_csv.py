import csv
from django.core.management import BaseCommand
from django.utils import timezone

from movies.models import Movie


class Command(BaseCommand):
    help = "Loads movies from imdb TSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        with open(file_path, "r", encoding="utf8") as tsv_file:
            data = csv.reader(tsv_file, delimiter="\t")
            next(data)  # skip the column names
            movies = []
            total = 0
            exclude = ["video", "tvEpisode", "tvSeries", "tvMiniSeries", "tvSpecial", "tvShort", "videoGame"]

            for row in data:
                if len(row)<6: 
                    continue
                    
                titleType = row[1]
                if titleType in exclude:
                    continue

                movie = Movie(
                    year=row[5].replace(r"\N", "0"),
                    title=row[2],
                    imdb_id=row[0]
                )
                movies.append(movie)

                buffer = len(movies)

                if buffer >= 500000:
                    Movie.objects.bulk_create(movies, ignore_conflicts=True)
                    total += buffer
                    print(f'Created {buffer} entries. A total of {total} entries')
                    movies = []
            if movies:
                Movie.objects.bulk_create(movies, ignore_conflicts=True)
                print(f'Created {len(movies)} entries. A total of {total} entries')
                
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )