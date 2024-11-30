from django.urls import reverse
from django.conf import settings
from django.db.models import Q, Count

from math import sin, cos, radians
from random import randint

from .models import Connection, User, Movie

graph_height = settings.GRAPH_HEIGHT
graph_width = settings.GRAPH_WIDTH

def get_top_connected_movies(movie, connected_ids):
    
    movie_is_movie2 = Q(conn1__movie2=movie)
    movie_is_movie1 = Q(conn2__movie1=movie)
    
    movies = Movie.objects.filter(id__in=connected_ids).annotate(count=Count(movie_is_movie2)+Count(movie_is_movie1))
    
    # movies = Movie.objects.filter(movie_is_movie2 | movie_is_movie1).annotate(count=Count(movie_is_movie2)+Count(movie_is_movie1))
    
    return movies

def get_connections_and_ids(movie):
    
    connections_where_movie_is_movie1 = movie.conn1.all().select_related("movie2")
    movie2_ids = connections_where_movie_is_movie1.values_list('movie2', flat=True)
    
    connections_where_movie_is_movie2 = movie.conn2.all().select_related("movie1")
    movie1_ids = connections_where_movie_is_movie2.values_list('movie1', flat=True)
    
    connected_ids = movie1_ids.union(movie2_ids)
    
    connections = connections_where_movie_is_movie1 | connections_where_movie_is_movie2
    
    return connections, connected_ids

def left_menu(user):
    left_menu = []
    
    if user.is_authenticated:
        left_menu.append(("Messages", reverse("index")))
        left_menu.append(("Want to watch", reverse("want_to_watch_list", args=[user.id])))
        left_menu.append(("Watched", reverse("watched_list", args=[user.id])))
    else:
        left_menu.append(("Login", reverse("login")))
        left_menu.append(("Register", reverse("register")))

    return left_menu

def right_menu(user, movie_id):
    right_menu = []

    right_menu.append(("Go to general page", reverse("movie", args=[movie_id])))

    if user.is_authenticated:
        connections1 = Connection.objects.filter(added_by=user).filter(movie1=movie_id)
        connections2 = Connection.objects.filter(added_by=user).filter(movie2=movie_id)
        if connections1.exists() or connections2.exists():
            right_menu.append(("Go to my page", reverse("user_movie", args=[movie_id, user.id])))

    return right_menu

def get_watchlists(user):
    # user = request.user

    watched = [*user.watched.all().values_list('id', flat=True)]
    wanna_watch = [*user.want_to_watch.all().values_list('id', flat=True)]

    return {
            "watched": watched,
            "wanna_watch": wanna_watch
        }

def has_connections(movies, user):
    return_dict = {}

    for m in movies:
        has_connections = False
        if m.conn1.all().filter(added_by = user).exists() or m.conn2.all().filter(added_by = user).exists():
            has_connections = True
        return_dict[m] = has_connections

    return return_dict

def calculate_coordinates(nodes):

    if len(nodes)<=1:
        return nodes

    x = nodes[0]["x"]
    y = nodes[0]["y"]

    older = 0
    newer = 0
    max_o = 0

    for n in nodes[1:]:
        o = n["offset"]
        if abs(o) > max_o:
            max_o = abs(o)
        if o < 0:
            older += 1
        else:
            newer += 1

    delta_theta1 = theta1 = 180 / (older + 1)
    delta_theta2 = theta2 = 180 / (newer + 1)
    
    norm_factor = (graph_height - 50) / 2 / max_o

    for n in nodes[1:]:
        o = n["offset"]
        if o >= 0:
            n["x"] = x + norm_factor*abs(o)*cos(radians(180 + theta2)) + randint(-10,10)
            n["y"] = y + norm_factor*abs(o)*sin(radians(180 + theta2)) + randint(-10,10)
            theta2 += delta_theta2
        else:
            n["x"] = x + norm_factor*abs(o)*cos(radians(theta1)) + randint(-10,10)
            n["y"] = y + norm_factor*abs(o)*sin(radians(theta1)) + randint(-10,10)
            theta1 += delta_theta1

    return nodes
