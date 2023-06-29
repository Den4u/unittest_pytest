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

    def test_notes_list_for_different_users(self):
        users_notes = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, note_in_list in users_notes:
            self.client.force_login(user)
            with self.subTest(user=user.username, note_in_list=note_in_list):
                response = self.client.get(url)
                note_in_object_list = self.note in response.context[
                    'object_list']
                self.assertEqual(note_in_object_list, note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
