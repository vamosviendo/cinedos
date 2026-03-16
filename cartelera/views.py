from django.utils import timezone
from django.views.generic import DetailView, ListView

from cartelera.models import Attendance, Showtime


ORDEN_MAP = {
    "fecha": ["datetime"],
    "pelicula": ["movie__title"],
    "cine": ["cinema__name"],
}


class ShowtimeListView(ListView):
    model = Showtime
    context_object_name = "showtimes"

    def get_queryset(self):
        qs = Showtime.objects.filter(
            datetime__gt=timezone.now()
        )

        fecha = self.request.GET.get("fecha")
        if fecha:
            qs = qs.filter(datetime__date=fecha)

        pelicula = self.request.GET.get("pelicula")
        if pelicula:
            qs = qs.filter(movie_id=pelicula)

        cine = self.request.GET.get("cine")
        if cine:
            qs = qs.filter(cinema_id=cine)

        barrio = self.request.GET.get("barrio")
        if barrio:
            qs = qs.filter(cinema__neighborhood=barrio)

        orden = self.request.GET.get("orden")
        if orden in ORDEN_MAP:
            qs = qs.order_by(*ORDEN_MAP[orden])

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_showtimes"] = set(
                Attendance.objects
                    .filter(user=self.request.user)
                    .exclude(status=Attendance.STATUS_CANCELLED)
                    .values_list("showtime_id", flat=True)
            )

        return context


class ShowtimeDetailView(DetailView):
    model = Showtime
    context_object_name = "showtime"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendances"] = Attendance.objects.filter(
            showtime=self.object,
            status=Attendance.STATUS_LOOKING,
        )
        if self.request.user.is_authenticated:
            context["user_attendance"] = Attendance.objects.filter(
                user=self.request.user,
                showtime=self.object,
            ).first()
        return context
