"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

"""User model tests."""

import os
from unittest import TestCase

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app
from models import db, User, Message, Follows, Likes

db.create_all()


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Clean up any existing users/messages/follows/likes."""
        Likes.query.delete()
        Follows.query.delete()
        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.u1 = User.signup(
            username="testuser1",
            email="test1@test.com",
            password="password",
            image_url=None
        )
        self.u2 = User.signup(
            username="testuser2",
            email="test2@test.com",
            password="password",
            image_url=None
        )
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Basic user model works."""
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 0)

    def test_repr(self):
        """__repr__ returns a string."""
        self.assertIsInstance(repr(self.u1), str)

    def test_is_following(self):
        """is_following returns True when appropriate."""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        """is_followed_by returns True when appropriate."""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_signup(self):
        """User.signup creates user and hashes password."""
        u3 = User.signup(
            username="testuser3",
            email="test3@test.com",
            password="secret",
            image_url=None
        )
        db.session.commit()

        self.assertEqual(u3.username, "testuser3")
        self.assertNotEqual(u3.password, "secret")
        self.assertTrue(u3.password.startswith("$2b$") or u3.password.startswith("$2a$"))

    def test_authenticate_valid(self):
        """User.authenticate returns user with valid creds."""
        user = User.authenticate("testuser1", "password")
        self.assertEqual(user.id, self.u1.id)

    def test_authenticate_invalid_username(self):
        """User.authenticate fails with bad username."""
        self.assertFalse(User.authenticate("baduser", "password"))

    def test_authenticate_invalid_password(self):
        """User.authenticate fails with bad password."""
        self.assertFalse(User.authenticate("testuser1", "wrongpassword"))