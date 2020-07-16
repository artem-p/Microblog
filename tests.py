from app import app, db

class UserModelCase(unittest.TestCase):
    def setUp(self):
        # configure tests to run in in-memory database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
