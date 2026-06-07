from django.urls import path

from blog import views


urlpatterns = [
    path("", views.index, name="index"),
    path("debug", views.debug, name="debug"),
    path("search", views.search, name="search"),
]
