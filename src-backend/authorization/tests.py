import time
import jwt
from django.http import HttpRequest, JsonResponse
from django.test import TestCase

from authorization.helpers.decorators import api_auth_demanded
from authorization.models import User


class RedisConnectionMock:
    database = {}

    def get(self, key):
        return self.database[key]

    def set(self, key, value):
        self.database[key] = value

    def delete(self, key):
        del self.database[key]


User.redis_connection = RedisConnectionMock()


class CreatObjects:
    def create_user(self):
        user = User(first_name='first_name',
                    last_name='last_name',
                    email='email',
                    username='email')
        user.set_password('password')
        user.save()
        return user

    def make_jwt(self, user):
        timestamp = time.time() + User.JWT_TIMEOUT
        payload = {
            'email': user.email,
            'timestamp': timestamp
        }
        return jwt.encode(payload, User.DJANGO_JWT_SECRET, algorithm='HS256'), timestamp


class ApiAuthDemandedTests(TestCase, CreatObjects):
    def tearDown(self):
        User.redis_connection.database = {}

    def test_success(self):
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        decoded_jwt = encoded_jwt.decode('utf-8')
        request = HttpRequest()
        request.META = {'HTTP_AUTHORIZATION': decoded_jwt}
        User.redis_connection.database[encoded_jwt] = timestamp

        @api_auth_demanded
        def func(request, user):
            return user

        authenticated_user = func(request)
        self.assertEqual(user.email, authenticated_user.email, 'Wrong user returned')

    def test_error_no_jwt_in_redis(self):
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        decoded_jwt = encoded_jwt.decode('utf-8')
        request = HttpRequest()
        request.META = {'HTTP_AUTHORIZATION': decoded_jwt}

        @api_auth_demanded
        def func(request, user):
            return user

        result = func(request)

        self.assertIsInstance(result, JsonResponse, 'JsonResponse must be returned')

        self.assertEqual(403, result.status_code, 'Wrong response status code')


class UserModelTests(TestCase, CreatObjects):
    def tearDown(self):
        User.redis_connection.database = {}

    def test_get_current_user(self):
        """
        get_current_user must return authenticated user by jwt
        """
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        decoded_jwt = encoded_jwt.decode('utf-8')
        User.redis_connection.database[encoded_jwt] = timestamp
        authenticated_user = User.get_current_user(decoded_jwt)
        self.assertEqual(user.email, authenticated_user.email, 'Wrong user returned')

    def test_get_current_user_no_redis_entity(self):
        """
        get_current_user must raise error if no redis entity for user
        """
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        decoded_jwt = encoded_jwt.decode('utf-8')
        with self.assertRaises(Exception):
            User.get_current_user(decoded_jwt)

    def test_get_current_user_with_old_timestamp(self):
        """
        get_current_user must raise error if timestamp is timed out
        """
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        decoded_jwt = encoded_jwt.decode('utf-8')
        User.redis_connection.database[encoded_jwt] = timestamp - User.JWT_TIMEOUT - 1
        with self.assertRaises(Exception):
            User.get_current_user(decoded_jwt)

    def test_authenticate(self):
        """
        authenticate method must return user and jwt and store jwt in redis
        """
        expected_user = self.create_user()
        user, encoded_jwt = User.authenticate('email', 'password')
        expected_jwt = list(User.redis_connection.database.keys())[0]
        self.assertEqual(expected_user.email, user.email, 'Wrong user returned')
        self.assertEqual(expected_jwt, encoded_jwt.encode('utf-8'), 'Wrong jwt returned')

    def test_authenticate_wrong_password(self):
        """
        authenticate method must raise exception on wrong password
        """
        self.create_user()
        with self.assertRaises(Exception):
            User.authenticate('email', 'wrong_password')

    def test_authenticate_wrong_email(self):
        """
        authenticate method must raise exception on wrong email
        """
        self.create_user()
        with self.assertRaises(Exception):
            User.authenticate('wrong_email', 'password')

    def test_get_user_from_request(self):
        """
        get_user_from_request must return authenticated user from request
        """
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        decoded_jwt = encoded_jwt.decode('utf-8')
        request = HttpRequest()
        request.META = {'HTTP_AUTHORIZATION': decoded_jwt}
        User.redis_connection.database[encoded_jwt] = timestamp
        authenticated_user = User.get_user_from_request(request)
        self.assertEqual(user.email, authenticated_user.email, 'Wrong user returned')

    def test_get_user_from_request_without_header(self):
        """
        get_user_from_request must raise Exception on no Authorization header
        """
        user = self.create_user()
        encoded_jwt, timestamp = self.make_jwt(user)
        request = HttpRequest()
        User.redis_connection.database[encoded_jwt] = timestamp
        with self.assertRaises(Exception):
            User.get_user_from_request(request)
