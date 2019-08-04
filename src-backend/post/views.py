from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import json

from authorization.models import User
from post.models import Post
from tools.http.mixins import JsonMixin


class PostView(TemplateView, JsonMixin):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PostView, self).dispatch(request, *args, **kwargs)

    def check_post_belongs_to_user(self, post, user):
        if post.author.pk != user.pk:
            raise Exception('Post does not belong to user')

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
            body = self.process_body(request, ['text', 'name', ])
        except Exception as error:
            return self.respond_error_json(error)

        post = Post(text=body['text'],
                    name=body['name'],
                    author=user,
                    status=Post.ACTIVE)
        post.save()
        return self.respond_success_json({'post': post.serialize()})

    def patch(self, request, post_id, *args, **kwargs):
        try:
            user = User.get_user_from_request(request)
            body = self.process_body(request)
            post = Post.objects.get(pk=post_id)
            self.check_post_belongs_to_user(post, user)
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
            self.check_post_belongs_to_user(post, user)
        except Exception as error:
            return self.respond_error_json(error)

        post.make_delete()
        return self.respond_success_json()


class PostListView(TemplateView, JsonMixin):
    def get_proper_posts(self, limit, offset, author):
        if author:
            return Post.objects.filter(author=int(author)).order_by('-pk')[offset: offset + limit]
        return Post.objects.order_by('-pk')[offset: offset + limit]

    def get(self, request, *args, **kwargs):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        author = request.GET.get('author', None)

        posts = self.get_proper_posts(limit, offset, author)
        serialized_posts = [post.serialize() for post in posts]
        total = Post.objects.count()
        return self.respond_success_json({'posts': serialized_posts, 'total_posts': total})
