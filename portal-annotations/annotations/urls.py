from django.urls import path
from . import views

urlpatterns = [
    path('annotations/', views.AnnotationListCreate.as_view(), name='annotation-list-create'),
    path('annotations/delete_by_permalink/', views.AnnotationListCreate.as_view(), name='annotation-delete-by-permalink'),
    path('annotations/<str:id>/', views.AnnotationRetrieveUpdateDestroy.as_view(), name='annotation-retrieve-update'),
    path('annotations/<str:id>/delete/', views.AnnotationRetrieveUpdateDestroy.as_view(), name='annotation-delete'),
]