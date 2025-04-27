from rest_framework import serializers
from .models import Annotation
import json

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['id', 'user', 'permalink', 'annotation', 'version']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        annotation = instance.annotation
        if isinstance(annotation, str):
            try:
                annotation = json.loads(annotation)
            except json.JSONDecodeError:
                annotation = {}
        # Ensure version is included in annotation JSON
        if not annotation.get('version') and instance.version:
            annotation['version'] = instance.version
        representation['annotation'] = annotation
        print('Serialized annotation:', annotation)  # Debug
        return annotation