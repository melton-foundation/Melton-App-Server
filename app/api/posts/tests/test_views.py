from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post, Tag
from authentication.models import Profile, ExpiringToken


class PostAPITest(APITestCase):
    EMAIL = 'test@email.com'
    NAME = 'test'
    IS_JUNIOR_FELLOW = True
    CAMPUS = 'University of the World'
    BATCH = 2020
    NUMBER = '99999999999'
    COUNTRY_CODE = '+91'

    def setUp(self):
        self.profile = Profile.objects.create(email=self.EMAIL, name=self.NAME,
                                              is_junior_fellow=self.IS_JUNIOR_FELLOW, campus=self.CAMPUS,
                                              batch=self.BATCH, number=self.NUMBER, country_code=self.COUNTRY_CODE)
        self.user = self.profile.user
        self.token = ExpiringToken.objects.get(user=self.user)

        self.posts = [
            {
                'title': 'First Post',
                'description': 'This is description for first post - description1',
                'content': 'This is content of first post',
                'tags': ['tag1', 'tag2'],
                'active': True
            },
            {
                'title': 'Second Post',
                'description': 'This is description for second post - description2',
                'content': 'This is conent of second post',
                'tags': ['tag2', 'tag3'],
                'active': True
            },
            {
                'title': 'Third Post',
                'description': 'This is description for third post - description3',
                'content': 'This is conent of third post',
                'tags': ['tag3', 'tag5'],
                'active': False
            }
        ]

        for post in self.posts:
            post_obj = Post.objects.create(title=post['title'], description=post['description'],
                                           content=post['content'], active=post['active'])
            post['id'] = post_obj.id
            post_obj.update_tags(post['tags'])

    def _build_url(self, *args, **kwargs):
        get = kwargs.pop('get', {})
        url = reverse(*args, **kwargs)
        if get:
            url += '?' + urlencode(get)
        return url

    def test_retrieve_post_list(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('posts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for post in response.data:
            self.assertSetEqual(set(['id', 'title', 'description', 'tags', 'created', 'updated']),
                                set(post.keys()))

    def test_retrieve_post(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('post', args=[self.posts[0]['id']])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSetEqual(set(['title', 'description', 'content', 'tags', 'created', 'updated']),
                            set(response.data.keys()))

    def test_cant_retrieve_inactive_post(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('post', args=[self.posts[2]['id']])
        # print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_posts_tag(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('posts', get={'search': 'tag2'})
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        for post in response.data:
            self.assertIn('tag2', post['tags'])

    def test_search_posts_title(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('posts', get={'search': 'first'})
        response = self.client.get(url)
        for post in response.data:
            self.assertIn('first', post['title'].lower())

    def test_search_posts_description(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('posts', get={'search': 'description1'})
        response = self.client.get(url)
        for post in response.data:
            self.assertIn('description1', post['description'].lower())
