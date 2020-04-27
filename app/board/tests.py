from datetime import timedelta

from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import auth
from django.utils import timezone

from board.models import Category, Announcement
from users.views import LogInView
from board.views import AnnouncementDashboardView, AnnouncementEditView, AnnouncementsView


class BoardTest(TestCase):

    ANNOUNCEMENT_DASHBOARD_URL = reverse(AnnouncementDashboardView.name)
    ANNOUNCEMENT_EDIT_URL = reverse(AnnouncementEditView.name)
    ANNOUNCEMENTS_URL = reverse(AnnouncementsView.name)
    LOGIN_URL = reverse(LogInView.name)

    def setUp(self):
        # set users
        user_0 = User(username='test_user_0', email='test@test.test')
        user_0.set_password('password')
        user_0.save()

        user_1 = User(username='test_user_1', email='test_1@test.test')
        user_1.set_password('password')
        user_1.save()

        self.client.login(username='test_user_0', password='password')

        # make announcements
        Announcement.objects.create(
            author=user_0,
            title='announcement_0',
            text='text_0',
            category=Category.MUSICIAN_IS_LOOKING,
        )
        Announcement.objects.create(
            author=user_1,
            title='announcement_1',
            text='text_1',
            category=Category.WORK_IS_LOOKING,
        )

    def tearDown(self):
        Announcement.objects.all().delete()
        User.objects.all().delete()

    def test_models_creation(self):
        announcement_0 = Announcement.objects.first()
        self.assertEqual(announcement_0.title, 'announcement_0')
        self.assertEqual(Category(announcement_0.category).label,
                         'Musician is looking for mates')
        self.assertEqual(announcement_0.category,
                         'MUSICIAN_IS_LOOKING')

        user = User.objects.first()
        self.assertEqual(user.announcements.first(), announcement_0)

    def test_get_announcements_dashboard(self):
        response: HttpResponse = self.client.get(self.ANNOUNCEMENT_DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/announcements_dashboard.html')

        announcements = response.context[0].get('announcements')
        self.assertEqual(announcements.count(), 1)
        self.assertEqual(announcements.first().title, 'announcement_0')

        announcement_2 = Announcement.objects.create(
            author=auth.get_user(self.client),
            title='announcement_2',
            text='text_2',
            category=Category.MUSICIAN_IS_LOOKING,
        )
        announcement_2.updated_at = timezone.now() - timedelta(days=35)
        announcement_2.save()

        response: HttpResponse = self.client.get(
            self.ANNOUNCEMENT_DASHBOARD_URL + '?active=1')
        announcements = response.context[0].get('announcements')
        self.assertEqual(announcements.count(), 1)
        self.assertEqual(announcements.first().title, 'announcement_0')

        response: HttpResponse = self.client.get(
            self.ANNOUNCEMENT_DASHBOARD_URL + '?archived=1')
        announcements = response.context[0].get('announcements')
        self.assertEqual(announcements.count(), 1)
        self.assertEqual(announcements.first().title, 'announcement_2')

        self.client.logout()
        response: HttpResponse = self.client.get(self.ANNOUNCEMENT_DASHBOARD_URL)
        self.assertRedirects(response,
                             f'{self.LOGIN_URL}?next={self.ANNOUNCEMENT_DASHBOARD_URL}')

    def test_get_new_announcement(self):
        response: HttpResponse = self.client.get(self.ANNOUNCEMENT_EDIT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/announcement_edit.html')

    def test_post_new_announcement(self):
        announcement_data = {
            'title': 'new_announcement',
            'text': 'new_text',
            'category': Category.LOOKING_FOR_WORK,
        }
        response: HttpResponse = self.client.post(self.ANNOUNCEMENT_EDIT_URL,
                                                  data=announcement_data)
        self.assertRedirects(response, self.ANNOUNCEMENT_DASHBOARD_URL)

        announcements = Announcement.objects.filter(author=auth.get_user(self.client)).all()
        self.assertEquals(announcements.count(), 2)
        self.assertEquals(announcements.last().title, 'new_announcement')

    def test_get_edit_announcement(self):
        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()
        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/'
        )
        self.assertEqual(response.status_code, 200)
        form = response.context[0].get('form')
        announcement = form.instance
        self.assertEqual(announcement.author, auth.get_user(self.client))
        self.assertEqual(announcement.title, 'announcement_0')

    def test_get_edit_announcement_another_user(self):
        user_0 = auth.get_user(self.client)
        self.client.logout()
        self.client.login(username='test_user_1', password='password')
        announcement = Announcement.objects.filter(author=user_0).first()
        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/'
        )
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

    def test_put_edit_announcement(self):
        new_data = {
            'title': 'edited',
            'text': 'edited',
            'category': Category.BAND_IS_LOOKING,
        }
        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()

        header = {'HTTP_X_HTTP_METHOD_OVERRIDE': 'PUT'}
        response: HttpResponse = self.client.post(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/',
            data=new_data,
            **header,
        )
        self.assertEqual(response.status_code, 302)

        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()
        self.assertEqual(announcement.title, 'edited')

        frozen_update = announcement.updated_at
        response: HttpResponse = self.client.post(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/?update=1',
            **header,
        )
        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()
        self.assertEqual(frozen_update, announcement.updated_at)

        announcement.updated_at = timezone.now() - timedelta(hours=5)
        announcement.save()
        response: HttpResponse = self.client.post(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/?update=1',
            **header,
        )
        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()
        self.assertNotEqual(frozen_update, announcement.updated_at)
        self.assertLess(frozen_update, announcement.updated_at)

    def test_put_edit_announcement_another_user(self):
        user_0 = auth.get_user(self.client)
        new_data = {
            'title': 'updated',
            'text': 'updated',
            'category': Category.BAND_IS_LOOKING,
        }
        announcement = Announcement.objects.filter(author=user_0).first()

        self.client.logout()
        self.client.login(username='test_user_1', password='password')

        header = {'HTTP_X_HTTP_METHOD_OVERRIDE': 'PUT'}
        response: HttpResponse = self.client.post(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/',
            data=new_data,
            **header,
        )
        self.assertEqual(response.status_code, 403)

        announcement = Announcement.objects.filter(author=user_0).first()
        self.assertEqual(announcement.title, 'announcement_0')

    def test_delete_edit_announcement(self):
        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()
        response: HttpResponse = (
            self.client
            .delete(f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/')
        )
        self.assertRedirects(response, self.ANNOUNCEMENT_DASHBOARD_URL)
        announcements = (
            Announcement.objects
            .filter(author=auth.get_user(self.client))
        )
        self.assertEqual(announcements.count(), 0)

    def test_delete_edit_announcement_another_user(self):
        user_0 = auth.get_user(self.client)
        announcement = Announcement.objects.filter(author=user_0).first()

        self.client.logout()
        self.client.login(username='test_user_1', password='password')

        response: HttpResponse = (
            self.client
            .delete(f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id}/')
        )
        self.assertEqual(response.status_code, 403)
        announcements = (
            Announcement.objects
            .filter(author=user_0)
        )
        self.assertEqual(announcements.count(), 1)

    def test_404_edit_announcement(self):
        announcement = Announcement.objects.filter(author=auth.get_user(self.client)).first()

        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id + 5}/'
        )
        self.assertEqual(response.status_code, 404)

        header = {'HTTP_X_HTTP_METHOD_OVERRIDE': 'PUT'}
        response: HttpResponse = self.client.put(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id + 5}/',
            data={},
            header=header,
        )
        self.assertEqual(response.status_code, 404)

        response: HttpResponse = self.client.delete(
            f'{self.ANNOUNCEMENT_EDIT_URL}{announcement.id + 5}/'
        )
        self.assertEqual(response.status_code, 404)

    def test_announcement_list(self):
        response: HttpResponse = self.client.get(self.ANNOUNCEMENTS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/announcements.html')

        announcements = response.context[0].get('announcements')
        self.assertEqual(announcements.count(), 2)

        announcement_0 = Announcement.objects.first()
        announcement_0.updated_at = timezone.now() - timedelta(days=31)
        announcement_0.save()

        response: HttpResponse = self.client.get(self.ANNOUNCEMENTS_URL)
        announcements = response.context[0].get('announcements')
        self.assertEqual(announcements.count(), 1)

    def test_announcement_detail(self):
        announcement_1 = Announcement.objects.last()
        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENTS_URL}{announcement_1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/announcement.html')

        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENTS_URL}{announcement_1.id + 5}/')
        self.assertEqual(response.status_code, 404)

        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENTS_URL}asdf/')
        self.assertEqual(response.status_code, 404)

    def test_announcement_category_filter(self):
        response: HttpResponse = self.client.get(
            f'{self.ANNOUNCEMENTS_URL}?category=WORK_IS_LOOKING')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/announcements.html')

        announcements = response.context[0].get('announcements')
        self.assertEqual(announcements.count(), 1)
        self.assertEqual(announcements.first().category, Category.WORK_IS_LOOKING)
