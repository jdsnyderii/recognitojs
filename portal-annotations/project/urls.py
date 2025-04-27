from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user.username if self.request.user.is_authenticated else ''
        return context

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('annotations.urls')),
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)