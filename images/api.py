from rest_framework import status, permissions, generics, parsers
from rest_framework.response import Response
from images.models import Image
from images.serializers import ImageUploadSerializer
from rest_framework import viewsets

class ImageUploadListView(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format = None):
        serializer = ImageUploadSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)