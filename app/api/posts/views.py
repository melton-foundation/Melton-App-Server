from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import filters
from authentication import authentication
from posts.models import Post
from posts.serializers import PostListSerializer, PostSerializer


class PostView(ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = []
    search_fields = ["title", "description", "tags__tag"]
    filter_backends = (filters.SearchFilter,)
    queryset = Post.objects.filter(active=True)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer
