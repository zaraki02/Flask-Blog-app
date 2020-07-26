from flask_blog import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')

    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec= 1800):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)['user_id']
        except:
            print("None!!!!!!!!!!!!!!!!!!!!!!!!")
            return None
        print("User is chill!!!!!!!!!!!!!!!!!!!")
        return Users.query.get(user_id)

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.image})'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # in the foreign key user is lower case as that is the table name that is by default named from he class User...

    def __repr__(self):
        return f'User({self.title}, {self.date}, {self.content})'
