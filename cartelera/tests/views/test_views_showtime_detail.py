from django.urls import reverse

from cartelera.models import Attendance
from cartelera.tests.factories import (
    AttendanceFactory,
    ShowtimeFactory,
    UserFactory,
)


class TestShowtimeDetailBase:
    """
    Tests — Iteración 1: caso base de ShowtimeDetailView
    Qué verificamos:
      1. Una PK válida responde 200.
      2. Una PK inexistente responde 404.
    """

    def test_devuelve_200(self, client):
        """La vista responde OK con una función existente."""
        showtime = ShowtimeFactory()
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_devuelve_404_si_showtime_no_existe(self, client):
        """La vista responde 404 si la función no existe."""
        url = reverse("cartelera:showtime-detail", kwargs={"pk": 99999})
        response = client.get(url)
        assert response.status_code == 404


class TestShowtimeDetailContext:
    """
    Tests — Iteración 2: contexto de ShowtimeDetailView
    Qué verificamos:
      1. El contexto incluye el showtime correcto.
      2. El contexto incluye las asistencias con status 'looking'.
      3. Las asistencias con otros status no aparecen.
    """

    def test_contexto_incluye_el_showtime(self, client):
        showtime = ShowtimeFactory()
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert response.context["showtime"] == showtime

    def test_contexto_incluye_asistencias_looking(self, client):
        showtime = ShowtimeFactory()
        asistencia = AttendanceFactory(
            showtime=showtime,
            status=Attendance.STATUS_LOOKING
        )
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert asistencia in response.context["attendances"]

    def test_contexto_excluye_asistencias_no_looking(self, client):
        showtime = ShowtimeFactory()
        matched = AttendanceFactory(
            showtime=showtime,
            status=Attendance.STATUS_MATCHED
        )
        cancelada = AttendanceFactory(
            showtime=showtime,
            status=Attendance.STATUS_CANCELLED
        )
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        attendances = list(response.context["attendances"])
        assert matched not in attendances
        assert cancelada not in attendances

    def test_contexto_excluye_asistencias_de_otras_funciones(self, client):
        showtime = ShowtimeFactory()
        otra_funcion = ShowtimeFactory()
        asistencia_otra = AttendanceFactory(showtime=otra_funcion, status=Attendance.STATUS_LOOKING)
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert asistencia_otra not in list(response.context["attendances"])
class TestShowtimeDetailUser:
    """
    Tests — Iteración 3: usuario autenticado en ShowtimeDetailView
    Qué verificamos:
      1. Usuario anónimo: 'user_attendance' no está en el contexto.
      2. Usuario autenticado sin asistencia: 'user_attendance' es None.
      3. Usuario autenticado con asistencia: 'user_attendance' es su Attendance.
    """

    def test_usuario_anonimo_no_recibe_user_attendance(self, client):
        showtime = ShowtimeFactory()
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert "user_attendance" not in response.context

    def test_usuario_autenticado_sin_asistencia_recibe_none(self, client):
        user = UserFactory()
        client.force_login(user)
        showtime = ShowtimeFactory()
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert response.context["user_attendance"] is None

    def test_usuario_autenticado_con_asistencia_recibe_su_attendance(self, client):
        user = UserFactory()
        client.force_login(user)
        showtime = ShowtimeFactory()
        asistencia = AttendanceFactory(user=user, showtime=showtime)
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert response.context["user_attendance"] == asistencia

    def test_user_attendance_no_muestra_asistencias_a_otras_funciones(self, client):
        user = UserFactory()
        client.force_login(user)
        showtime = ShowtimeFactory()
        otra_funcion = ShowtimeFactory()
        AttendanceFactory(user=user, showtime=otra_funcion)
        url = reverse("cartelera:showtime-detail", kwargs={"pk": showtime.pk})
        response = client.get(url)
        assert response.context["user_attendance"] is None
