from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '123jskdbf123sdfjn729889728'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
app.config["MAIL_SERVER"] = 'smtp.googlemail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
#app.config['MAIL_USE_SSL'] = True

app.config["MAIL_USERNAME"] = "abhijeet2101999@gmail.com"#os.environ.get('EMAIL_USER')

app.config["MAIL_PASSWORD"] = 'mywcpjijmvzhpfnc'
mail = Mail(app)

from flask_blog import routes

'''
from flask_blog.users.routes import users
from flask_blog.posts.routes import posts
from flask_blog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)

'''