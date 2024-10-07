from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import Note  

class CreateNoteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('create_note')

    def test_create_note_success(self):
        response = self.client.post(self.url, {
            'content': 'This is a test note.',
            'visits': '5',
            'expire_at': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        })
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.first().content, 'This is a test note.')

        self.assertEqual(response.status_code, 302) 

    def test_create_note_missing_content(self):
        response = self.client.post(self.url, {
            'content': '',
            'visits': '5',
            'expire_at': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Content is required.')

    def test_create_note_missing_max_visits(self):
        response = self.client.post(self.url, {
            'content': 'This is a test note.',
            'visits': '',
            'expire_at': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Max visits is required.')

    def test_create_note_missing_expire_date(self):
        response = self.client.post(self.url, {
            'content': 'This is a test note.',
            'visits': '5',
            'expire_at': ''
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Expire date is required.')

    def test_create_note_expire_date_in_past(self):
        response = self.client.post(self.url, {
            'content': 'This is a test note.',
            'visits': '5',
            'expire_at': (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        })
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Expire date cannot be in the past.')

    def test_create_note_no_post_request(self):
        response = self.client.get(self.url) 
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'index.html') 

class GetNoteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('get_note', args=[1]) 

    def test_get_existing_note(self):
        note = Note.objects.create(
            content='Test note',
            remaining_views=3,
            expire_at=(timezone.now() + timedelta(days=1)).date()
        )
        response = self.client.get(reverse('get_note', args=[note.id]))
        
    
        self.assertContains(response, 'Test note')
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'note_created.html')

    def test_get_non_existing_note(self):
        non_existing_uuid = uuid.uuid4()
        response = self.client.get(reverse('get_note', args=[non_existing_uuid])) 
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The note has expired or no longer exists. Please create a new one.")
        self.assertRedirects(response, '/secret-note')

    def test_get_note_with_expired_views(self):
        note = Note.objects.create(
            content='Test note',
            remaining_views=0, 
            expire_at=(timezone.now() + timedelta(days=1)).date()
        )
        response = self.client.get(reverse('get_note', args=[note.id]))
        messages = list(get_messages(response.wsgi_request))
        
    
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The note has expired or no longer exists. Please create a new one.")
        self.assertRedirects(response, '/secret-note')

    def test_get_note_expired(self):
        note = Note.objects.create(
            content='Test note',
            remaining_views=5,
            expire_at=(timezone.now() - timedelta(days=1)).date() 
        )
        response = self.client.get(reverse('get_note', args=[note.id]))
        messages = list(get_messages(response.wsgi_request))
        
    
        self.assertEqual(Note.objects.count(), 0)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The note has expired or no longer exists. Please create a new one.")
        self.assertRedirects(response, '/secret-note')

    def test_get_note_decrement_remaining_views(self):
        note = Note.objects.create(
            content='Test note',
            remaining_views=5,
            expire_at=(timezone.now() + timedelta(days=1)).date()
        )
        response = self.client.get(reverse('get_note', args=[note.id]))
        
    
        note.refresh_from_db()
        self.assertEqual(note.remaining_views, 4)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'note_created.html')
