from django.db import models
from django.contrib.auth.models import User


class AnnouncementCategory(models.Model):
    BAND_IS_LOOKING = 'band_is_looking'
    MUSICIAN_IS_LOOKING = 'musician_is_looking'
    LOOKING_FOR_WORK = 'looking_for_work'
    WORK_IS_LOOKING = 'work_is_looking'

    NAME = [
        (BAND_IS_LOOKING, _('Band is looking for mate')),
        (MUSICIAN_IS_LOOKING, _('Musician is looking for mates')),
        (LOOKING_FOR_WORK, _('Looking for work')),
        (WORK_IS_LOOKING, _('Work for musicians')),
    ]

    name = models.CharField(choices=NAME, default=BAND_IS_LOOKING)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<AnnouncementCategory name: {self.name}>'


class Announcement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='announcements')
    title = models.TextField()
    text = models.TextField()
    category = models.ForeignKey('AnnouncementCategory', related_name='announcements')

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'<Announcement author: {self.author} title: {self.name}>'
