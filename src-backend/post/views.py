from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import json

from authorization.models import User
from post.models import Post  # , PostGroup


class JsonMixin:
    def clean_body(self, request):
        return json.loads(request.body)

    def check_body(self, body: dict, expected_parameters: list):
        error_list = []
        for parameter in expected_parameters:
            if parameter not in body:
                error_list.append(parameter)
        if error_list:
            raise Exception('Request demands following parameters: ' + ', '.join(error_list))

    def process_body(self, request, expected_parameters=None):
        body = self.clean_body(request)
        if expected_parameters:
            self.check_body(body, expected_parameters)
        return body

    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        return context

    def respond_error_json(self, error):
        response = {
            'status': 'error',
            'message': str(error),
        }
        return self.render_to_json_response(response, status=400)

    def respond_success_json(self, payload=None):
        if not payload:
            payload = {}
        payload['status'] = 'ok'
        return self.render_to_json_response(payload)


class PostView(TemplateView, JsonMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PostView, self).dispatch(request, *args, **kwargs)

    def check_post_reachable(self, post, request):
        if post.status == Post.DELETED:
            raise Exception('Post not found')

        if post.status != Post.ACTIVE:
            user = None
            try:
                user = User.get_user_from_request(request)
            except:
                pass
            if not user or not user.pk == post.author.pk:
                raise Exception('Post not found')

    def get(self, request, post_id, *args, **kwargs):
        try:
            post = Post.objects.get(pk=post_id)
            self.check_post_reachable(post, request)
        except Exception as error:
            return self.respond_error_json(error)

        return self.respond_success_json({'post': post.serialize()})

    def put(self, request, *args, **kwargs):
        try:
            user = User.get_user_from_request(request)
            body = self.process_body(request, ['text', 'name', ])  # 'post_group'])
        except Exception as error:
            return self.respond_error_json(error)

        # group = PostGroup.objects.get(pk=body['post_group'])
        post = Post(text=body['text'],
                    name=body['name'],
                    author=user,
                    status=Post.ACTIVE)
                    # post_group=group)
        post.save()
        return self.respond_success_json({'post': post.serialize()})

    def patch(self, request, post_id, *args, **kwargs):
        try:
            user = User.get_user_from_request(request)
            body = self.process_body(request)
            post = Post.objects.get(pk=post_id)
            if post.author.pk != user.pk:
                raise Exception('Post does not belong to user')
        except Exception as error:
            return self.respond_error_json(error)

        text = body.get('text', None)
        name = body.get('name', None)
        post.update(text=text, name=name)
        return self.respond_success_json({'post': post.serialize()})

    def delete(self, request, post_id, *args, **kwargs):
        try:
            user = User.get_user_from_request(request)
            post = Post.objects.get(pk=post_id)
            if post.author.pk != user.pk:
                raise Exception('Post does not belong to user')
        except Exception as error:
            return self.respond_error_json(error)

        post.make_delete()
        return self.respond_success_json()


class PostListView(TemplateView, JsonMixin):
    def get(self, request, *args, **kwargs):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))

        posts = Post.objects.order_by('-pk')[offset: offset + limit]
        serialized_posts = [post.serialize() for post in posts]
        total = Post.objects.count()

        return self.respond_success_json({'posts': serialized_posts, 'total_posts': total})

# class PostGroupView(TemplateView, JsonMixin):
#     pass
