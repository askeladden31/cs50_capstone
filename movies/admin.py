from django.contrib import admin

from .models import Movie, Connection, User

# Register your models here.

admin.site.register(User)

class ConnectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['movie1', 'movie2']

class MovieAdmin(admin.ModelAdmin):
    search_fields = ['title', 'year'] 

admin.site.register(Movie, MovieAdmin)
admin.site.register(Connection, ConnectionAdmin)