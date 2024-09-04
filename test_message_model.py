"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for Message Model."""
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does the basic model work?"""
        
        default_image = "static/images/default-pic.png"

        user = User.signup(
        email=f"user1@test.com",
        username=f"user1",
        password="HASHED_PASSWORD",
        image_url=default_image
        )

        db.session.add(user)
        db.session.commit()

        msg = Message(text="Test Message.",
                      user_id=user.id)
        
        db.session.add(msg)
        db.session.commit()

        #Check if the message contains correctly inputted data and if other data gets prefilled by the message model.
        self.assertEqual(msg.text, "Test Message.")
        self.assertEqual(msg.user_id, user.id)
        self.assertIsNotNone(msg.timestamp)
        self.assertIsNotNone(msg.id)

    def test_message_by_user(self):
        """Does it recognize which user the message came from?"""

        default_image = "static/images/default-pic.png"

        user = User.signup(
        email=f"user1@test.com",
        username=f"user1",
        password="HASHED_PASSWORD",
        image_url=default_image
        )

        db.session.add(user)
        db.session.commit()

        msg = Message(text="Test Message.",
                      user_id=user.id)
        
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(msg.user.__repr__(), f"<User #{user.id}: user1, user1@test.com>")