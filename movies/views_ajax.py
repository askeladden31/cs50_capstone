import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q, Count, Case, When, F, Subquery

from .models import Connection, Movie
from .functions import *

graph_height = settings.GRAPH_HEIGHT
graph_width = settings.GRAPH_WIDTH

default_x = graph_height / 2
default_y = graph_height / 2

def push_node(nodes, movie, links=None, offset=None, user_id=None, request_user=None, connection_id=None, connection_description=None):

    movie_id = movie.id
    
    print(connection_id);
    
    nodes.append(
        {
            "id": movie_id,
            "name": str(movie),
            "x": default_x,
            "y": default_y,
            "offset": offset,
            
            "movie_url": reverse('movie', args=[movie_id,]),
            "user_movie_url": reverse('user_movie_graph', args=[movie_id, user_id]) if user_id else None,
            "request_user_movie_url": reverse('user_movie_graph', args=[movie_id, request_user.id]) if request_user else None,
            
            "watched_url": reverse('watched', args=[movie_id,]),
            "want_to_watch_url": reverse('want_to_watch'),
            "remove_url": reverse('remove_connection', args=[connection_id,]) if connection_id else None,
            
            "want_to_watch": request_user.want_to_watch.filter(pk=movie_id).exists() if request_user else None,            
            "watched": request_user.watched.filter(pk=movie_id).exists() if request_user else None,
            # these may be changed to annotated values
            
            "connection_id": connection_id,
            "connection_description": connection_description,
            # these must be either annotated or sent as params
        }
    )
        
    if offset:
        links.append(dict(
            [
                ("source", 0),
                ("target", len(nodes)-1),
            ]
        ))

def generate_nodes_and_links(movie, movies, connections, user=None, request_user=None):
    '''Generates objects for d3'''

    year = movie.year
    
    nodes = [
        {
            "id": movie.id,
            "name": str(movie),
            "year": year,
            "x": graph_height / 2,
            "y": graph_width / 2,
            "movie_url": reverse('movie', args=[movie.id,]),
            "user_movie_url": reverse('user_movie', args=[movie.id, user.id]) if user else None,
            "request_user_movie_url": reverse('user_movie', args=[movie.id, request_user.id]) if request_user else None,
            "want_to_watch": request_user.want_to_watch.filter(pk=movie_id).exists() if request_user else None,
            "want_to_watch_url": reverse('want_to_watch'),
            "watched": request_user.watched.filter(pk=movie_id).exists() if request_user else None,
            "watched_url": reverse('watched', args=[movie.id,]),
            # "": args=[movie.id]
        },
    ]

    links = []
   
    for movie in movies[:10]:
        nodes.append(dict(
            [
                ("id", movie.id),
                ("name", str(movie)),
                ("movie_url", reverse('movie', args=[movie.id,])),
                ("offset", year - movie.year),
            ]
        ))
        links.append(dict(
            [
                ("source", 0),
                ("target", len(nodes)-1),
            ]
        ))
   

def movie_graph(request, movie_id):
    '''Returns the json representation of the movie's most popular connections'''
    
    movie = get_object_or_404(Movie, pk=movie_id)
    
    _, connected_ids = get_connections_and_ids(movie)
    
    movies = get_top_connected_movies(movie, connected_ids)
      
    year = movie.year
    request_user = request.user if request.user.is_authenticated else None
    
    nodes = []
    
    push_node(nodes, movie, 
        request_user = request_user)
    
    links = []
    
    for m in movies:
        push_node(nodes, m, 
            links = links, 
            offset = year - m.year, 
            request_user = request_user)
            
    nodes = calculate_coordinates(nodes)

    return JsonResponse({"nodes": nodes, "links": links}, safe=False)

def user_movie_graph(request, movie_id, user_id):
    '''Returns the json representation of the movie's connections graph'''

    movie = get_object_or_404(Movie, pk=movie_id)

    connections, _ = get_connections_and_ids(movie)
    
    year = movie.year
    request_user = request.user if request.user.is_authenticated else None
    
    nodes = []
    
    push_node(nodes, movie,
        user_id = user_id,
        request_user = request_user)
    
    links = []
    
    for c in connections.filter(added_by=user_id):
    
        m = c.movie1 if c.movie2==movie else c.movie2
    
        push_node(nodes, m,
            links = links,
            offset = year - m.year,
            user_id = user_id,
            request_user = request_user,
            connection_id = c.id,
            connection_description = c.description,
        )
    
    calculate_coordinates(nodes)

    return JsonResponse({"nodes": nodes, "links": links}, safe=False)

def search(request):

    q = request.GET.get('q')
    terms = q.split()
            
    year = 0
    last_term = terms[-1]
    
    # if last term is numeric and 4-digit, assume it's the year of release, unless it's the only term
    if len(terms)>1 and last_term.isnumeric() and len(last_term) == 4:
        year = last_term
        terms.remove(last_term)
    
    # reassemble the title query with the year removed
    q = ' '.join(terms)

    # first order of relevancy is 'exact match'
    exact_match = Q(title__iexact=q)
    
    # second order of relevancy is 'starts with'
    # starts_with = Q(title__istartswith=terms[0])
    starts_with = Q(title__istartswith=q)
    
    # third order of relevancy is 'contains terms'
    contains = Q()
    for t in terms:
        contains &= Q(title__icontains=t)
    
    year_match = Q()
    if year!=0:
        # year match is a priority modifier
        year_match = Q(year=year)
        # could also be part of the title
        # contains &= Q(title__icontains=year)
        # doesn't work with 'terminator 1984'
        
    movies = Movie.objects.filter((exact_match & year_match) | (starts_with & year_match) | contains).annotate(
        priority=Case(
            When(year_match & exact_match, then=1),
            When(year_match & starts_with, then=2),
            When(year_match & contains, then=3),
            # When(starts_with & contains, then=4),
            When(contains, then=5),
            default=99
        )
    ).order_by('priority')
        
    res = [movie.serialize() for movie in movies]

    return JsonResponse(res[:15], safe=False)

@login_required
def want_to_watch(request):
    if request.method != "POST":
        return HttpResponse("POST request required.", status=400)  

    data = json.loads(request.body)

    id = data['id']
    wannaw = data['status']
    user = request.user
    movie = get_object_or_404(Movie, pk=id)

    if wannaw:
        movie.want_to_watch.remove(user)
    else:
        movie.want_to_watch.add(user)

    return JsonResponse({
            "status": user.want_to_watch.filter(pk=movie.id).exists(),
        }, status=200) 

@login_required
def watched(request, movie_id, redirect=None):
    if request.method != "POST":
        return HttpResponse("POST request required.", status=400)  

    data = json.loads(request.body)
    print(data)

    id = movie_id
    watched = bool(data['status'])
    user = request.user
    movie = get_object_or_404(Movie, pk=id)

    if watched:
        movie.watched.remove(user)
        print('removing')
    else:
        print('adding')
        movie.watched.add(user)
        movie.want_to_watch.remove(user)

    return JsonResponse({
            "status": user.watched.filter(pk=movie.id).exists(),
        }, status=200)

def right_menu_api(request, movie_id):
    r_menu = right_menu(request.user, movie_id)
    watchlists = {}
    wannawatch = watched = False
    if request.user.is_authenticated:
        watchlists = get_watchlists(request.user)
        wannawatch = movie_id in watchlists['wanna_watch']
        watched = movie_id in watchlists['watched']

    return JsonResponse(
        {
            "right_menu": r_menu,
            "watchlists": watchlists,
            "watched": watched,
            "wannawatch": wannawatch,
            "watched_url": reverse("watched", args=[movie_id]),
            "wannawatch_url": reverse("want_to_watch"),
        }, status=200
    )