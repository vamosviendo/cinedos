"""
Tests — Iteración 4: usuario autenticado en ShowtimeListView
Qué verificamos:
  1. Usuario anónimo: el contexto no incluye 'user_showtimes'
  2. Usuario autenticado: el contexto incluye 'user_showtimes'
  3. Solo aparecen IDs de funciones con asistencia activa (looking + matched)
  4. Las asistencias canceladas no aparecen en 'user_showtimes'
"""
from django.urls import reverse

from cartelera.models import Attendance
from cartelera.tests.factories import AttendanceFactory, ShowtimeFactory, UserFactory


def test_usuario_anonimo_no_recibe_user_showtimes(client):
    """El contexto no incluye 'user_showtimes' si el usuario no está logueado."""
    url = reverse("cartelera:showtime-list")
    response = client.get(url)
    assert "user_showtimes" not in response.context


def test_usuario_autenticado_recibe_user_showtimes(client):
    """El contexto incluye 'user_showtimes' si el usuario está logueado."""
    user = UserFactory()
    client.force_login(user)

    url = reverse("cartelera:showtime-list")
    response = client.get(url)
    assert "user_showtimes" in response.context


def test_user_showtimes_contiene_ids_de_asistencias_activas(client):
    """user_showtimes incluye IDs de funciones con status looking o matched."""
    user = UserFactory()
    client.force_login(user)

    asistencia_looking = AttendanceFactory(user=user, status=Attendance.STATUS_LOOKING)
    asistencia_matched = AttendanceFactory(user=user, status=Attendance.STATUS_MATCHED)

    url = reverse("cartelera:showtime-list")
    response = client.get(url)

    user_showtimes = response.context["user_showtimes"]
    assert asistencia_looking.showtime_id in user_showtimes
    assert asistencia_matched.showtime_id in user_showtimes


def test_user_showtimes_excluye_asistencias_canceladas(client):
    """user_showtimes no incluye IDs de funciones con status cancelled."""
    user = UserFactory()
    client.force_login(user)

    asistencia_cancelada = AttendanceFactory(user=user, status=Attendance.STATUS_CANCELLED)

    url = reverse("cartelera:showtime-list")
    response = client.get(url)

    user_showtimes = response.context["user_showtimes"]
    assert asistencia_cancelada.showtime_id not in user_showtimes


def test_user_showtimes_no_incluye_asistencias_de_otros_usuarios(client):
    """user_showtimes solo refleja las asistencias del usuario logueado."""
    user = UserFactory()
    otro_usuario = UserFactory()
    client.force_login(user)

    asistencia_otro = AttendanceFactory(user=otro_usuario, status=Attendance.STATUS_LOOKING)

    url = reverse("cartelera:showtime-list")
    response = client.get(url)

    user_showtimes = response.context["user_showtimes"]
    assert asistencia_otro.showtime_id not in user_showtimes
