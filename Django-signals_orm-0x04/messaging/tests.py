from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db import models
from .models import Message, Notification, MessageHistory
from django.db.models.signals import post_save, pre_save, post_delete
from .signals import create_message_notification, log_message_edit, cleanup_user_data
import json

class MessageNotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )

    def test_notification_created_on_message_save(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )
        notification = Notification.objects.get(user=self.receiver, message=message)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_message_update(self):
        self.message.content = "Updated message"
        self.message.save()
        self.assertEqual(Notification.objects.count(), 1)

    def test_edit_logs_history(self):
        self.message.content = "Edited message"
        self.message.save()
        history = MessageHistory.objects.get(message=self.message)
        self.assertEqual(history.old_content, "Original message")
        self.assertEqual(history.edited_by, self.sender)
        self.assertTrue(self.message.edited)

    def test_no_history_on_same_content(self):
        self.message.content = "Original message"
        self.message.save()
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(self.message.edited)

    def test_message_history_view(self):
        self.client.login(username='sender', password='testpass')
        self.message.content = "Edited message"
        self.message.save()
        response = self.client.get(f'/message/{self.message.id}/history/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['message']['content'], "Edited message")
        self.assertEqual(data['history'][0]['old_content'], "Original message")

    def test_unauthorized_access(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        self.client.login(username='other', password='testpass')
        response = self.client.get(f'/message/{self.message.id}/history/')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_user_deletion_cascades_data(self):
        Notification.objects.create(user=self.sender, message=self.message)
        MessageHistory.objects.create(
            message=self.message,
            old_content="Old content",
            edited_by=self.sender
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(MessageHistory.objects.count(), 1)
        self.sender.delete()
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(MessageHistory.objects.count(), 0)

    def test_delete_user_view(self):
        self.client.login(username='sender', password='testpass')
        Notification.objects.create(user=self.sender, message=self.message)
        MessageHistory.objects.create(
            message=self.message,
            old_content="Old content",
            edited_by=self.sender
        )
        response = self.client.post('/delete-account/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'User sender deleted successfully')
        self.assertFalse(User.objects.filter(username='sender').exists())
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(MessageHistory.objects.count(), 0)

    def test_delete_user_wrong_method(self):
        self.client.login(username='sender', password='testpass')
        response = self.client.get('/delete-account/')
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_post_delete_signal(self):
        other_message = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Another message"
        )
        Notification.objects.create(user=self.sender, message=other_message)
        MessageHistory.objects.create(
            message=self.message,
            old_content="Old content",
            edited_by=self.sender
        )
        Message.sender.field.remote_field.on_delete = models.SET_NULL
        Message.receiver.field.remote_field.on_delete = models.SET_NULL
        Notification.user.field.remote_field.on_delete = models.SET_NULL
        MessageHistory.edited_by.field.remote_field.on_delete = models.SET_NULL
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(MessageHistory.objects.count(), 1)
        self.sender.delete()
        self.assertEqual(Message.objects.filter(sender=self.sender).count(), 0)
        self.assertEqual(Message.objects.filter(receiver=self.sender).count(), 0)
        self.assertEqual(Notification.objects.filter(user=self.sender).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(edited_by=self.sender).count(), 0)
        Message.sender.field.remote_field.on_delete = models.CASCADE
        Message.receiver.field.remote_field.on_delete = models.CASCADE
        Notification.user.field.remote_field.on_delete = models.CASCADE
        MessageHistory.edited_by.field.remote_field.on_delete = models.CASCADE

    def test_threaded_conversation(self):
        reply1 = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply 1",
            parent_message=self.message
        )
        reply2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Reply 2",
            parent_message=reply1
        )
        self.client.login(username='sender', password='testpass')
        response = self.client.get(f'/message/{self.message.id}/thread/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['conversation']['content'], "Original message")
        self.assertEqual(len(data['conversation']['replies']), 1)
        self.assertEqual(data['conversation']['replies'][0]['content'], "Reply 1")
        self.assertEqual(len(data['conversation']['replies'][0]['replies']), 1)
        self.assertEqual(data['conversation']['replies'][0]['replies'][0]['content'], "Reply 2")

    def test_threaded_conversation_unauthorized(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        other_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Other message"
        )
        self.client.login(username='other', password='testpass')
        response = self.client.get(f'/message/{other_message.id}/thread/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f'/message/{self.message.id}/thread/')
        self.assertEqual(response.status_code, 404)

    def test_threaded_conversation_query_optimization(self):
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply",
            parent_message=self.message
        )
        self.client.login(username='sender', password='testpass')
        with self.assertNumQueries(3):
            response = self.client.get(f'/message/{self.message.id}/thread/')
            self.assertEqual(response.status_code, 200)

    def test_threaded_conversation_sender_filter(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        unrelated_message = Message.objects.create(
            sender=other_user,
            receiver=self.receiver,
            content="Unrelated message"
        )
        self.client.login(username='sender', password='testpass')
        response = self.client.get(f'/message/{unrelated_message.id}/thread/')
        self.assertEqual(response.status_code, 404)

    def test_unread_messages_manager(self):
        # Create messages
        unread_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            read=False
        )
        read_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Read message",
            read=True
        )
        # Test custom manager
        unread = Message.unread.for_user(self.receiver)
        self.assertEqual(unread.count(), 2)  # Includes self.message and unread_message
        self.assertNotIn(read_message, unread)

    def test_unread_messages_view(self):
        # Create messages
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            read=False
        )
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Read message",
            read=True
        )
        self.client.login(username='receiver', password='testpass')
        response = self.client.get('/unread-messages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['unread_messages']), 2)  # self.message and unread_message
        self.assertEqual(data['unread_messages'][0]['content'], "Original message")
        self.assertFalse(data['unread_messages'][0]['read'])

    def test_unread_messages_query_optimization(self):
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Unread message",
            read=False
        )
        self.client.login(username='receiver', password='testpass')
        with self.assertNumQueries(1):  # Single query with select_related
            response = self.client.get('/unread-messages/')
            self.assertEqual(response.status_code, 200)

    def test_signal_disconnected_during_test(self):
        post_save.disconnect(create_message_notification, sender=Message)
        pre_save.disconnect(log_message_edit, sender=Message)
        post_delete.disconnect(cleanup_user_data, sender=User)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="No notification or history should be created"
        )
        message.content = "Edited message"
        message.save()
        self.sender.delete()
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0)
        post_save.connect(create_message_notification, sender=Message)
        pre_save.connect(log_message_edit, sender=Message)
        post_delete.connect(cleanup_user_data, sender=User)