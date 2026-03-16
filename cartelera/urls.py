from django.urls import path

from cartelera.views import ShowtimeDetailView, ShowtimeListView

app_name = "cartelera"

urlpatterns = [
    path("funciones/", ShowtimeListView.as_view(), name="showtime-list"),
    path("funciones/<int:pk>/", ShowtimeDetailView.as_view(), name="showtime-detail"),
]