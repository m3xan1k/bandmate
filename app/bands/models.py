from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class City(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<City: {self.name}>'


class Instrument(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey('InstrumentCategory', on_delete=models.SET_NULL,
                                 related_name='instruments', null=True)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<Instrument: {self.name}>'


class InstrumentCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<InstrumentCategory: {self.name}>'


class Style(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<Style: {self.name}>'


class MusicianManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activated=True)


class Musician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_busy = models.BooleanField(default=False, null=False, blank=False)
    activated = models.BooleanField(default=False, null=False, blank=False)
    city = models.ForeignKey('City', on_delete=models.SET_NULL,
                             related_name='musicians', null=True)
    bands = models.ManyToManyField('Band', related_name='musicians')
    instruments = models.ManyToManyField('Instrument', related_name='musicians')

    objects = models.Manager()
    activated_objects = MusicianManager()

    def representation_name(self):
        return f'{self.first_name} {self.user.username} {self.last_name}'.strip()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.representation_name()}'

    def __repr__(self):
        return f'<Musician: {self.representation_name()}>'


class Band(models.Model):
    """
    Has custom method to create new instances
    Creation new instance from Constructor is deprecated
    """
    admin = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='administrated_bands')
    name = models.CharField(max_length=255, blank=True)
    styles = models.ManyToManyField('Style', related_name='bands')
    description = models.TextField(blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL,
                             related_name='bands', null=True)

    @classmethod
    def create(cls, admin: User, *args, **kwargs):
        if admin is None:
            raise ValueError("'admin' argument is required to create a band")
        band = cls(*args, **kwargs)
        band.admin.musician.bands.add(band)
        return band

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'<Band: {self.name} id: {self.id}>'


@receiver(post_save, sender=User)
def create_musician(sender, instance, created, **kwargs):
    if created:
        Musician.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_musician(sender, instance, **kwargs):
    instance.musician.save()
