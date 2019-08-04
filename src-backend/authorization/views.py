from django.core.validators import validate_email
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from authorization.helpers.decorators import api_auth_demanded
from authorization.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from tools.http.mixins import JsonMixin


class UserView(TemplateView, JsonMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UserView, self).dispatch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        body = json.loads(request.body)
        try:
            old_user = None
            try:
                old_user = User.objects.get(username=body['email'])
            except:
                pass
            if old_user:
                raise Exception('User already exists')
        except Exception as error:
            return self.respond_error_json(error, status=409)

        try:
            validate_email(body.get('email'))
        except Exception as error:
            return self.respond_error_json(error, status=400)

        user = User(first_name=body['first_name'],
                    last_name=body['last_name'],
                    email=body['email'],
                    username=body['email'])
        user.set_password(body['password'])
        user.save()
        return self.respond_success_json(status=201)

    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        try:
            user, encoded_jwt = User.authenticate(body['email'], body['password'])
            return self.respond_success_json({'jwt': encoded_jwt, 'user': user.serialize()})
        except Exception as error:
            return self.respond_error_json(error, status=403)

    @method_decorator(api_auth_demanded)
    def patch(self, request, user, *args, **kwargs):
        body = json.loads(request.body)
        first_name = body.get('first_name', None)
        last_name = body.get('last_name', None)
        save = False
        if first_name:
            user.first_name = first_name
            save = True
        if last_name:
            user.last_name = last_name
            save = True
        if save:
            user.save()
        return self.respond_success_json()

    @method_decorator(api_auth_demanded)
    def delete_user(self, request, user, *args, **kwargs):
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
