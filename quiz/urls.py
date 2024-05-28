from .views import *
from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('quiz', QuizViewset)
router.register('questions', QuestionViewset)
router.register('options', OptionViewset)
router.register('scheduled-event',ScheduledEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
