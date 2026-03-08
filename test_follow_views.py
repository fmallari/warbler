"""Follow view tests -- testing likes, user model, message model, user views and message views """

import os
from unittest import TestCase

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
from models import db, User, Follows, Message, Likes


db.create_all()
app.config["WTF_CSRF_ENABLED"] = False

class FollowViewsTestCase(TestCase):
    """Test views for follow/unfollow."""

    def setUp(self):
        """Create test client and sample users."""

        Likes.query.delete()
        Message.query.delete()
        Follows.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.user1 = User.signup(
            username="user1",
            email="user1@test.com",
            password="password",
            image_url=None
        )

        self.user2 = User.signup(
            username="user2",
            email="user2@test.com",
            password="password",
            image_url=None
        )

        db.session.commit()

        self.user1_id = self.user1.id
        self.user2_id = self.user2.id

    def tearDown(self):
        db.session.rollback()


    def test_follow_user(self):
        """Logged-in user can follow another user."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1_id

            resp = c.post(f"/users/follow/{self.user2_id}",
                          follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            user1 = User.query.get(self.user1_id)

            self.assertEqual(len(user1.following), 1)
            self.assertEqual(user1.following[0].id, self.user2_id)

    def test_unfollow_user(self):
        """Logged-in user can unfollow another user."""

        self.user1.following.append(self.user2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1_id

            resp = c.post(f"/users/stop-following/{self.user2_id}",
                          follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            user1 = User.query.get(self.user1_id)
            self.assertEqual(len(user1.following), 0)

    def test_follow_requires_login(self):
        """Must be logged in to follow."""

        with self.client as c:
            resp = c.post(f"/users/follow/{self.user2_id}",
                          follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)
    
    def test_unfollow_requires_login(self):
        """Must be logged in to unfollow."""

        with self.client as c:
            resp = c.post(f"/users/stop-following/{self.user2_id}",
                          follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)