from django.core.validators import validate_email
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from authorization.helpers.decorators import api_auth_demanded
from authorization.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tools.http.mixins import JsonMixin


class UserView(TemplateView, JsonMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UserView, self).dispatch(request, *args, **kwargs)

    def check_old_user_exists(self, body):
        old_user = None
        try:
            old_user = User.objects.get(username=body['email'])
        except:
            pass
        if old_user:
            raise Exception('User already exists')

    def create_new_user(self, body):
        user = User(first_name=body['first_name'],
                    last_name=body['last_name'],
                    email=body['email'],
                    username=body['email'])
        user.set_password(body['password'])
        user.save()

    def put(self, request, *args, **kwargs):
        try:
            body = self.process_body(request, ['first_name', 'last_name', 'email', 'password', ])
            validate_email(body.get('email'))
        except Exception as error:
            return self.respond_error_json(error, status=400)

        try:
            self.check_old_user_exists(body)
        except Exception as error:
            return self.respond_error_json(error, status=409)

        self.create_new_user(body)
        return self.respond_success_json(status=201)

    def post(self, request, *args, **kwargs):
        try:
            body = self.process_body(request, ['email', 'password', ])
            user, encoded_jwt = User.authenticate(body['email'], body['password'])
            return self.respond_success_json({'jwt': encoded_jwt, 'user': user.serialize()})
        except Exception as error:
            return self.respond_error_json(error, status=403)

    @method_decorator(api_auth_demanded)
    def delete(self, request, user, *args, **kwargs):
        try:
            user.delete()
            return self.respond_success_json()
        except Exception as error:
            return self.respond_error_json(error, status=403)


def respond_200(payload: dict = None):
    if not payload:
        payload = {}
    payload['status'] = 'ok'
    return JsonResponse(payload, status=200)


@csrf_exempt
@api_auth_demanded
def check(request, user):
    return respond_200({'email': user.email})


@csrf_exempt
@api_auth_demanded
def logout(request, user):
    user.unauthenticate(request.headers['Authorization'])
    return respond_200()
