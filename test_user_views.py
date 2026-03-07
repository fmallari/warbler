"""User view tests."""

import os
from unittest import TestCase

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
from models import db, User, Message, Follows, Likes

db.create_all()
app.config["WTF_CSRF_ENABLED"] = False


class UserViewsTestCase(TestCase):
    """Test views for users."""

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
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_list_users(self):
        """Can see users index."""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"testuser", resp.data)

    def test_signup(self):
        """Can signup a new user."""
        with self.client as c:
            resp = c.post(
                "/signup",
                data={
                    "username": "newuser",
                    "email": "new@test.com",
                    "password": "password",
                    "image_url": ""
                },
                follow_redirects=True
            )
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(User.query.filter_by(username="newuser").first() is not None)

    def test_login_valid(self):
        """Can login with valid credentials."""
        with self.client as c:
            resp = c.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Hello, testuser!", resp.data)
            
# ------ intentionally marked invalid characters in password field to fail test, but test is passing when pw has 6+ characters. Ignore. ------
    def test_login_invalid(self):
        """Cannot login with bad credentials."""
        with self.client as c:
            resp = c.post(
                "/login",
                data={"username": "testuser", "password": "wrong"},
                follow_redirects=True
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Invalid credentials", resp.data)

    def test_logout(self):
        """Can logout user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get("/logout", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"You have successfully logged out", resp.data)

    def test_profile_get_requires_login(self):
        """Must be logged in to view profile edit form."""
        with self.client as c:
            resp = c.get("/users/profile", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)

    def test_profile_edit(self):
        """Logged-in user can edit profile."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.post(
                "/users/profile",
                data={
                    "username": "updateduser",
                    "email": "updated@test.com",
                    "image_url": "",
                    "header_image_url": "",
                    "bio": "Updated bio",
                    "password": "password"
                },
                follow_redirects=False
            )

            self.assertEqual(resp.status_code, 302)

            updated = User.query.get(self.user.id)
            self.assertEqual(updated.username, "updateduser")
            self.assertEqual(updated.email, "updated@test.com")
            self.assertEqual(updated.bio, "Updated bio")