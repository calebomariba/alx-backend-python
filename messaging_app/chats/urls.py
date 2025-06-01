from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from django.urls import routers.DefaultRouter()




from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_nested.routers import NestedDefaultRouter


# Define the main router for conversations
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
conversation_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', MessageViewSet, basename='conversation-message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]