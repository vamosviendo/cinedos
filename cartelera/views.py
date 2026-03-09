from django.utils import timezone
from django.views.generic import ListView

from cartelera.models import Showtime


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

        return qs
