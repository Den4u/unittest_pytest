from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Reader')
        cls.author = User.objects.create(username='Author')
        cls.note = Note.objects.create(title='Заголовок', text='TEKCT',
                                       author=cls.author, slug='slug')

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_availability_for_auth_user(self):
        urls = (
            'notes:list', 'notes:add', 'notes:success'
        )
        self.client.force_login(self.author)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:detail', (self.note.id,)),
            ('notes:edit', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_note_add_delete_for_author(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            ('notes:detail', (self.SLUG,)),
            ('notes:delete', (self.SLUG,)),
            ('notes:edit', (self.SLUG,))
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user.username, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
