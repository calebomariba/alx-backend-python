from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification
from django.db.models.signals import post_save
from .signals import create_message_notification

class MessageNotificationTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_notification_created_on_message_save(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )

        # Check if a notification was created for the receiver
        notification = Notification.objects.get(user=self.receiver, message=message)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_message_update(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message"
        )

        # Update the message
        message.content = "Updated message"
        message.save()

        # Check that only one notification exists
        self.assertEqual(Notification.objects.count(), 1)

    def test_signal_disconnected_during_test(self):
        # Disconnect the signal
        post_save.disconnect(create_message_notification, sender=Message)

        # Create a message
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="No notification should be created"
        )

        # Check that no notification was created
        self.assertEqual(Notification.objects.count(), 0)

        # Reconnect the signal to avoid affecting other tests
        post_save.connect(create_message_notification, sender=Message)