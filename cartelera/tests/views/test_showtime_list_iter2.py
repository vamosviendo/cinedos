"""
Tests — Iteración 2: filtros de ShowtimeListView
Qué verificamos:
  1. ?fecha=      filtra por fecha exacta
  2. ?pelicula=   filtra por id de película
  3. ?cine=       filtra por id de cine
  4. ?barrio=     filtra por barrio del cine
  5. Filtros combinados se aplican con AND
"""
from django.urls import reverse
from django.utils import timezone

from cartelera.tests.factories import CinemaFactory, MovieFactory, ShowtimeFactory


def test_filtro_por_fecha(client):
    """Solo aparecen funciones del día solicitado."""
    hoy = timezone.localdate()
    manana = hoy + timezone.timedelta(days=1)
    pasado = hoy + timezone.timedelta(days=2)

    funcion_manana = ShowtimeFactory(
        datetime=timezone.make_aware(
            timezone.datetime.combine(manana, timezone.datetime.min.time().replace(hour=20))
        )
    )
    funcion_pasado = ShowtimeFactory(
        datetime=timezone.make_aware(
            timezone.datetime.combine(pasado, timezone.datetime.min.time().replace(hour=20))
        )
    )

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"fecha": manana.isoformat()})

    showtimes = list(response.context["showtimes"])
    assert funcion_manana in showtimes
    assert funcion_pasado not in showtimes


def test_filtro_por_pelicula(client):
    """Solo aparecen funciones de la película solicitada."""
    pelicula_a = MovieFactory()
    pelicula_b = MovieFactory()
    funcion_a = ShowtimeFactory(movie=pelicula_a)
    funcion_b = ShowtimeFactory(movie=pelicula_b)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"pelicula": pelicula_a.id})

    showtimes = list(response.context["showtimes"])
    assert funcion_a in showtimes
    assert funcion_b not in showtimes


def test_filtro_por_cine(client):
    """Solo aparecen funciones del cine solicitado."""
    cine_a = CinemaFactory()
    cine_b = CinemaFactory()
    funcion_a = ShowtimeFactory(cinema=cine_a)
    funcion_b = ShowtimeFactory(cinema=cine_b)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"cine": cine_a.id})

    showtimes = list(response.context["showtimes"])
    assert funcion_a in showtimes
    assert funcion_b not in showtimes


def test_filtro_por_barrio(client):
    """Solo aparecen funciones de cines del barrio solicitado."""
    cine_palermo = CinemaFactory(neighborhood="Palermo")
    cine_belgrano = CinemaFactory(neighborhood="Belgrano")
    funcion_palermo = ShowtimeFactory(cinema=cine_palermo)
    funcion_belgrano = ShowtimeFactory(cinema=cine_belgrano)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"barrio": "Palermo"})

    showtimes = list(response.context["showtimes"])
    assert funcion_palermo in showtimes
    assert funcion_belgrano not in showtimes


def test_filtros_combinados(client):
    """Fecha + película se aplican juntos (AND)."""
    hoy = timezone.localdate()
    manana = hoy + timezone.timedelta(days=1)
    pasado = hoy + timezone.timedelta(days=2)

    pelicula_a = MovieFactory()
    pelicula_b = MovieFactory()

    # La que tiene que aparecer: película A, mañana
    funcion_correcta = ShowtimeFactory(
        movie=pelicula_a,
        datetime=timezone.make_aware(
            timezone.datetime.combine(manana, timezone.datetime.min.time().replace(hour=20))
        ),
    )
    # Misma película, otro día
    funcion_otro_dia = ShowtimeFactory(
        movie=pelicula_a,
        datetime=timezone.make_aware(
            timezone.datetime.combine(pasado, timezone.datetime.min.time().replace(hour=20))
        ),
    )
    # Mismo día, otra película
    funcion_otra_pelicula = ShowtimeFactory(
        movie=pelicula_b,
        datetime=timezone.make_aware(
            timezone.datetime.combine(manana, timezone.datetime.min.time().replace(hour=20))
        ),
    )

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"fecha": manana.isoformat(), "pelicula": pelicula_a.id})

    showtimes = list(response.context["showtimes"])
    assert funcion_correcta in showtimes
    assert funcion_otro_dia not in showtimes
    assert funcion_otra_pelicula not in showtimes
