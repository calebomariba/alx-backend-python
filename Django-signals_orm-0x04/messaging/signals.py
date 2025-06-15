from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    # Check if the instance exists in the database (i.e., it's an update)
    if instance.pk:
        try:
            old_message = Message.objects.get(pk=instance.pk)
            # If content has changed, log the old content
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender  # Assuming sender is the editor
                )
                instance.edited = True  # Mark the message as edited
        except Message.DoesNotExist:
            pass  # Handle case where message doesn't exist yet