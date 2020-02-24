from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from blogs.filters import BlogFilter
from blogs.models import Blog
from blogs.serializers import BlogSerializer


class BlogViewSet(ViewSet):
    def list(self, request):
        queryset = Blog.objects.all()
        queryset = BlogFilter(data=request.GET, queryset=queryset, request=request).qs
        serializer = BlogSerializer(queryset, many=True)
        return Response(serializer.data)
