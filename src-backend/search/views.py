from django.views.generic import TemplateView
from post.models import Post
from search.src.search import PostSearch
from tools.http.mixins import JsonMixin


class SearchView(TemplateView, JsonMixin):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', None)
        if not query:
            return self.respond_error_json({'message': 'No query provided'})

        search_object = PostSearch()
        result = search_object.run(query)
        posts = Post.objects.filter(pk__in=result)
        serialized_posts = [post.serialize() for post in posts]

        return self.respond_success_json({'posts': serialized_posts})
