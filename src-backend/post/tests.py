from django.test import TestCase

from authorization.models import User
from post.models import Post, OldPost


class PostModelTests(TestCase):
    def test_check_new_text_false(self):
        """
        check_new_text method must return false for new post
        """
        post = Post()
        self.assertFalse(post.check_new_text(), 'Method check_new_text must return true')

    def test_check_new_text_true(self):
        """
        check_new_text method must return true if new text or name provided
        """
        user = self._create_user()
        post, name, text = self._create_post_name_text(user)

        post.old_text = 'old_text'
        post.old_name = 'old_name'
        self.assertTrue(post.check_new_text(), 'Method check_new_text must return true')

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
            post.save_old_version()

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

        post.save_old_version()
        old_post = OldPost.objects.get(name=name, text=text)
        self.assertIsNotNone(old_post, 'Method save_old_version must create old version')

    def test_check_cannot_create_old_version_true(self):
        """
        Method check_cannot_create_old_version must return false
        if old properties not set
        """
        post = Post()
        self.assertTrue(post.check_cannot_create_old_version(),
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

        self.assertFalse(post.check_cannot_create_old_version(),
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

    def _create_user(self):
        user = User(first_name='first_name',
                    last_name='last_name',
                    email='email',
                    username='email',
                    password='password')
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

