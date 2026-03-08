"""
Tests de modelos — Fase 1.

Convención:
  - Cada clase de test corresponde a un modelo.
  - Los métodos siguen el patrón: test_<qué_se_prueba>
  - Un test = una sola afirmación lógica (puede tener varios assert
    si todos verifican la misma cosa).

Para correr estos tests:
  pytest cartelera/tests/test_models.py -v
"""
import pytest
from django.db import IntegrityError
from django.utils import timezone

from cartelera.models import Attendance, Cinema, Match, Movie, Promotion, Showtime
from cartelera.tests.factories import (
    AttendanceFactory,
    CinemaFactory,
    MatchFactory,
    MovieFactory,
    PromotionFactory,
    ShowtimeFactory,
    UserFactory,
)


# ---------------------------------------------------------------------------
# Cinema
# ---------------------------------------------------------------------------

class TestCinemaModel:

    def test_str_incluye_nombre_y_barrio(self):
        cinema = CinemaFactory(name="Showcase Nordelta", neighborhood="Tigre")
        assert str(cinema) == "Showcase Nordelta (Tigre)"

    def test_se_ordena_por_nombre(self):
        cinema1 = CinemaFactory(name="Showcase Nordelta")
        cinema2 = CinemaFactory(name="Abasto Shopping")
        cinema3 = CinemaFactory(name="Cine Test")
        assert list(Cinema.objects.all()) == [cinema2, cinema3, cinema1]

    def test_ciudad_default_es_buenos_aires(self):
        cinema = Cinema.objects.create(
            name="Cine Test",
            address="Calle Falsa 123",
            neighborhood="Palermo",
        )
        assert cinema.city == "Buenos Aires"

    def test_puede_tener_multiples_promociones(self):
        cinema = CinemaFactory()
        PromotionFactory(cinema=cinema)
        PromotionFactory(cinema=cinema)
        assert cinema.promotions.count() == 2

    def test_puede_tener_multiples_funciones(self):
        cinema = CinemaFactory()
        ShowtimeFactory(cinema=cinema)
        ShowtimeFactory(cinema=cinema)
        assert cinema.showtimes.count() == 2


# ---------------------------------------------------------------------------
# Movie
# ---------------------------------------------------------------------------

class TestMovieModel:

    def test_str_es_el_titulo(self):
        movie = MovieFactory(title="El Padrino")
        assert str(movie) == "El Padrino"

    def test_se_ordenan_por_titulo(self):
        movie1 = MovieFactory(title="El Padrino")
        movie2 = MovieFactory(title="Zama")
        movie3 = MovieFactory(title="Amarcord")
        assert list(Movie.objects.all()) == [movie3, movie1, movie2]

    def test_titulo_original_puede_estar_vacio(self):
        movie = Movie.objects.create(
            title="Película 1",
            rating="ATP",
            duration_minutes=100,
        )
        assert movie.original_title == ""

    def test_titulo_original_es_opcional_en_formularios(self):
        from django.forms import ModelForm
        from cartelera.models import Movie

        class MovieForm(ModelForm):
            class Meta:
                model = Movie
                fields = ["title", "original_title", "rating"]

        form = MovieForm(data={"title": "Película 1", "rating": "ATP", "original_title": ""})
        assert form.is_valid(), form.errors

    def test_duracion_puede_ser_nula(self):
        movie = MovieFactory(duration_minutes=None)
        assert movie.duration_minutes is None

    def test_puede_tener_multiples_funciones(self):
        movie = MovieFactory()
        ShowtimeFactory(movie=movie)
        ShowtimeFactory(movie=movie)
        assert movie.showtimes.count() == 2


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------

class TestPromotionModel:

    def test_str_incluye_cine_y_descripcion(self):
        cinema = CinemaFactory(name="Hoyts Abasto")
        promo = PromotionFactory(
            cinema=cinema,
            description="2x1 con Ualá todos los días",
        )
        assert str(promo) == "Hoyts Abasto — 2x1 con Ualá todos los días"

    def test_activa_sin_fechas_es_valida_hoy(self):
        promo = PromotionFactory(is_active=True, valid_from=None, valid_until=None)
        assert promo.is_valid_today() is True

    def test_inactiva_no_es_valida_hoy(self):
        promo = PromotionFactory(is_active=False)
        assert promo.is_valid_today() is False

    def test_no_valida_si_no_comenzo_aun(self):
        manana = timezone.localdate() + timezone.timedelta(days=1)
        promo = PromotionFactory(is_active=True, valid_from=manana, valid_until=None)
        assert promo.is_valid_today() is False

    def test_no_valida_si_ya_vencio(self):
        ayer = timezone.localdate() - timezone.timedelta(days=1)
        promo = PromotionFactory(is_active=True, valid_from=None, valid_until=ayer)
        assert promo.is_valid_today() is False

    def test_valida_dentro_del_rango_de_fechas(self):
        ayer = timezone.localdate() - timezone.timedelta(days=1)
        manana = timezone.localdate() + timezone.timedelta(days=1)
        promo = PromotionFactory(is_active=True, valid_from=ayer, valid_until=manana)
        assert promo.is_valid_today() is True


# ---------------------------------------------------------------------------
# Showtime
# ---------------------------------------------------------------------------

class TestShowtimeModel:

    def test_str_incluye_pelicula_cine_y_fecha(self):
        movie = MovieFactory(title="Oppenheimer")
        cinema = CinemaFactory(name="Village Recoleta")
        dt = timezone.datetime(2025, 7, 21, 20, 30, tzinfo=timezone.get_current_timezone())
        showtime = ShowtimeFactory(movie=movie, cinema=cinema, datetime=dt)
        resultado = str(showtime)
        assert "Oppenheimer" in resultado
        assert "Village Recoleta" in resultado
        assert "21/07/2025" in resultado
        assert "20:30" in resultado

    def test_se_ordena_por_fecha_y_hora_cine_y_sala(self):
        cinema1 = CinemaFactory(name="Atlas Recoleta")
        cinema2 = CinemaFactory(name="Showcase Haedo")
        sala1 = "Sala 1"
        sala2 = "Sala 2"
        dt1 = timezone.datetime(2025, 7, 21, 20, 30, tzinfo=timezone.get_current_timezone())
        dt2 = timezone.datetime(2025, 7, 21, 22, 50, tzinfo=timezone.get_current_timezone())
        showtime1 = ShowtimeFactory(datetime=dt2, cinema=cinema1, screen=sala2)
        showtime2 = ShowtimeFactory(datetime=dt2, cinema=cinema1, screen=sala1)
        showtime3 = ShowtimeFactory(datetime=dt1, cinema=cinema2, screen=sala1)
        showtime4 = ShowtimeFactory(datetime=dt1, cinema=cinema1, screen=sala1)

        assert list(Showtime.objects.all()) == [showtime4, showtime3, showtime2, showtime1]

    def test_funcion_futura_es_upcoming(self):
        showtime = ShowtimeFactory(
            datetime=timezone.now() + timezone.timedelta(hours=2)
        )
        assert showtime.is_upcoming() is True

    def test_funcion_pasada_no_es_upcoming(self):
        showtime = ShowtimeFactory(
            datetime=timezone.now() - timezone.timedelta(hours=2)
        )
        assert showtime.is_upcoming() is False

    def test_available_spots_cuenta_solo_los_que_buscan_companero(self):
        showtime = ShowtimeFactory()
        AttendanceFactory(showtime=showtime, status=Attendance.STATUS_LOOKING)
        AttendanceFactory(showtime=showtime, status=Attendance.STATUS_LOOKING)
        AttendanceFactory(showtime=showtime, status=Attendance.STATUS_MATCHED)
        AttendanceFactory(showtime=showtime, status=Attendance.STATUS_CANCELLED)
        assert showtime.available_spots() == 2

    def test_no_puede_haber_dos_funciones_en_mismo_cine_sala_y_hora(self):
        cinema = CinemaFactory()
        dt = timezone.now() + timezone.timedelta(days=1)
        ShowtimeFactory(cinema=cinema, screen="Sala 1", datetime=dt)
        with pytest.raises(IntegrityError):
            ShowtimeFactory(cinema=cinema, screen="Sala 1", datetime=dt)

    def test_mismo_cine_distinta_sala_mismo_horario_es_valido(self):
        cinema = CinemaFactory()
        dt = timezone.now() + timezone.timedelta(days=1)
        s1 = ShowtimeFactory(cinema=cinema, screen="Sala 1", datetime=dt)
        s2 = ShowtimeFactory(cinema=cinema, screen="Sala 2", datetime=dt)
        assert s1.pk != s2.pk


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

class TestAttendanceModel:

    def test_str_incluye_usuario_y_funcion(self):
        user = UserFactory(username="juancito")
        attendance = AttendanceFactory(user=user)
        assert str(attendance.showtime) in str(attendance)
        assert "juancito" in str(attendance)

    def test_estado_default_es_looking(self):
        user = UserFactory(username="juancito")
        showtime = ShowtimeFactory()
        attendance = Attendance.objects.create(
            user=user,
            showtime=showtime,
            note="",
        )
        assert attendance.status == Attendance.STATUS_LOOKING

    def test_un_usuario_no_puede_anotarse_dos_veces_a_la_misma_funcion(self):
        user = UserFactory()
        showtime = ShowtimeFactory()
        AttendanceFactory(user=user, showtime=showtime)
        with pytest.raises(IntegrityError):
            AttendanceFactory(user=user, showtime=showtime)

    def test_dos_usuarios_distintos_pueden_anotarse_a_la_misma_funcion(self):
        showtime = ShowtimeFactory()
        a1 = AttendanceFactory(showtime=showtime, user=UserFactory())
        a2 = AttendanceFactory(showtime=showtime, user=UserFactory())
        assert a1.pk != a2.pk

    def test_nota_puede_estar_vacia(self):
        attendance = AttendanceFactory()
        assert attendance.note == ""


# # ---------------------------------------------------------------------------
# # Match
# # ---------------------------------------------------------------------------

class TestMatchModel:

    def test_str_incluye_ambos_usuarios(self):
        requester = UserFactory(username="ana")
        requested = UserFactory(username="beto")
        match = MatchFactory(requester=requester, requested=requested)
        resultado = str(match)
        assert "ana" in resultado
        assert "beto" in resultado
        assert str(match.showtime) in resultado

    def test_estado_default_es_pending(self):
        showtime = ShowtimeFactory()
        requester = UserFactory()
        requested = UserFactory()
        match = Match.objects.create(
            showtime=showtime,
            requester=requester,
            requested=requested,
        )
        assert match.status == Match.STATUS_PENDING

    def test_puede_confirmarse(self):
        match = MatchFactory(status=Match.STATUS_PENDING)
        match.status = Match.STATUS_CONFIRMED
        match.save()
        match.refresh_from_db()
        assert match.status == Match.STATUS_CONFIRMED

    def test_puede_rechazarse(self):
        match = MatchFactory(status=Match.STATUS_PENDING)
        match.status = Match.STATUS_REJECTED
        match.save()
        match.refresh_from_db()
        assert match.status == Match.STATUS_REJECTED

    def test_match_referencia_una_funcion(self):
        showtime = ShowtimeFactory()
        match = MatchFactory(showtime=showtime)
        assert match.showtime.pk == showtime.pk
