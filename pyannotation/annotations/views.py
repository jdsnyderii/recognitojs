from rest_framework import generics, status
from rest_framework.response import Response
from datetime import datetime

from .models import Annotation
from .serializers import AnnotationSerializer
import logging
import uuid

logger = logging.getLogger(__name__)

class AnnotationListCreate(generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer

    def get_queryset(self):
        logger.info(f"Received GET request: query_params={self.request.query_params}, data={self.request.data}")
        permalink = self.request.query_params.get('permalink')
        if permalink:
            return Annotation.objects.filter(permalink=permalink)
        return Annotation.objects.all()

    def create(self, request, *args, **kwargs):
        logger.info(f"Received POST request: data={request.data}")
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

        try:
            annotations = Annotation.objects.filter(permalink=permalink)
            count = annotations.count()
            if count == 0:
                logger.warning(f"No annotations found for permalink: {permalink}")
                return Response({'error': 'No annotations found for the given permalink'}, status=status.HTTP_404_NOT_FOUND)

            annotations.delete()
            logger.info(f"Deleted {count} annotations for permalink: {permalink}")
            return Response({'message': f'Successfully deleted {count} annotations'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting annotations: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnnotationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Received PATCH request: id={self.kwargs.get('id')}, data={request.data}")
        user = request.data.get('user')
        permalink = request.data.get('permalink')
        annotation_data = request.data.get('annotation')

        if not all([user, permalink, annotation_data]):
            logger.error("Missing required fields in PATCH request")
            return Response({'error': 'User, permalink, and annotation are required'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        logger.info(f"Retrieved instance: id={instance.id}, version={instance.version}")

        stored_version = instance.version
        sent_version = annotation_data.get('version')
        if stored_version and sent_version and stored_version != sent_version:
            logger.warning(f"Version conflict for annotation {instance.id}: stored={stored_version}, sent={sent_version}")
            return Response({'detail': 'Version conflict'}, status=status.HTTP_409_CONFLICT)

        annotation_data.update({'version': datetime.now().astimezone().isoformat()})
        serializer = self.get_serializer(instance, data=annotation_data, partial=True)
        if serializer.is_valid():
            updated_instance = serializer.save(user=user, permalink=permalink)
            logger.info(f"Annotation updated successfully: id={updated_instance.id}, version={updated_instance.version}")
            # Verify database state
            db_instance = Annotation.objects.get(id=updated_instance.id)
            logger.info(f"Database state: id={db_instance.id}, version={db_instance.version}")
            return Response(serializer.data)
        logger.error(f"Serializer errors in PATCH: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Received GET request: id={self.kwargs.get('id')}")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved annotation: id={instance.id}")
            return Response(serializer.data)
        except Annotation.DoesNotExist:
            logger.error(f"Annotation not found: id={self.kwargs.get('id')}")
            return Response({'error': 'Annotation not found'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Received DELETE request: id={self.kwargs.get('id')}, data={request.data}")
        try:
            instance = self.get_object()
            logger.info(f"Instance ID to DELETE: id={instance.id}")
            permalink = request.data.get('permalink')
            if not permalink:
                logger.error("Permalink missing in DELETE request")
                return Response({'error': 'Permalink is required'}, status=status.HTTP_400_BAD_REQUEST)
            if instance.permalink != permalink:
                logger.warning(f"Permalink mismatch: sent={permalink}, stored={instance.permalink}")
                return Response({'error': 'Permalink does not match'}, status=status.HTTP_400_BAD_REQUEST)
            instance.delete()
            logger.info(f"Annotation deleted successfully: id={instance.id}")
            return Response({'message': 'Annotation deleted successfully'}, status=status.HTTP_200_OK)
        except Annotation.DoesNotExist:
            logger.error(f"Annotation not found: id={self.kwargs.get('id')}")
            return Response({'error': 'Annotation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting annotation: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
