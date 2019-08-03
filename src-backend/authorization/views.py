from authorization.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def respond_403(error: Exception):
    response = {
        'status': 'error',
        'message': str(error)
    }
    return JsonResponse(response, status=403)


def respond_200(payload: dict):
    payload['status'] = 'ok'
    return JsonResponse(payload, status=200)


def create_user(request):
    body = json.loads(request.body)
    try:
        old_user = User.objects.get(username=body['email'])
        if old_user:
            response = {
                'status': 'error',
                'message': 'User already exists'
            }
            return JsonResponse(response, status=409)
    except:
        pass

    user = User(first_name=body['first_name'],
                last_name=body['last_name'],
                email=body['email'],
                username=body['email'])
    user.set_password(body['password'])
    user.save()
    response = {
        'status': 'ok'
    }
    return JsonResponse(response, status=201)


def authenticate_user(request):
    body = json.loads(request.body)
    try:
        user, encoded_jwt = User.authenticate(body['email'], body['password'])
        return respond_200({'jwt': encoded_jwt, 'user': user.serialize()})
    except Exception as error:
        return respond_403(error)


def update_user(request):
    body = json.loads(request.body)
    user = User.get_user_from_request(request)
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
    return respond_200({})


def delete_user(request):
    try:
        user = User.get_user_from_request(request)
        user.delete()
        return respond_200({})
    except Exception as error:
        return respond_403(error)


def get_user(request):
    pass


@csrf_exempt
def user(request):
    if request.method == 'PUT':
        return create_user(request)
    if request.method == 'POST':
        return authenticate_user(request)
    if request.method == 'PATCH':
        return update_user(request)
    if request.method == 'DELETE':
        return delete_user(request)
    if request.method == 'GET':
        return get_user(request)


@csrf_exempt
def check(request):
    try:
        user = User.get_user_from_request(request)
        return respond_200({'email': user.email})

    except Exception as error:
        return respond_403(error)
