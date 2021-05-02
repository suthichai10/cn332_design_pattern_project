from django.urls import path
from . import views
from pdf import views as pdf_views
urlpatterns = [
    path('' , pdf_views.index , name = "index"),
    path('about/' , views.about, name = 'about'),
    path('download/<str:file_id>/<path:file_name>/<str:mimeType>', pdf_views.download , name ='download'),
    path('profile/history/' , views.history , name = 'history'),
    path('register/' , views.register , name = "register"),
    path('logout/' , views.logout_view , name = "logout"),
    path('login/' , views.login_view , name = "login"),

]