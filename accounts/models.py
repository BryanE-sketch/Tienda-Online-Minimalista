from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuario propio: hoy igual al de Django, mañana ampliable."""

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.username