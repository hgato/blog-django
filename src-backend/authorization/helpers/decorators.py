from django.http import JsonResponse, HttpRequest

from authorization.models import User


def api_auth_demanded(func):
    """
    Decorator for view function that returns 403 error if user is not authenticated
    before calling view function
    """
    def wrapper(request: HttpRequest, *args, **kwargs):
        try:
            user = User.get_user_from_request(request)
            if not user:
                raise Exception('User not found')
            return func(request, user, *args, **kwargs)
        except Exception as error:
            return JsonResponse({'status': 'error', 'message': str(error)}, status=403)
    return wrapper
