from django.db import models

class Person(models.Model):
    """Модель, представляющая таблицу базы данных."""

    uuid4 = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    vector = models.BinaryField(null=True)