from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


URL = {
    'list': reverse('notes:list'),
    'add': reverse('notes:add'),
    'success': reverse('notes:success'),
    'login': reverse('users:login'),
    'edit': reverse('notes:edit', args=('note-slug',)),
    'delete': reverse('notes:delete', args=('note-slug',))
}


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        expected_count = Note.objects.count() + 1
        url = URL['add']
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, URL['success'])
        after_operation_count = Note.objects.count()
        self.assertEqual(after_operation_count, expected_count)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        before_operation_count = Note.objects.count()
        url = URL['add']
        response = self.client.post(url, data=self.form_data)
        after_operation_count = Note.objects.count()
        login_url = URL['login']
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(after_operation_count, before_operation_count)

    def test_empty_slug(self):
        expected_count = Note.objects.count() + 1
        url = URL['add']
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, URL['success'])
        after_operation_count = Note.objects.count()
        self.assertEqual(after_operation_count, expected_count)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestSlugLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст',
            slug='note-slug', author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_not_unique_slug(self):
        before_operation_count = Note.objects.count()
        url = URL['add']
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        after_operation_count = Note.objects.count()
        self.assertEqual(after_operation_count, before_operation_count)

    def test_author_can_edit_note(self):
        url = URL['edit']
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, URL['success'])
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        url = URL['edit']
        response = self.reader_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        expected_count = Note.objects.count() - 1
        url = URL['delete']
        response = self.author_client.post(url)
        after_operation_count = Note.objects.count()
        self.assertRedirects(response, URL['success'])
        self.assertEqual(after_operation_count, expected_count)

    def test_other_user_cant_delete_note(self):
        before_operation_count = Note.objects.count()
        url = URL['delete']
        response = self.reader_client.post(url)
        after_operation_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(after_operation_count, before_operation_count)
