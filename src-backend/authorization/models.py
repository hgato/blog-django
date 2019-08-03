from __future__ import annotations
import os
import time
import jwt
import redis
from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest


class User(AbstractUser):
    JWT_TIMEOUT = 24 * 3600
    DJANGO_JWT_SECRET = os.environ.get('DJANGO_JWT_SECRET')

    @classmethod
    def get_current_user(cls, encoded_jwt: str) -> User:
        redis_connection = redis.Redis(host='redis', port=6379, db=0)
        timestamp = redis_connection.get(encoded_jwt.encode('utf-8'))

        if not timestamp:
            raise Exception('User unauthenticated')

        if float(timestamp) < time.time():
            raise Exception('Authentication timed out')

        payload = jwt.decode(encoded_jwt, cls.DJANGO_JWT_SECRET, algorithm=['HS256'])

        try:
            user = User.objects.get(username=payload['email'])
            if user:
                return user
        except:
            pass

        raise Exception('No such user')

    @classmethod
    def authenticate(cls, email: str, password: str):
        user = authenticate(username=email, password=password)
        if not user:
            raise Exception('No such user')

        timestamp = time.time() + cls.JWT_TIMEOUT

        payload = {
            'email': user.email,
            'timestamp': timestamp
        }
        encoded_jwt = jwt.encode(payload, cls.DJANGO_JWT_SECRET, algorithm='HS256')

        redis_connection = redis.Redis(host='redis', port=6379, db=0)
        redis_connection.set(encoded_jwt, timestamp)

        return user, encoded_jwt.decode('utf-8')

    @classmethod
    def get_user_from_request(cls, request: HttpRequest):
        jwt = request.headers.get('Authorization')
        if not jwt:
            jwt = request.headers.get('HTTP_AUTHORIZATION')
        return cls.get_current_user(jwt)

    def serialize(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'password': self.password,
            'id': self.id,
        }
