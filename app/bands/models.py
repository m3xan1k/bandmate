from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class City(models.Model):
    name = models.CharField(max_length=50)


class Instrument(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey('InstrumentCategory', on_delete=models.SET_NULL,
                                 related_name='instruments')


class InstrumentCategory(models.Model):
    name = models.CharField(max_length=50)


class Style(models.Model):
    name = models.CharField(max_length=50)


class Musician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_busy = models.BooleanField(default=False, null=False, blank=False)
    city = models.ForeignKey('City', on_delete=models.SET_NULL,
                             related_name='musicians', null=True)
    bands = models.ManyToManyField('Band', related_name='musicians')


class Band(models.Model):
    name = models.CharField(max_length=255, blank=True)
    styles = models.ManyToManyField('Style', related_name='bands')
    description = models.TextField(blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL,
                             related_name='bands', null=True)


@receiver(post_save, sender=User)
def create_musician(sender, instance, created, **kwargs):
    if created:
        Musician.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_musician(sender, instance, **kwargs):
    instance.musician.save()
