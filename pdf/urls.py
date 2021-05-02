from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name = 'upload'),
    path('merge/', views.merge, name = 'merge'),
    path('split/', views.split, name = 'split'),
    path('delete/', views.delete, name = 'delete'),
]