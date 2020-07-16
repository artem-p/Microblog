from app import app, db
from app.models import User
import unittest

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



if __name__ == '__main__':
    unittest.main(verbosity=2)
