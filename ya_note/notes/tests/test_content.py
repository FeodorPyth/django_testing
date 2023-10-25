from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


URL = {
    'list': reverse('notes:list'),
    'add': reverse('notes:add'),
    'edit': reverse('notes:edit', args=('note-slug',))
}


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст',
            slug='note-slug', author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_notes_list_for_dif_users(self):
        url = URL['list']
        users = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user_status, note_in_list in users:
            with self.subTest(user_status=user_status):
                response = user_status.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        urls = (
            (URL['add']),
            (URL['edit']),
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
