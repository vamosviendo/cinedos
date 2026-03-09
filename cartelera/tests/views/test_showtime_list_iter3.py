"""
Tests — Iteración 3: orden configurable de ShowtimeListView
Qué verificamos:
  1. Sin ?orden= respeta el orden del modelo (datetime, cinema, screen)
  2. ?orden=fecha     ordena por datetime ascendente
  3. ?orden=pelicula  ordena por título de película ascendente
  4. ?orden=cine      ordena por nombre de cine ascendente
  5. Un valor inválido en ?orden= cae al orden por defecto
"""
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from cartelera.tests.factories import CinemaFactory, MovieFactory, ShowtimeFactory


def test_orden_por_defecto(client):
    """Sin ?orden= el resultado respeta el ordering del modelo."""
    manana = timezone.now() + timedelta(days=1)
    pasado = timezone.now() + timedelta(days=2)

    cine_a = CinemaFactory(name="Atlas")
    cine_z = CinemaFactory(name="Zurich")

    # Misma fecha, distinto cine — el modelo ordena por cinema después de datetime
    s1 = ShowtimeFactory(datetime=manana, cinema=cine_a)
    s2 = ShowtimeFactory(datetime=manana, cinema=cine_z)
    s3 = ShowtimeFactory(datetime=pasado, cinema=cine_a)

    url = reverse("cartelera:showtime-list")
    response = client.get(url)

    showtimes = list(response.context["showtimes"])
    assert showtimes.index(s1) < showtimes.index(s2)
    assert showtimes.index(s2) < showtimes.index(s3)


def test_orden_por_fecha(client):
    """?orden=fecha ordena por datetime ascendente."""
    manana = timezone.now() + timedelta(days=1)
    pasado = timezone.now() + timedelta(days=2)

    s_tarde = ShowtimeFactory(datetime=pasado)
    s_temprano = ShowtimeFactory(datetime=manana)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"orden": "fecha"})

    showtimes = list(response.context["showtimes"])
    assert showtimes.index(s_temprano) < showtimes.index(s_tarde)


def test_orden_por_pelicula(client):
    """?orden=pelicula ordena por título ascendente."""
    pelicula_a = MovieFactory(title="Amelie")
    pelicula_z = MovieFactory(title="Zama")

    s_z = ShowtimeFactory(movie=pelicula_z)
    s_a = ShowtimeFactory(movie=pelicula_a)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"orden": "pelicula"})

    showtimes = list(response.context["showtimes"])
    assert showtimes.index(s_a) < showtimes.index(s_z)


def test_orden_por_cine(client):
    """?orden=cine ordena por nombre de cine ascendente."""
    manana = timezone.now() + timedelta(days=1)
    pasado = timezone.now() + timedelta(days=2)

    cine_a = CinemaFactory(name="Atlas")
    cine_z = CinemaFactory(name="Zurich")

    s_z = ShowtimeFactory(datetime=manana, cinema=cine_z)
    s_a = ShowtimeFactory(datetime=pasado, cinema=cine_a)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"orden": "cine"})

    showtimes = list(response.context["showtimes"])
    assert showtimes.index(s_a) < showtimes.index(s_z)


def test_orden_invalido_cae_a_defecto(client):
    """Un valor desconocido en ?orden= no rompe la view y usa el orden por defecto."""
    manana = timezone.now() + timedelta(days=1)
    pasado = timezone.now() + timedelta(days=2)

    cine_a = CinemaFactory(name="Atlas")
    s1 = ShowtimeFactory(datetime=manana, cinema=cine_a)
    s2 = ShowtimeFactory(datetime=pasado, cinema=cine_a)

    url = reverse("cartelera:showtime-list")
    response = client.get(url, {"orden": "inventado"})

    assert response.status_code == 200
    showtimes = list(response.context["showtimes"])
    assert showtimes.index(s1) < showtimes.index(s2)
