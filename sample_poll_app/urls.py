"""URL routes for the sample app."""
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter

from .viewsets import ChoiceViewSet, QuestionViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(
        template_name='sample_poll_app/home.html'), name='home'),
    url(r'^api-auth/', include(
        'rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls))
)
