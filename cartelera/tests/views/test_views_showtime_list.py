from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from cartelera.models import Attendance
from cartelera.tests.factories import (
    AttendanceFactory,
    CinemaFactory,
    MovieFactory,
    ShowtimeFactory,
    UserFactory,
)


class TestShowtimeListGeneral:
    """
    Tests — Iteración 1: caso base de ShowtimeListView
    Qué verificamos:
      1. La URL responde 200 (la view existe y está conectada).
      2. Solo aparecen funciones futuras; las pasadas no se muestran.
    """
    def test_showtime_list_devuelve_200(self, client):
        """La vista responde OK sin necesidad de login."""
        url = reverse("cartelera:showtime-list")
        response = client.get(url)
        assert response.status_code == 200

    def test_showtime_list_solo_funciones_futuras(self, client):
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


class TestShowtimeListFilters:
    """
    Tests — Iteración 2: filtros de ShowtimeListView
    Qué verificamos:
      1. ?fecha=      filtra por fecha exacta
      2. ?pelicula=   filtra por id de película
      3. ?cine=       filtra por id de cine
      4. ?barrio=     filtra por barrio del cine
      5. Filtros combinados se aplican con AND
    """
    def test_filtro_por_fecha(self, client):
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

    def test_filtro_por_pelicula(self, client):
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

    def test_filtro_por_cine(self, client):
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

    def test_filtro_por_barrio(self, client):
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

    def test_filtros_combinados(self, client):
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


class TestShowtimeListOrder:
    """
    Tests — Iteración 3: orden configurable de ShowtimeListView
    Qué verificamos:
      1. Sin ?orden= respeta el orden del modelo (datetime, cinema, screen)
      2. ?orden=fecha     ordena por datetime ascendente
      3. ?orden=pelicula  ordena por título de película ascendente
      4. ?orden=cine      ordena por nombre de cine ascendente
      5. Un valor inválido en ?orden= cae al orden por defecto
    """
    def test_orden_por_defecto(self, client):
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

    def test_orden_por_fecha(self, client):
        """?orden=fecha ordena por datetime ascendente."""
        manana = timezone.now() + timedelta(days=1)
        pasado = timezone.now() + timedelta(days=2)

        s_tarde = ShowtimeFactory(datetime=pasado)
        s_temprano = ShowtimeFactory(datetime=manana)

        url = reverse("cartelera:showtime-list")
        response = client.get(url, {"orden": "fecha"})

        showtimes = list(response.context["showtimes"])
        assert showtimes.index(s_temprano) < showtimes.index(s_tarde)

    def test_orden_por_pelicula(self, client):
        """?orden=pelicula ordena por título ascendente."""
        pelicula_a = MovieFactory(title="Amelie")
        pelicula_z = MovieFactory(title="Zama")

        s_z = ShowtimeFactory(movie=pelicula_z)
        s_a = ShowtimeFactory(movie=pelicula_a)

        url = reverse("cartelera:showtime-list")
        response = client.get(url, {"orden": "pelicula"})

        showtimes = list(response.context["showtimes"])
        assert showtimes.index(s_a) < showtimes.index(s_z)

    def test_orden_por_cine(self, client):
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

    def test_orden_invalido_cae_a_defecto(self, client):
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


class TestShowtimeListUser:
    """
    Tests — Iteración 4: usuario autenticado en ShowtimeListView
    Qué verificamos:
      1. Usuario anónimo: el contexto no incluye 'user_showtimes'
      2. Usuario autenticado: el contexto incluye 'user_showtimes'
      3. Solo aparecen IDs de funciones con asistencia activa (looking + matched)
      4. Las asistencias canceladas no aparecen en 'user_showtimes'
    """
    def test_usuario_anonimo_no_recibe_user_showtimes(self, client):
        """El contexto no incluye 'user_showtimes' si el usuario no está logueado."""
        url = reverse("cartelera:showtime-list")
        response = client.get(url)
        assert "user_showtimes" not in response.context

    def test_usuario_autenticado_recibe_user_showtimes(self, client):
        """El contexto incluye 'user_showtimes' si el usuario está logueado."""
        user = UserFactory()
        client.force_login(user)

        url = reverse("cartelera:showtime-list")
        response = client.get(url)
        assert "user_showtimes" in response.context

    def test_user_showtimes_contiene_ids_de_asistencias_activas(self, client):
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

    def test_user_showtimes_excluye_asistencias_canceladas(self, client):
        """user_showtimes no incluye IDs de funciones con status cancelled."""
        user = UserFactory()
        client.force_login(user)

        asistencia_cancelada = AttendanceFactory(user=user, status=Attendance.STATUS_CANCELLED)

        url = reverse("cartelera:showtime-list")
        response = client.get(url)

        user_showtimes = response.context["user_showtimes"]
        assert asistencia_cancelada.showtime_id not in user_showtimes

    def test_user_showtimes_no_incluye_asistencias_de_otros_usuarios(self, client):
        """user_showtimes solo refleja las asistencias del usuario logueado."""
        user = UserFactory()
        otro_usuario = UserFactory()
        client.force_login(user)

        asistencia_otro = AttendanceFactory(user=otro_usuario, status=Attendance.STATUS_LOOKING)

        url = reverse("cartelera:showtime-list")
        response = client.get(url)

        user_showtimes = response.context["user_showtimes"]
        assert asistencia_otro.showtime_id not in user_showtimes

    def test_user_showtimes_contiene_ids_de_funciones_no_de_asistencias(self, client):
        """user_showtimes debe contener IDs de Showtime, no de Attendance.

        Si hay objetos previos en la DB, el id de Attendance difiere del
        showtime_id. El bug devolvía ids de Attendance en lugar de showtime_ids.
        """
        user = UserFactory()
        client.force_login(user)

        # Crear una función extra para que los IDs se desincronicen
        ShowtimeFactory()

        asistencia = AttendanceFactory(user=user, status=Attendance.STATUS_LOOKING)
        # A esta altura: asistencia.id != asistencia.showtime_id (con alta probabilidad)

        url = reverse("cartelera:showtime-list")
        response = client.get(url)

        user_showtimes = response.context["user_showtimes"]
        assert asistencia.showtime_id in user_showtimes
        assert asistencia.id not in user_showtimes or asistencia.id == asistencia.showtime_id