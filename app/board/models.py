from django.db import models
from django.contrib.auth.models import User


class Category(models.TextChoices):
    BAND_IS_LOOKING = 'BAND_IS_LOOKING', 'Band is looking for mate'
    MUSICIAN_IS_LOOKING = 'MUSICIAN_IS_LOOKING', 'Musician is looking for mates'
    LOOKING_FOR_WORK = 'LOOKING_FOR_WORK', 'Looking for work'
    WORK_IS_LOOKING = 'WORK_IS_LOOKING', 'Work is looking'

    class Meta:
        verbose_name_plural = 'Categories'


class Announcement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='announcements')
    title = models.TextField()
    text = models.TextField()
    category = models.CharField(max_length=50, choices=Category.choices,
                                default=Category.BAND_IS_LOOKING)

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<Announcement author: {self.author} title: {self.name}>'
