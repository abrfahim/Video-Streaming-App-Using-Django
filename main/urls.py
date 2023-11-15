from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('video/<int:video_id>/', views.watch_video, name='watch_video'),
    path('video/add_comment/', views.add_comment, name='add_comment'),
    path('video/add_like/<int:video_id>/', views.add_like, name='add_like'),
    path('<str:session_username>/profile/', views.profile, name='profile'),
    path('<str:session_username>/dashboard/', views.dashboard, name='dashboard'),
    path('add_subscriber/<viewer>/', views.add_sub, name='add_subscriber'),
    path('upload/', views.upload_video, name='upload'),
    path('edit_video/<int:video_id>', views.edit_video, name='edit_video'),
    path('delete_video/', views.delete_video, name='delete_video'),
    path('update_details/', views.update_details, name='update_details'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('search/', views.search, name='search'),
]
