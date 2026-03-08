from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Cinema(models.Model):
    """Un cine o sala específica."""

    name = models.CharField("nombre", max_length=200)
    address = models.CharField("direccion", max_length=300)
    neighborhood = models.CharField("barrio/localidad", max_length=100)
    city = models.CharField("ciudad", max_length=100, default="Buenos Aires")

    class Meta:
        verbose_name = "cine"
        verbose_name_plural = "cines"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.neighborhood})"


class Movie(models.Model):
    title = models.CharField("título", max_length=300)
    original_title = models.CharField(
        "título original", max_length=300, blank=True, default=""
    )
    poster_url = models.URLField("URL del póster", blank=True, default="")
    rating = models.CharField(
        "clasificación",
        max_length=10,
        blank=True,
        default="",
        help_text="Ej: ATP, +13, +16, +18",
    )
    duration_minutes = models.PositiveIntegerField(
        "duración (minutos)", null=True, blank=True
    )

    class Meta:
        verbose_name = "película"
        verbose_name_plural = "películas"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Promotion(models.Model):
    """Una promoción 2x1 vigente en un cine."""

    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.CASCADE,
        related_name="promotions",
        verbose_name="cine",
    )
    description = models.CharField(
        "descripción",
        max_length=300,
        help_text="Ej: 2x1 con tarjeta Santander todos los días",
    )
    payment_method = models.CharField(
        "medio de pago",
        max_length=100,
        blank=True,
        default="",
        help_text="Ej: Santander, Ualá, Mercado Pago",
    )
    is_active = models.BooleanField("activa", default=True)
    valid_from = models.DateField("válida desde", null=True, blank=True)
    valid_until = models.DateField("válida hasta", null=True, blank=True)

    class Meta:
        verbose_name = "promoción"
        verbose_name_plural = "promociones"

    def __str__(self):
        return f"{self.cinema.name} — {self.description}"

    def is_valid_today(self):
        """Devuelve True si la promoción está activa hoy."""
        if not self.is_active:
            return False
        today = timezone.localdate()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True


class Showtime(models.Model):
    """Una función: película + cine + fecha/hora."""

    FORMAT_2D = "2D"
    FORMAT_3D = "3D"
    FORMAT_IMAX = "IMAX"
    FORMAT_CHOICES = [
        (FORMAT_2D, "2D"),
        (FORMAT_3D, "3D"),
        (FORMAT_IMAX, "IMAX"),
    ]

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="showtimes",
        verbose_name="película",
    )
    cinema = models.ForeignKey(
        Cinema,
        on_delete=models.CASCADE,
        related_name="showtimes",
        verbose_name="cine",
    )
    datetime = models.DateTimeField("fecha y hora")
    screen = models.CharField("sala", max_length=50, blank=True, default="")
    format = models.CharField(
        "formato", max_length=10, choices=FORMAT_CHOICES, default=FORMAT_2D
    )

    class Meta:
        verbose_name = "función"
        verbose_name_plural = "funciones"
        ordering = ["datetime", "cinema", "screen"]
        # No puede haber dos funciones idénticas en el mismo cine/sala/hora
        constraints = [
            models.UniqueConstraint(
                fields=["cinema", "datetime", "screen"],
                name="unique_showtime_per_screen",
            )
        ]

    def __str__(self):
        return (
            f"{self.movie.title} — {self.cinema.name} — "
            f"{self.datetime.strftime('%d/%m/%Y %H:%M')}"
        )

    def is_upcoming(self):
        """Devuelve True si la función aún no ocurrió."""
        if self.datetime > timezone.localtime():
            return True
        return False

    def available_spots(self):
        """Cuántos usuarios están buscando compañero para esta función."""
        return self.attendances.filter(
            status=Attendance.STATUS_LOOKING
        ).count()


class Attendance(models.Model):
    """Un usuario que se anotó para una función buscando compañero de 2x1."""

    STATUS_LOOKING = "looking"
    STATUS_MATCHED = "matched"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_LOOKING, "Buscando compañero"),
        (STATUS_MATCHED, "Compañero encontrado"),
        (STATUS_CANCELLED, "Cancelado"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name="usuario",
    )
    showtime = models.ForeignKey(
        Showtime,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name="función",
    )
    status = models.CharField(
        "estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_LOOKING,
    )
    created_at = models.DateTimeField("anotado el", auto_now_add=True)
    note = models.CharField(
        "nota opcional",
        max_length=200,
        blank=True,
        default="",
        help_text="Ej: Solo voy si es versión original",
    )

    class Meta:
        verbose_name = "asistencia"
        verbose_name_plural = "asistencias"
        ordering = ["created_at"]

        constraints = [
            # Un usuario no puede anotarse dos veces a la misma función
            models.UniqueConstraint(
                fields=["user", "showtime"],
                name="unique_attendance_per_user_showtime",
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.showtime}"
class Match(models.Model):
    """Dos usuarios que acordaron compartir una promo 2x1 en una función."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente de confirmación"),
        (STATUS_CONFIRMED, "Confirmado"),
        (STATUS_REJECTED, "Rechazado"),
    ]

    showtime = models.ForeignKey(
        Showtime,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name="función",
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="match_requests_sent",
        verbose_name="quien propone",
    )
    requested = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="match_requests_received",
        verbose_name="a quien se propone",
    )
    status = models.CharField(
        "estado", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField("propuesto el", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado el", auto_now=True)

    class Meta:
        verbose_name = "match"
        verbose_name_plural = "matches"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.requester} - {self.requested} para {self.showtime}"
