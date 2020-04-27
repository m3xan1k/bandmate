# Generated by Django 3.0.5 on 2020-04-26 09:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('text', models.TextField()),
                ('category', models.CharField(choices=[('BAND_IS_LOOKING', 'Band is looking for mate'), ('MUSICIAN_IS_LOOKING', 'Musician is looking for mates'), ('LOOKING_FOR_WORK', 'Looking for work'), ('WORK_IS_LOOKING', 'Work is looking'), ("<class 'board.models.Category.Meta'>", 'Meta')], default='BAND_IS_LOOKING', max_length=50)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
