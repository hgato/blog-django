from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from post.models import Post
from search.src.search import PostSearch


class SearchView(TemplateView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', None)
        if not query:
            return JsonResponse({'status': 'error', 'message': 'No query provided'}, status=400)
        search_object = PostSearch()
        result = search_object.run(query)
        posts = Post.objects.filter(pk__in=result)
        serialized_posts = [post.serialize() for post in posts]
        response = {
            'posts': serialized_posts
        }
        return JsonResponse(response)
