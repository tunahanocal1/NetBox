from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search, name='search'),
    path('book/<str:olid>/', views.book_detail, name='book_detail'),
    path('my-books/<str:status_type>/', views.user_book_list, name='user_book_list'),
    path('toggle-status/<str:olid>/', views.toggle_book_status, name='toggle_book_status'),
]
