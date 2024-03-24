from django.test import TestCase
from django.contrib.auth.models import User
from post.models import Post
from notifications.models import Notification
from .models import Comment  # replace 'yourapp' with the name of your Django app

class CommentSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.post = Post.objects.create(title='Test Post', content='Test content', user=self.user)
        self.comment = Comment.objects.create(post=self.post, user=self.user, body='Test comment')

    def test_comment_created_signal(self):
        """
        Test if a notification is created when a comment is saved.
        """
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.post, self.post)
        self.assertEqual(notification.sender, self.user)
        self.assertEqual(notification.user, self.post.user)
        self.assertEqual(notification.text_preview, 'Test comment')

    def test_comment_deleted_signal(self):
        """
        Test if the associated notification is deleted when a comment is deleted.
        """
        self.comment.delete()
        self.assertEqual(Notification.objects.count(), 0)
