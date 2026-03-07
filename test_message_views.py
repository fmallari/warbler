"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

"""Message view tests."""

import os
from unittest import TestCase

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
from models import db, User, Message, Follows, Likes

db.create_all()
app.config["WTF_CSRF_ENABLED"] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        Likes.query.delete()
        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(
            username="testuser",
            email="test@test.com",
            password="password",
            image_url=None
        )
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_add_message(self):
        """Logged-in user can add message."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=False)

            self.assertEqual(resp.status_code, 302)
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_no_user(self):
        """Anon user cannot add message."""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(Message.query.count(), 0)
            self.assertIn(b"Access unauthorized", resp.data)

    def test_show_message(self):
        """Can view message details."""
        msg = Message(text="Test message", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            resp = c.get(f"/messages/{msg.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test message", resp.data)

    def test_delete_own_message(self):
        """Logged-in user can delete own message."""
        msg = Message(text="Delete me", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=False)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(Message.query.count(), 0)