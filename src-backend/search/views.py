from django.views.generic import TemplateView
from post.models import Post
from search.src.search import PostSearch
from tools.http.mixins import JsonMixin


class SearchView(TemplateView, JsonMixin):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        size = request.GET.get('limit', 10)
        from_ = request.GET.get('offset', 0)

        search_object = PostSearch()
        search_object.size = size
        search_object.from_ = from_
        result, total = search_object.run(query)
        posts = Post.objects.filter(pk__in=result)
        serialized_posts = [post.serialize() for post in posts]

        return self.respond_success_json({'posts': serialized_posts, 'total_posts': total})
