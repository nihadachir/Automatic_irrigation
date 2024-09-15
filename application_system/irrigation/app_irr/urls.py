from django.urls import path
from app_irr import views


urlpatterns=[
    path('',views.home,name="home"),
    path('register',views.register,name='register'),
    path('login',views.logIn,name='login'),
    path('logout',views.logOut,name='logout'),
    path('navbar',views.navbar,name='navbar'),
    path('d', views.d, name='d'),
    path('profile',views.admin,name='profile'),
    path('profile/update',views.admin_update,name='profile_update'),
    path('terrain',views.terrain,name='terrain'),
    path('terre_data',views.terre_data,name='terre_data'),
    path('terre_data/update',views.terrain_update,name='terrain_update'),
    path('show_address_static',views.show_address_static,name='show_address_static'),
    path('statistique_create',views.statistique_create,name='statistique_create'),
    path('statistique',views.statistique,name='statistique'),
    path('statistique_update',views.statistique_update,name='statistique_update'),
    path('statistique_delete',views.statistique_delete,name='statistique_delete'),
     path('prediction',views.prediction,name='prediction'),
 
   
   
    
   





]