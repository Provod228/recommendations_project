from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Content
from .serializers import ContentSerializer


class TestView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'main.html'
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = Content.objects.all()
        return Response({"content": ContentSerializer(content, many=True).data})
