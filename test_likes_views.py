"""Like view tests."""

import os
from unittest import TestCase

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
from models import db, User, Message, Follows, Likes

db.create_all()
app.config["WTF_CSRF_ENABLED"] = False
app.config["TESTING"] = True


class LikesViewsTestCase(TestCase):
    """Test views for likes."""

    def setUp(self):
        Likes.query.delete()
        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.user = User.signup(
            username="testuser",
            email="test@test.com",
            password="password",
            image_url=None
        )

        self.other_user = User.signup(
            username="otheruser",
            email="other@test.com",
            password="password",
            image_url=None
        )

        db.session.commit()

        self.msg = Message(
            text="hello world",
            user_id=self.other_user.id
        )
        db.session.add(self.msg)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_add_like(self):
        """Logged-in user can like a message."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.post(f"/users/add_like/{self.msg.id}", follow_redirects=False)
            self.assertEqual(resp.status_code, 302)

            like = Likes.query.filter_by(
                user_id=self.user.id,
                message_id=self.msg.id
            ).first()

            self.assertIsNotNone(like)

    def test_remove_like(self):
        """Logged-in user can unlike a message."""
        like = Likes(user_id=self.user.id, message_id=self.msg.id)
        db.session.add(like)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.post(f"/users/remove_like/{self.msg.id}", follow_redirects=False)
            self.assertEqual(resp.status_code, 302)

            like = Likes.query.filter_by(
                user_id=self.user.id,
                message_id=self.msg.id
            ).first()

            self.assertIsNone(like)

    def test_add_like_requires_login(self):
        """Anonymous user cannot like a message."""
        with self.client as c:
            resp = c.post(f"/users/add_like/{self.msg.id}", follow_redirects=False)
            self.assertEqual(resp.status_code, 302)

            like = Likes.query.filter_by(
                message_id=self.msg.id
            ).first()

            self.assertIsNone(like)

    def test_likes_page_renders_liked_posts(self):
        """Likes page shows liked messages."""
        like = Likes(user_id=self.user.id, message_id=self.msg.id)
        db.session.add(like)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get(f"/users/{self.user.id}/likes")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"hello world", resp.data)
            self.assertIn(b"@otheruser", resp.data)