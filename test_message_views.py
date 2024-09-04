"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_message_visiblity_after_adding_message(self):
        """Is the text displayed on the message, via HTML?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            my_inputted_text = "Hello, please test me out!"

            resp = c.post("/messages/new", data={"text": my_inputted_text}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(my_inputted_text, resp.get_data().decode())

    def test_view_message(self):
        """Is the text on the message displayed in the message closeup, via HTML?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            my_inputted_text = "Hello, view me right now!"

            c.post("/messages/new", data={"text": my_inputted_text}, follow_redirects=True)
            msg_id = Message.query.filter_by(user_id = self.testuser.id).first().id #Retriving message id.
            
            html = c.get(f"/messages/{msg_id}")

            self.assertIn(html.status_code, 200)
            self.assertIn(my_inputted_text, html.get_data().decode())

    def test_delete_message(self):
        """Will the message get removed and not appear on the user page anymore?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            my_inputted_text = "Hello, view me right now!"

            resp = c.post("/messages/new", data={"text": my_inputted_text}, follow_redirects=True)
            
            self.assertIn(my_inputted_text, resp.get_data().decode()) #Confirming that the message exists, before we try deleting it.
            msg_id = Message.query.filter_by(user_id = self.testuser.id).first().id #Retriving message id.

            self.assertIn(resp.status_code, 200)

            resp2 = c.post(f"/messages/{msg_id}/delete", follow_redirects=True)
            self.assertNotIn(my_inputted_text, resp2.get_data().decode())

            self.assertIn(resp2.status_code, 200)