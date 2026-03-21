import pytest
from django.urls import reverse

from cartelera.models import Attendance
from cartelera.tests.factories import (
    AttendanceFactory,
    ShowtimeFactory,
    UserFactory
)


@pytest.fixture
def showtime():
    return ShowtimeFactory()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def attendance(showtime, user):
    return AttendanceFactory(showtime=showtime, user=user)


@pytest.fixture
def url_create(showtime):
    return reverse("cartelera:attendance-create", kwargs={"pk": showtime.pk})


@pytest.fixture
def url_cancel(attendance):
    return reverse("cartelera:attendance-cancel", kwargs={"pk": attendance.pk})


class TestAttendanceCreateBase:
    """
    Tests — Iteración 1: caso base de AttendanceCreateView
    Qué verificamos:
      1. Usuario anónimo es redirigido al login.
      2. Usuario autenticado recibe 200 con GET (o bien, POST vacío redirige).
    """

    def test_anonimo_es_redirigido_al_login(self, client, showtime, url_create):
        response = client.post(url_create)
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_usuario_autenticado_puede_acceder(self, client, showtime, user, url_create):
        client.force_login(user)
        response = client.post(url_create)
        # Redirige al detalle de la función — no da error
        assert response.status_code == 302

    def test_crea_asistencia_si_no_existe(self, client, showtime, user, url_create):
        attendances = Attendance.objects.count()
        client.force_login(user)
        client.post(url_create)
        assert Attendance.objects.count() == attendances + 1

    def test_si_existe_asistencia_redirige_sin_hacer_nada_mas(
            self, client, showtime, user, attendance, url_create):
        # AttendanceFactory(user=user, showtime=showtime)
        client.force_login(user)
        client.post(url_create)
        assert Attendance.objects.filter(user=user, showtime=showtime).count() == 1


class TestAttendanceCancelBase:
    """
    Tests — Iteración 1: caso base de AttendanceCancelView
    Qué verificamos:
      1. Usuario anónimo es redirigido al login.
      2. Usuario autenticado puede acceder.
    """

    def test_anonimo_es_redirigido_al_login(self, client):
        asistencia = AttendanceFactory()
        url = reverse("cartelera:attendance-cancel", kwargs={"pk": asistencia.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_usuario_autenticado_puede_acceder(self, client, user, url_cancel):
        client.force_login(user)
        response = client.post(url_cancel)
        assert response.status_code == 302

    def test_cancela_asistencia(self, client, user, attendance, url_cancel):
        client.force_login(user)
        client.post(url_cancel)
        attendance.refresh_from_db()
        assert attendance.status == Attendance.STATUS_CANCELLED
