from django.urls import path

from .views import ShowtimeListView

app_name = "cartelera"

urlpatterns = [
    path("funciones/", ShowtimeListView.as_view(), name="showtime-list"),
]