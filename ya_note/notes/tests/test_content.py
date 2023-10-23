from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст',
            slug='note-slug', author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель')

    def test_notes_list_for_dif_users(self):
        url = reverse('notes:list')
        users = (
            (self.author, True),
            (self.reader, False),
        )
        for user_status, note_in_list in users:
            with self.subTest(user_status=user_status):
                self.client.force_login(user_status)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
