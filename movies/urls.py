from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/', views.movie_graph, name='movie'),
    path('<int:movie_id>/<int:user_id>', views.user_movie, name='user_movie'),
    path('graph/<int:movie_id>/<int:user_id>', views.user_movie_graph, name='user_movie_graph'),
    path('graph/<int:movie_id>', views.movie_graph, name='movie_graph'),
    path('search', views.search, name='search'),
    path('add', views.add_connection, name='add_connection'),
    path('remove/<int:connection_id>', views.remove_connection, name='remove_connection'),
    
    path('want_to_watch', views.want_to_watch, name='want_to_watch'),
    path('watched/<int:movie_id>', views.watched, name='watched'),
    
    path('watched_list/<int:user_id>', views.watched_list, name="watched_list"),
    path('want_to_watch_list/<int:user_id>', views.want_to_watch_list, name="want_to_watch_list"),
    path('logout', views.logout_view, name='logout'),
    path('login', views.login_view, name='login'),
    path('register', views.register, name='register'),
    path('right_menu_api/<int:movie_id>', views.right_menu_api, name='right_menu_api'),
    
    path('watched_list/remove/<int:movie_id>', views.watched_remove, name="watched_remove"),
    path('want_to_watch_list/remove/<int:movie_id>', views.want_to_watch_remove, name="want_to_watch_remove"),
]
