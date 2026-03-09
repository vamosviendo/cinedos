from django.utils import timezone
from django.views.generic import ListView

from cartelera.models import Showtime


class ShowtimeListView(ListView):
    model = Showtime
    context_object_name = "showtimes"

    def get_queryset(self):
        return Showtime.objects.filter(
            datetime__gt=timezone.now()
        )