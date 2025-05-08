from django.db import models
import json

class Annotation(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    user = models.CharField(max_length=255)
    permalink = models.URLField()
    annotation = models.JSONField()
    version = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} by {self.user}"