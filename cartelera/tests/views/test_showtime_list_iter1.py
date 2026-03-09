"""
Tests — Iteración 1: caso base de ShowtimeListView
Qué verificamos:
  1. La URL responde 200 (la view existe y está conectada).
  2. Solo aparecen funciones futuras; las pasadas no se muestran.
"""
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django import asserts

from cartelera.tests.factories import ShowtimeFactory


def test_showtime_list_devuelve_200(client):
    """La vista responde OK sin necesidad de login."""
    url = reverse("cartelera:showtime-list")
    response = client.get(url)
    assert response.status_code == 200


def test_showtime_list_solo_funciones_futuras(client):
    """Las funciones pasadas no aparecen en el contexto."""
    futura = ShowtimeFactory()  # por defecto: mañana a las 20hs
    pasada = ShowtimeFactory(
        datetime=timezone.now() - timedelta(days=1)
    )

    url = reverse("cartelera:showtime-list")
    response = client.get(url)

    showtimes = list(response.context["showtimes"])
    assert futura in showtimes
    assert pasada not in showtimes
