from django.http import JsonResponse

from authorization.models import User


def api_auth_demanded(func):
    def wrapper(request, *args, **kwargs):
        try:
            user = User.get_user_from_request(request)
            if not user:
                raise Exception('User not found')
            return func(request, user, *args, **kwargs)
        except Exception as error:
            return JsonResponse({'status': 'error', 'message': str(error)})
    return wrapper
