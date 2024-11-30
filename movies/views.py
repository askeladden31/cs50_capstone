# import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.db.models import Exists, OuterRef

from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Movie, Connection, User
from .views_ajax import *

# Create your views here.

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "movies/login.html", {
                "message": "Invalid username and/or password.",
                "left_menu": left_menu(request.user)
            })
    else:
        return render(request, "movies/login.html", {
            "left_menu": left_menu(request.user)
        })

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "movies/register.html", {
                "message": "Passwords must match.",
                "left_menu": left_menu(request.user)
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "movies/register.html", {
                "message": "Username already taken.",
                "left_menu": left_menu(request.user)
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "movies/register.html", {
            "left_menu": left_menu(request.user)
        }) 

def index(request):
    return render(request, "movies/layout.html", {
        "graph_height": graph_height,
        "graph_width": graph_width,
        "left_menu": left_menu(request.user)
    })

def movie_graph(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    return render(request, "movies/movie.html", {
        "movie": movie,
        "left_menu": left_menu(request.user),
        "fetch_url": reverse('movie_graph', args=[movie.id]),
        # should move these to the graph view:
        "graph_height": graph_height,
        "graph_width": graph_width,
    })

def user_movie(request, movie_id, user_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    user = get_object_or_404(User, pk=user_id)

    return render(request, "movies/user_movie.html", {
        "user": user,
        "movie": movie,
        "left_menu": left_menu(request.user),
        "fetch_url": reverse('user_movie_graph', args=[movie_id, user_id]),
        # "right_menu": right_menu(request.user, movie),
        # should move these to the graph view:
        "graph_height": graph_height,
        "graph_width": graph_width
    }) 

@login_required
def add_connection(request):
    if request.method != "POST":
        return HttpResponse("POST request required.", status=400)

    movie1_id = request.POST['movie1']
    movie2_id = request.POST['movie2']
    user = request.user
    description = request.POST['conn_dsc']

    Connection.objects.create(movie1_id=movie1_id, movie2_id=movie2_id, added_by=user, description=description)

    return HttpResponseRedirect(reverse("user_movie", args=[movie1, user.id]))    

@login_required
def remove_connection(request, connection_id):
    if request.method != "DELETE":
        return HttpResponse("DELETE request required.", status=405)
        
    conn = get_object_or_404(Connection, pk=connection_id)
    conn.delete()
    
    return HttpResponse(status=204)
    

def watched_list(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    movies = user.watched.all() # .annotate(in_graph=Exists())

    res = []

    for m in movies:
        in_graph = False
        if m.conn1.all().filter(added_by = user).exists() or m.conn2.all().filter(added_by = user).exists():
            in_graph = True
        res.append((m, in_graph))

    return render(request, "movies/watched_list.html", {
        "user": user,
        "movies": res,
        "left_menu": left_menu(request.user)
    })

@login_required    
def watched_remove(request, movie_id):

    user = request.user    
    movie = get_object_or_404(user.watched, pk=movie_id)
    user.watched.remove(movie)
    res = user.watched.all()
 
    return redirect("watched_list", user.id)
     
def want_to_watch_remove(request, movie_id):

    user = request.user    
    movie = get_object_or_404(user.wanna_watch, pk=movie_id)
    user.wanna_watch.remove(movie)
    res = user.wanna_watch.all()
 
    return redirect('want2watch_list', user.id)

def want_to_watch_list(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    movies = user.want_to_watch.all()

    res = [] # [movie, in_graph]

    for m in movies:
        in_graph = False
        if m.conn1.all().filter(added_by = user).exists() or m.conn2.all().filter(added_by = user).exists():
            in_graph = True
        res.append((m, in_graph))

    return render(request, "movies/want_to_watch_list.html", {
        "user": user,
        "movies": res,
        "left_menu": left_menu(request.user)
    })
