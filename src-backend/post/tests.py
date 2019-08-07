import json

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse

from authorization.models import User
from post.models import Post, OldPost


class CreateEntities:
    EMAIL = 'email'
    PASSWORD = 'password'

    def _create_user(self, email=None):
        email = email if email else self.EMAIL
        user = User(first_name='first_name',
                    last_name='last_name',
                    email=email,
                    username=email)
        user.set_password(self.PASSWORD)
        user.save()
        return user

    def _create_post_name_text(self, user):
        text = 'text'
        name = 'name'
        post = Post(text=text,
                    name=name,
                    author=user)
        post.save()
        return post, name, text


class PostModelTests(TestCase, CreateEntities):
    def test_check_new_text_false(self):
        """
        check_new_text method must return false for new post
        """
        post = Post()
        self.assertFalse(post._check_new_text(), 'Method check_new_text must return true')

    def test_check_new_text_true(self):
        """
        check_new_text method must return true if new text or name provided
        """
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        post.old_text = 'old_text'
        post.old_name = 'old_name'
        self.assertTrue(post._check_new_text(), 'Method check_new_text must return true')

    def test_save_old_version_error(self):
        """
        save_old_version method must not save old version of post
        for new post, it must raise exception instead
        """
        text = 'text'
        name = 'name'
        post = Post(text=text,
                    name=name)

        with self.assertRaises(Exception):
            post._save_old_version()

    def test_save_old_version_success(self):
        """
        save_old_version method must save old version of post
        for updating old post
        """
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        new_text = 'new_text'
        new_name = 'new_name'
        post.old_text = text
        post.old_name = name
        post.old_author = post.author
        post.old_date = post.date
        post.text = new_text
        post.name = new_name

        post._save_old_version()
        old_post = OldPost.objects.get(name=name, text=text)
        self.assertIsNotNone(old_post, 'Method save_old_version must create old version')

    def test_check_cannot_create_old_version_true(self):
        """
        Method check_cannot_create_old_version must return false
        if old properties not set
        """
        post = Post()
        self.assertTrue(post._check_cannot_create_old_version(),
                        'Method check_cannot_create_old_version must return true')

    def test_check_cannot_create_old_version_false(self):
        """
        Method check_cannot_create_old_version must return true
        if old properties set
        """
        post = Post()
        post.old_date = 'set'
        post.old_name = 'set'
        post.old_text = 'set'
        post.old_author = 'set'

        self.assertFalse(post._check_cannot_create_old_version(),
                         'Method check_cannot_create_old_version must return false')

    def test_update_must_save_old_and_new_version(self):
        """
        Method update must update post and create old_post
        """
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        new_text = 'new_text'
        new_name = 'new_name'
        post.update(new_name, new_text)

        expected_post = Post.objects.get(pk=post.pk)
        self.assertEqual(expected_post.name, new_name, 'New name must be saved')
        self.assertEqual(expected_post.text, new_text, 'New text must be saved')

        expected_old_post = OldPost.objects.get(name=name, text=text)
        self.assertIsNotNone(expected_old_post, 'Old post must be saved')

    def test_update_saves_new_date(self):
        """
        Only method update must save new date
        """
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        date1 = post.date

        post.text = 'text1'
        post.name = 'name1'
        post.save()
        date2 = post.date

        post.update(name='name2', text='text')
        date3 = post.date

        self.assertEqual(date1, date2, 'Save method must not update date')
        self.assertNotEqual(date1, date3, 'Update method must update date')

    def test_make_delete(self):
        """
        Method make_delete must only set DL status
        """
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        self.assertEqual(Post.PENDING, post.status, "Default method must be Pending")
        post.make_delete()
        self.assertEqual(Post.DELETED, post.status, 'Method make_delete should set Deleted status')

    def test_serialize(self):
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        expected = {
            'id': post.pk,
            'text': post.text,
            'name': post.name,
            'author': {
                'first_name': post.author.first_name,
                'last_name': post.author.last_name,
                'id': post.author.id,
            },
            'date': post.date,
        }
        self.assertEqual(expected, post.serialize(), 'Wrong dictionary returned')


class PostViewTest(TestCase, CreateEntities):
    def test_post_live_cycle(self):
        self._create_user()
        _, jwt_header = User.authenticate(self.EMAIL, self.PASSWORD)

        post_pk = self.create_post_success(jwt_header).pk
        self.get_post_success(post_pk)

        self.update_post_success(post_pk, jwt_header)
        self.get_post_success(post_pk)

        self.delete_post_success(post_pk, jwt_header)
        self.get_post_error(post_pk)

    def test_auth_needed(self):
        self.create_post_auth_error()

        user = self._create_user()
        post, name, text = self._create_post_name_text(user)
        post.status = Post.ACTIVE
        post.save()

        self.update_post_auth_error(post.pk)
        self.delete_post_auth_error(post.pk)

    def test_other_user_auth(self):
        self._create_user()
        _, jwt_header = User.authenticate(self.EMAIL, self.PASSWORD)

        post_user = self._create_user(email='alternative_email')
        post, name, text = self._create_post_name_text(post_user)
        post.status = Post.ACTIVE
        post.save()

        self.update_post_wrong_user(post.pk, jwt_header)
        self.delete_post_wrong_user(post.pk, jwt_header)

    def create_post_success(self, jwt_header):
        request_data = {
            "name": "post_name",
            "text": "post_text"
        }
        header = {'HTTP_AUTHORIZATION': jwt_header}
        response = self.client.put(reverse('posts'), json.dumps(request_data),
                                   content_type="application/json", **header)
        self.assertContains(response, 'ok', status_code=200)
        post = Post.objects.get(name=request_data['name'],
                                text=request_data['text'])
        self.assertIsNotNone(post)
        return post

    def create_post_auth_error(self):
        request_data = {
            "name": "post_name",
            "text": "post_text"
        }
        response = self.client.put(reverse('posts'), json.dumps(request_data),
                                   content_type="application/json")
        self.assertContains(response, 'error', status_code=403)
        with self.assertRaises(ObjectDoesNotExist):
            Post.objects.get(name=request_data['name'],
                             text=request_data['text'])

    def get_post_success(self, post_pk):
        post = Post.objects.get(pk=post_pk)
        response = self.client.get(reverse('post', kwargs={'post_id': post.pk}))
        self.assertContains(response, 'ok', status_code=200)
        self.assertContains(response, post.name, status_code=200)
        self.assertContains(response, post.text, status_code=200)

    def get_post_error(self, post_pk):
        response = self.client.get(reverse('post', kwargs={'post_id': post_pk}))
        self.assertContains(response, 'error', status_code=400)

    def update_post_success(self, post_pk, jwt_header):
        request_data = {
            "name": "new_post_name",
            "text": "new_post_text"
        }
        header = {'HTTP_AUTHORIZATION': jwt_header}
        response = self.client.patch(reverse('post', kwargs={'post_id': post_pk}),
                                     json.dumps(request_data),
                                     content_type="application/json",
                                     **header)
        self.assertContains(response, 'ok', status_code=200)
        self.assertContains(response, request_data['name'], status_code=200)
        self.assertContains(response, request_data['text'], status_code=200)
        post = Post.objects.get(pk=post_pk)
        self.assertEqual(request_data['name'], post.name, 'New name must be set')
        self.assertEqual(request_data['text'], post.text, 'New text must be set')

    def update_post_auth_error(self, post_pk):
        post = Post.objects.get(pk=post_pk)
        request_data = {
            "name": "new_post_name",
            "text": "new_post_text"
        }
        response = self.client.patch(reverse('post', kwargs={'post_id': post_pk}),
                                     json.dumps(request_data),
                                     content_type="application/json")
        self.assertContains(response, 'error', status_code=403)
        self.assertNotEqual(request_data['name'], post.name, 'New name must not be set')
        self.assertNotEqual(request_data['text'], post.text, 'New text must not be set')

    def update_post_wrong_user(self, post_pk, jwt_header):
        post = Post.objects.get(pk=post_pk)
        request_data = {
            "name": "new_post_name",
            "text": "new_post_text"
        }
        header = {'HTTP_AUTHORIZATION': jwt_header}
        response = self.client.patch(reverse('post', kwargs={'post_id': post_pk}),
                                     json.dumps(request_data),
                                     content_type="application/json",
                                     **header)
        self.assertContains(response, 'error', status_code=400)
        self.assertNotEqual(request_data['name'], post.name, 'New name must not be set')
        self.assertNotEqual(request_data['text'], post.text, 'New text must not be set')

    def delete_post_success(self, post_pk, jwt_header):
        header = {'HTTP_AUTHORIZATION': jwt_header}
        response = self.client.delete(reverse('post', kwargs={'post_id': post_pk}),
                                      **header)
        self.assertContains(response, 'ok', status_code=200)
        post = Post.objects.get(pk=post_pk)
        self.assertEqual(post.DELETED, post.status, 'Status DL not set')

    def delete_post_auth_error(self, post_pk):
        response = self.client.delete(reverse('post', kwargs={'post_id': post_pk}))
        self.assertContains(response, 'error', status_code=403)
        post = Post.objects.get(pk=post_pk)
        self.assertEqual(post.ACTIVE, post.status, 'Status DL not set')

    def delete_post_wrong_user(self, post_pk, jwt_header):
        header = {'HTTP_AUTHORIZATION': jwt_header}
        response = self.client.delete(reverse('post', kwargs={'post_id': post_pk}),
                                      **header)
        self.assertContains(response, 'error', status_code=400)
        post = Post.objects.get(pk=post_pk)
        self.assertEqual(post.ACTIVE, post.status, 'Status DL not set')


class PostListViewTest(TestCase):
    def test_list(self):
        (user1, user2,
         post_us1_ac, post_us1_pd, post_us1_dl,
         post_us2_ac, post_us2_pd, post_us2_dl) = self.create_users_and_posts()

        response = self.client.get(reverse('posts_list'))
        self.assert_contains_name(response, [post_us1_ac, post_us2_ac, ])
        self.assert_not_contains_name(response, [post_us1_pd, post_us1_dl,
                                                 post_us2_pd, post_us2_dl, ])

    def test_author_list(self):
        (user1, user2,
         post_us1_ac, post_us1_pd, post_us1_dl,
         post_us2_ac, post_us2_pd, post_us2_dl) = self.create_users_and_posts()

        response = self.client.get(reverse('posts_list') + '?author={}'.format(user1.pk))
        self.assert_contains_name(response, [post_us1_ac, ])
        self.assert_not_contains_name(response, [post_us2_ac, post_us1_pd, post_us1_dl,
                                                 post_us2_pd, post_us2_dl, ])

    def test_list_limit_offset(self):
        (user1, user2,
         post_us1_ac, post_us1_pd, post_us1_dl,
         post_us2_ac, post_us2_pd, post_us2_dl) = self.create_users_and_posts()

        response = self.client.get(reverse('posts_list') + '?limit=1&offset=0')
        self.assert_contains_name(response, [post_us2_ac, ])
        self.assert_not_contains_name(response, [post_us1_ac, post_us1_pd, post_us1_dl,
                                                 post_us2_pd, post_us2_dl, ])

        response = self.client.get(reverse('posts_list') + '?limit=1&offset=1')
        self.assert_contains_name(response, [post_us1_ac, ])
        self.assert_not_contains_name(response, [post_us2_ac, post_us1_pd, post_us1_dl,
                                                 post_us2_pd, post_us2_dl, ])

    def assert_contains_name(self, response, posts):
        for post in posts:
            self.assertContains(response, '"name": "{}"'.format(post.name))

    def assert_not_contains_name(self, response, posts):
        for post in posts:
            self.assertNotContains(response, '"name": "{}"'.format(post.name))

    def create_users_and_posts(self):
        user1 = User(first_name='first_name',
                     last_name='last_name',
                     email='email1',
                     username='email1')
        user1.set_password('password')
        user1.save()

        user2 = User(first_name='first_name',
                     last_name='last_name',
                     email='email2',
                     username='email2')
        user2.set_password('password')
        user2.save()

        post_us1_ac = Post.objects.create(name='name1',
                                          text='text',
                                          author=user1,
                                          status=Post.ACTIVE)
        post_us1_pd = Post.objects.create(name='name2',
                                          text='text',
                                          author=user1,
                                          status=Post.PENDING)
        post_us1_dl = Post.objects.create(name='name3',
                                          text='text',
                                          author=user1,
                                          status=Post.DELETED)

        post_us2_ac = Post.objects.create(name='name4',
                                          text='text',
                                          author=user2,
                                          status=Post.ACTIVE)
        post_us2_pd = Post.objects.create(name='name5',
                                          text='text',
                                          author=user2,
                                          status=Post.PENDING)
        post_us2_dl = Post.objects.create(name='name6',
                                          text='text',
                                          author=user2,
                                          status=Post.DELETED)
        return (user1, user2,
                post_us1_ac, post_us1_pd, post_us1_dl,
                post_us2_ac, post_us2_pd, post_us2_dl)
