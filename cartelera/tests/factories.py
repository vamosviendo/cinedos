"""
Factories para tests.
Cada factory crea instancias válidas con datos mínimos,
permitiendo sobreescribir solo lo que el test necesita.
"""
import factory
from django.contrib.auth.models import User
from django.utils import timezone

from cartelera.models import Attendance, Cinema, Match, Movie, Promotion, Showtime


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"usuario_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@ejemplo.com")
    password = factory.PostGenerationMethodCall("set_password", "contraseña123")


class CinemaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cinema

    name = factory.Sequence(lambda n: f"Cine {n}")
    address = "Av. Corrientes 1234"
    neighborhood = "San Nicolás"
    city = "Buenos Aires"


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Sequence(lambda n: f"Película {n}")
    original_title = ""
    rating = "ATP"
    duration_minutes = 100


class PromotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Promotion

    cinema = factory.SubFactory(CinemaFactory)
    description = "2x1 con tarjeta Santander todos los días"
    payment_method = "Santander"
    is_active = True
    valid_from = None
    valid_until = None


class ShowtimeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Showtime

    movie = factory.SubFactory(MovieFactory)
    cinema = factory.SubFactory(CinemaFactory)
    # Por defecto: mañana a las 20hs (siempre futura)
    datetime = factory.LazyFunction(
        lambda: timezone.now().replace(hour=20, minute=0, second=0, microsecond=0)
        + timezone.timedelta(days=1)
    )
    screen = factory.Sequence(lambda n: f"Sala {n}")
    format = Showtime.FORMAT_2D


class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendance

    user = factory.SubFactory(UserFactory)
    showtime = factory.SubFactory(ShowtimeFactory)
    status = Attendance.STATUS_LOOKING
    note = ""


class MatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Match

    showtime = factory.SubFactory(ShowtimeFactory)
    requester = factory.SubFactory(UserFactory)
    requested = factory.SubFactory(UserFactory)
    status = Match.STATUS_PENDING
