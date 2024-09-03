"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work, with the user being created correctly with appropriate information and the opposite with inappropriate information?"""

        u = {
            "email":"test@test.com",
            "username":"testuser",
            "password":"HASHED_PASSWORD",
            "image_url":"static/images/default-pic.png"
        }

        signed_up_user = User.signup(
            email=u["email"],
            username=u["username"],
            password=u["password"],
            image_url=u["image_url"]
        )

        db.session.add(signed_up_user)
        db.session.commit()

        created_user = User.query.filter(User.username == u["username"]).first()

        # User should have no messages, or followers, but should also be created properly, with __repr__ working.
        self.assertEqual(len(created_user.messages), 0)
        self.assertEqual(len(created_user.followers), 0)
        self.assertEqual(created_user.username, u["username"])
        self.assertEqual(created_user.email, u["email"])
        self.assertNotEqual(created_user.password, u["password"])
        self.assertEqual(created_user.__repr__(), f"<User #{created_user.id}: {created_user.username}, {created_user.email}>")

        not_unique_user = User.signup(
            email=u["email"],
            username=u["username"],
            password=u["password"],
            image_url=u["image_url"]
        )

        def test_this_constraint():
            try:
                db.session.add(not_unique_user)
                db.session.commit()
            except:
                raise ValueError

        self.assertRaises(ValueError, test_this_constraint)

    def test_user_is_following(self):
        """Does is_following() detect if user1 is following user2?"""

        default_image = "static/images/default-pic.png"

        for user_num in range(1,3):
            create_user = User.signup(
                email=f"user{user_num}@test.com",
                username=f"user{user_num}",
                password="HASHED_PASSWORD",
                image_url=default_image
                )
            
            db.session.add(create_user)
            db.session.commit()
            
        u1 = User.query.filter_by(username = "user1").first()
        u2 = User.query.filter_by(username = "user2").first()

        the_follow = u1.following.append(u2)
        db.session.commit()
#user should authenticate at the certain variable for such
        #user1 should be following user2, with the is_following() method working.
        self.assertEqual(u1.is_following(u2), True) #should return True.

        #user1 now unfollows user2, now the is_following() method should return false.
        u1.following.remove(u2)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), False) #should return False.

    def test_user_followed_by(self):
        """Does is_followed_by() detect if user2 is followed by user?"""

        default_image = "static/images/default-pic.png"

        for user_num in range(1,3):
            create_user = User.signup(
                email=f"user{user_num}@test.com",
                username=f"user{user_num}",
                password="HASHED_PASSWORD",
                image_url=default_image
                )
            
            db.session.add(create_user)
            db.session.commit()
            
        u1 = User.query.filter_by(username = "user1").first()
        u2 = User.query.filter_by(username = "user2").first()

        the_follow = u2.followers.append(u1)
        db.session.commit()

        #user2 should be followed by user1, with the is_followed_by() method working.
        self.assertEqual(u2.is_followed_by(u1), True)

        #user2 now isn't followed by user1 anymore, so the is_followed_by() method should return false.

        u2.followers.remove(u1)
        db.session.commit()

        self.assertEqual(u2.is_followed_by(u1), False)

    def test_user_authenticate(self):
        """Does user authentication return a user when provided with a valid username and password?
        Also does it return False if provided with the incorrect credentials"""
        
        default_image = "static/images/default-pic.png"

        user = User.signup(
        email=f"user1@test.com",
        username=f"user1",
        password="HASHED_PASSWORD",
        image_url=default_image
        )

        self.assertEqual(type(user.authenticate( #With correct info
            username="user1",
            password="HASHED_PASSWORD")), User)
        
        self.assertEqual(user.authenticate( #With incorrect user
            username="user1_but_incorrect",
            password="HASHED_PASSWORD"), False)
        
        self.assertEqual(user.authenticate( #With incorrect password
            username="user1",
            password="HASHED_PASSWORD_INCORRECT"), False)