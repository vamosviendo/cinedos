from django.urls import path

from cartelera.views import (
    AttendanceCancelView,
    AttendanceCreateView,
    ShowtimeDetailView,
    ShowtimeListView
)

app_name = "cartelera"

urlpatterns = [
    path("funciones/", ShowtimeListView.as_view(), name="showtime-list"),
    path("funciones/<int:pk>/", ShowtimeDetailView.as_view(), name="showtime-detail"),
    path("funciones/<int:pk>/apuntarse/", AttendanceCreateView.as_view(), name="attendance-create"),
    path("asistencias/<int:pk>/cancelar/", AttendanceCancelView.as_view(), name="attendance-cancel"),
]