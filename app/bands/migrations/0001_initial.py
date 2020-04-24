# Generated by Django 3.0.5 on 2020-04-24 12:27

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
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Musician',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50)),
                ('bio', models.TextField(blank=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('is_busy', models.BooleanField(default=False)),
                ('activated', models.BooleanField(default=False)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='musicians', to='bands.City')),
                ('instruments', models.ManyToManyField(related_name='musicians', to='bands.Instrument')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='instrument',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='instruments', to='bands.InstrumentCategory'),
        ),
        migrations.CreateModel(
            name='Band',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='administrated_bands', to=settings.AUTH_USER_MODEL)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bands', to='bands.City')),
                ('musicians', models.ManyToManyField(related_name='bands', to='bands.Musician')),
                ('styles', models.ManyToManyField(related_name='bands', to='bands.Style')),
            ],
        ),
    ]