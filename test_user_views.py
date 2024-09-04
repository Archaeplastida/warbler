"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for user."""

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
        
    def test_follower_or_following_viewing(self):
        """Can you see a user's followers/following if you're logged in? Are you not allowed to see a user's followers/following when logged out?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.add(testuser2)
        db.session.commit()

        resp = c.get(f"/users/{testuser2.id}/following")
        resp2 = c.get(f"/users/{testuser2.id}/followers")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

        #Time to log the user out and see if they're able to access these same views/routes (which the anon shouldn't).
        
        with self.client as c:
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

        resp3 = c.get(f"/users/{testuser2.id}/following")
        resp4 = c.get(f"/users/{testuser2.id}/followers")

        self.assertEqual(resp3.status_code, 302)
        self.assertEqual(resp4.status_code, 302)

    def test_logout(self):
        """Can you logout properly?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f"/messages/new")
        self.assertEqual(resp.status_code, 200) #Making sure the user is logged in first before logging out.
        
        resp2 = c.get("/logout")
        self.assertEqual(resp2.status_code, 302) #Making sure the logout redirects, so it gives out a 302 code.

    def test_adding_deleting_message(self):
        """Can you add or delete your messages? Can you add or delete messages when logged out? Can you add or delete another user's message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.add(testuser2)
        db.session.commit()

        testuser2msg = Message(text="I am testuser2, and this is my message!",
                               user_id=testuser2.id)
        
        db.session.add(testuser2msg)
        db.session.commit()

        print(testuser2msg.id)

        msg_resp = c.post("/messages/new", data={"text": "I am the one!"}, follow_redirects=True)
        self.assertEqual(msg_resp.status_code, 200) #Checking if user can send their own message.

        msg_id = Message.query.filter_by(user_id = self.testuser.id).first().id #Retriving message id.
        msg_delete_resp = c.post(f"/messages/{msg_id}/delete", follow_redirects=True)

        self.assertEqual(msg_delete_resp.status_code, 200)

        #It wouldn't really be possible to add message to the other user as the current user since the system is built in a way to check the cookie, instead of the specific id. Though, testing would work on trying to delete the other user's message.
        def test_unauthorized_msg_deletion():
            try:
                msg_delete_resp2 = c.post(f"/messages/{testuser2msg}/delete")
            except:
                raise ValueError

        self.assertRaises(ValueError, test_unauthorized_msg_deletion())

        #Now time to logout and see if we can send/delete messages

        with self.client as c:
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

        msg_resp2 = c.post("/messages/new", data={"text": "I want to send this unauthorized message."})

        self.assertEqual(msg_resp2.status_code, 302)

        #Creating another message since the first one was already deleted in the testing.

        testusermsg = Message(text="I am testuser!!! And this is my message!",
                               user_id=self.testuser.id)
        
        db.session.add(testusermsg)
        db.session.commit()

        def test_unauthorized_msg_deletion2():
            try:
                msg_delete_resp2 = c.post(f"/messages/{testusermsg}/delete")
            except:
                raise ValueError
            
        self.assertRaises(ValueError, test_unauthorized_msg_deletion2())