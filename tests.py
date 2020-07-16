import unittest
from datetime import datetime, timedelta
from app import app, db
from app.models import Post, User


class UserModelCase(unittest.TestCase):
    def setUp(self):
        # configure tests to run in in-memory database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        user = User(username='susan')
        user.set_password('cat')
        self.assertFalse(user.check_password('dog'))
        self.assertTrue(user.check_password('cat'))

    def test_avatar(self):
        user = User(username='john', email='john@example.com')

        self.assertEqual(user.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow_unfollow(self):
        john = User(username='john', email='john@example.com')
        susan = User(username='susan', email='susan@example.com')

        db.session.add(john)
        db.session.add(susan)
        db.session.commit()

        self.assertEqual(john.followed.all(), [])
        self.assertEqual(susan.followed.all(), [])

        
        john.follow(susan)
        db.session.commit()

        self.assertTrue(john.is_following(susan))
        self.assertEqual(john.followed.count(), 1)
        self.assertEqual(john.followed.first().username, 'susan')

        self.assertEqual(susan.followers.count(), 1)
        self.assertEqual(susan.followers.first().username, 'john')

        
        john.unfollow(susan)
        db.session.commit()

        self.assertFalse(john.is_following(susan))
        self.assertEqual(john.followed.count(), 0)
        self.assertEqual(susan.followers.count(), 0)


    def test_followed_posts(self):
        # create users
        john = User(username='john', email='john@example.com')
        susan = User(username='susan', email='susan@example.com')
        mary = User(username='mary', email='mary@example.com')
        david = User(username='david', email='david@example.com')
        db.session.add_all([john, susan, mary, david])

        # create posts
        now = datetime.utcnow()
        johns_post = Post(body="post from john", author=john, timestamp=now + timedelta(seconds=1))
        susans_post = Post(body="post from susan", author=susan, timestamp=now + timedelta(seconds=4))
        marys_post = Post(body="post from mary", author=mary, timestamp=now + timedelta(seconds=3))
        davids_post = Post(body="post from david", author=david, timestamp=now + timedelta(seconds=2))
        db.session.add_all([johns_post, susans_post, marys_post, davids_post])
        db.session.commit()

        # setup the followers
        john.follow(susan)
        john.follow(david)
        susan.follow(mary)
        mary.follow(david)
        db.session.commit()

        # check the followed posts of each user
        john_followed_posts = john.followed_posts().all()
        susan_followed_posts = susan.followed_posts().all()
        mary_followed_posts = mary.followed_posts().all()
        david_followed_posts = david.followed_posts().all()

        self.assertEqual(john_followed_posts, [susans_post, davids_post, johns_post])
        self.assertEqual(susan_followed_posts, [susans_post, marys_post])
        self.assertEqual(mary_followed_posts, [marys_post, davids_post])
        self.assertEqual(david_followed_posts, [davids_post])


if __name__ == '__main__':
    unittest.main(verbosity=2)
