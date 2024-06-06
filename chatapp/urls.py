from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('conversation', ConversationViewSet)
router.register('messages', MessagesViewSet)

urlpatterns = [
    path('', lobby),
    path('', include(router.urls))
]
