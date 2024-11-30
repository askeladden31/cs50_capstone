from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

class Connection(models.Model):
    movie1 = models.ForeignKey("Movie", on_delete=models.PROTECT, related_name="conn1") 
    movie2 = models.ForeignKey("Movie", on_delete=models.PROTECT, related_name="conn2") 
    added_by = models.ForeignKey("User", on_delete=models.CASCADE) 
    description = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.movie1} <-> {self.movie2}"

class Movie(models.Model):
    title = models.CharField(max_length=128, db_index=True)
    year = models.IntegerField(db_index=True)
    imdb_id = models.CharField(max_length=16)
    want_to_watch = models.ManyToManyField("User", blank=True, related_name="want_to_watch") 
    watched = models.ManyToManyField("User", blank=True, related_name="watched") 
    tracking = models.ManyToManyField("User", blank=True, related_name="tracking")

    def __str__(self):
        if self.year != 0:
            return f"{self.title} ({self.year})"
        else:
            return self.title

    def serialize(self):
        return {
            "id": self.id,
            "title": f"{str(self)} [{self.imdb_id}]" 
        } 
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'year', 'imdb_id'], name='unique_movie')
        ]

