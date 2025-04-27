from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Annotation
from .serializers import AnnotationSerializer
import uuid
import logging

logger = logging.getLogger(__name__)

class AnnotationListCreate(generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        permalink = self.request.query_params.get('permalink')
        if permalink:
            return Annotation.objects.filter(permalink=permalink)
        return Annotation.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        permalink = request.data.get('permalink')
        annotation = request.data.get('annotation')
        if not user or not permalink or not annotation:
            logger.error(f"Missing fields: user={user}, permalink={permalink}, annotation={annotation}")
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        if not annotation.get('id'):
            annotation['id'] = str(uuid.uuid4())
        version = annotation.get('version', '1970-01-01T00:00:00Z')
        serializer = self.get_serializer(data={
            'id': annotation['id'],
            'user': user,
            'permalink': permalink,
            'annotation': annotation,
            'version': version
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(annotation, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, *args, **kwargs):
        logger.info(f"Received DELETE to delete_by_permalink: query_params={request.query_params}, data={request.data}")
        permalink = request.data.get('permalink')
        if not permalink:
            logger.error("Permalink missing in delete_by_permalink")
            return Response({'error': 'Permalink is required for delete_by_permalink'}, status=status.HTTP_400_BAD_REQUEST)
        annotations = Annotation.objects.filter(permalink=permalink)
        if not annotations.exists():
            return Response({'message': 'No annotations found for this permalink'}, status=status.HTTP_404_NOT_FOUND)
        annotations.delete()
        return Response({'message': 'Annotations deleted'}, status=status.HTTP_204_NO_CONTENT)

class AnnotationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        try:
            obj = super().get_object()
            return obj
        except Annotation.DoesNotExist:
            logger.error(f"Annotation not found: id={self.kwargs.get('id')}")
            return Response({'error': 'Annotation not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id, *args, **kwargs):
        logger.info(f"Received PATCH request: id={id}, data={request.data}")
        user = request.data.get('user')
        permalink = request.data.get('permalink')
        annotation_data = request.data.get('annotation')

        if not all([user, permalink, annotation_data]):
            logger.error("Missing required fields in PATCH request")
            return Response({'error': 'User, permalink, and annotation are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            annotation = Annotation.objects.get(id=id)
            stored_version = annotation.version
            sent_version = annotation_data.get('version')

            if stored_version != sent_version:
                logger.warning(f"Version conflict for annotation {id}: stored={stored_version}, sent={sent_version}")
                return Response({'detail': 'Version conflict'}, status=status.HTTP_409_CONFLICT)

            serializer = AnnotationSerializer(annotation, data=annotation_data, partial=True)
            if serializer.is_valid():
                serializer.save(user=user, permalink=permalink)
                logger.info(f"Annotation updated successfully: id={id}")
                return Response(serializer.data)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Annotation.DoesNotExist:
            logger.error(f"Annotation not found: id={id}")
            return Response({'error': 'Annotation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating annotation: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Received DELETE request: url={request.path}, data={request.data}")
        instance = self.get_object()
        if isinstance(instance, Response):
            return instance
        if instance.user != request.user.username:
            logger.error(f"Permission denied: user={request.user.username}, annotation_user={instance.user}")
            return Response({'error': 'You can only delete your own annotations'}, status=status.HTTP_403_FORBIDDEN)
        permalink = request.data.get('permalink')
        logger.info(f"Deleting annotation: id={instance.id}, sent_permalink={permalink}, stored_permalink={instance.permalink}")
        if permalink and permalink != instance.permalink:
            logger.error(f"Permalink mismatch: sent={permalink}, stored={instance.permalink}")
            return Response({'error': 'Permalink does not match annotation'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)