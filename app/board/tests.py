from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponse

from board.models import Category, Announcement
from users.views import LogInView
from board.views import AnnouncementDashboardView, AnnouncementEditView


class BoardTest(TestCase):

    ANNOUNCEMENT_DASHBOARD_URL = reverse(AnnouncementDashboardView.name)
    ANNOUNCEMENT_EDIT_URL = reverse(AnnouncementEditView.name)
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

        self.client.logout()
        response: HttpResponse = self.client.get(self.ANNOUNCEMENT_DASHBOARD_URL)
        self.assertRedirects(response,
                             f'{self.LOGIN_URL}?next={self.ANNOUNCEMENT_DASHBOARD_URL}')

    def test_get_new_announcement(self):
        response: HttpResponse = self.client.get(self.ANNOUNCEMENT_EDIT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/announcement_edit.html')
