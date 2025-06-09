from django_filters import rest_framework as filters
from chats.models import Message
from django.contrib.auth.models import User

class MessageFilter(filters.FilterSet):
    """
    Filter messages by conversation participants or timestamp range.
    """
    participant = filters.ModelMultipleChoiceFilter(
        field_name='conversation__participants',
        queryset=User.objects.all(),
        label='Participant user IDs'
    )
    timestamp_gte = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_lte = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['participant', 'timestamp_gte', 'timestamp_lte']