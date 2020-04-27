from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ActiveAnnouncementManager(models.Manager):
    def get_queryset(self):
        due_date = timezone.now() - timedelta(days=30)
        return (
            super(ActiveAnnouncementManager, self).get_queryset()
            .filter(updated_at__gt=due_date)
        )


class Category(models.TextChoices):
    BAND_IS_LOOKING = 'BAND_IS_LOOKING', 'Band is looking for mate'
    MUSICIAN_IS_LOOKING = 'MUSICIAN_IS_LOOKING', 'Musician is looking for mates'
    LOOKING_FOR_WORK = 'LOOKING_FOR_WORK', 'Looking for work'
    WORK_IS_LOOKING = 'WORK_IS_LOOKING', 'Work is looking'


class Announcement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='announcements')
    title = models.TextField()
    text = models.TextField()
    category = models.CharField(max_length=50, choices=Category.choices,
                                default=Category.BAND_IS_LOOKING)
    updated_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    active = ActiveAnnouncementManager()

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<Announcement author: {self.author} title: {self.title}>'
