"""Message model tests."""

import os
from unittest import TestCase

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app
from models import db, User, Message, Follows, Likes

db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        Likes.query.delete()
        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.user = User.signup(
            username="msguser",
            email="msg@test.com",
            password="password",
            image_url=None
        )
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Basic message model works."""
        msg = Message(text="Hello world", user_id=self.user.id)
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(msg.text, "Hello world")
        self.assertEqual(msg.user_id, self.user.id)
        self.assertEqual(msg.user.username, "msguser")

    def test_user_has_message(self):
        """User relationship contains new message."""
        msg = Message(text="Testing messages", user_id=self.user.id)
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "Testing messages")