from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from musicapp.models import Song, Playlist, Favourite, Recent
from musicapp.views import get_last_played_song
from musicapp.predict import predict_gen


class MusicAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.song1 = Song.objects.create(
            name='Test Song 1',
            album='Test Album',
            language='Hindi',
            singer='Singer A',
            year=2020
        )
        self.song2 = Song.objects.create(
            name='Test Song 2',
            album='Test Album 2',
            language='English',
            singer='Singer B',
            year=2021
        )
        self.client = Client()

    def test_anonymous_pages(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('all_songs'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('hindi_songs'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('english_songs'))
        self.assertEqual(response.status_code, 200)

    def test_protected_pages_redirect_anonymous(self):
        protected_routes = ['recent', 'mymusic', 'playlist', 'favourite', 'upload']
        for route in protected_routes:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 302)

    def test_authenticated_pages(self):
        self.client.force_login(self.user)
        routes = ['index', 'all_songs', 'hindi_songs', 'english_songs', 'recent', 'mymusic', 'playlist', 'favourite', 'upload']
        for route in routes:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200)

    def test_get_last_played_song_fallback(self):
        song = get_last_played_song()
        self.assertIsNotNone(song)
        self.assertEqual(song.id, self.song1.id)

    def test_favourite_flow(self):
        self.client.force_login(self.user)
        # Add favorite
        response = self.client.post(reverse('detail', args=[self.song1.id]), {'add-fav': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Favourite.objects.filter(user=self.user, song=self.song1, is_fav=True).exists())

        # Remove favorite
        response = self.client.post(reverse('detail', args=[self.song1.id]), {'rm-fav': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Favourite.objects.filter(user=self.user, song=self.song1).exists())

    def test_playlist_flow(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('detail', args=[self.song1.id]), {'playlist': 'My Playlist'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Playlist.objects.filter(user=self.user, playlist_name='My Playlist', song=self.song1).exists())

        response = self.client.get(reverse('playlist_songs', args=['My Playlist']))
        self.assertEqual(response.status_code, 200)

    def test_predict_gen(self):
        dummy_meta = [100.0, 0.3, 0.1, 2000.0, 2000.0, 4000.0, 0.1] + [0.0] * 20
        genre = predict_gen(dummy_meta)
        self.assertIsInstance(genre, str)
