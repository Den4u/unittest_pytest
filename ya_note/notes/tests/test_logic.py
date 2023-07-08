from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestNoteCreation(TestCase):
    ADD_NOTE_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.form_data = {'title': 'Form title',
                         'text': 'Form text',
                         'slug': 'form-slug'}

    def test_anonymous_user_cant_create_note(self):
        expected_count = Note.objects.count()
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.ADD_NOTE_URL}'
        self.assertRedirects(response, expected_url)
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_count)

    def test_user_can_create_note(self):
        expected_count = Note.objects.count() + 1
        self.client.force_login(self.author)
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_count)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_slug_must_be_unique(self):
        expected_count = Note.objects.count() + 1
        self.client.force_login(self.author)
        self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        new_count = Note.objects.count()
        response = self.client.post(self.ADD_NOTE_URL, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertEqual(new_count, expected_count)
        self.assertFormError(response, form='form',
                             field='slug', errors=warning)

    def test_empty_slug(self):
        expected_count = Note.objects.count() + 1
        self.client.force_login(self.author)
        del self.form_data['slug']
        response = self.client.post(self.ADD_NOTE_URL,
                                    data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_count)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.get()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Тайтл заметки'
    NEW_NOTE_TITLE = 'Обновлённый тайтл'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='note-slug',
            author=cls.author,
        )
        cls.edit_note_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_note_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT}

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_note_url, self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_note_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get()
        self.assertIsNotNone(note_from_db)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        expected_count = Note.objects.count() - 1
        response = self.author_client.post(self.delete_note_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), expected_count)

    def test_other_user_cant_delete_note(self):
        expected_count = Note.objects.count()
        response = self.reader_client.post(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), expected_count)
