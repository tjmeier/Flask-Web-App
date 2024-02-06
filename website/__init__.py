from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gsn#ef?KWkdQGVq%bYQbE_tSQ}3B0*__A$v{`s")4LRU;1y5/o3W{OI_T?^EVQf' #encrypts and secures cookies and session data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' #stores database in the 'website' folder
    db.init_app(app) #initialize database with this current app



    from .views import views
    from .views_auth import views_auth
    from .views_admin import views_admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(views_auth, url_prefix='/')
    app.register_blueprint(views_admin, url_prefix='/admin')


    from .models import User, Note #gets specific database models that we created into the app

    create_database(app)

    #since a login is required, we send users who need to be logged in to the login page
    login_manager = LoginManager()
    login_manager.login_view = 'views_auth.login'
    login_manager.init_app(app)

    #tells login manager how to load a user
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME): #checks if the database file has been created
        with app.app_context():
            db.create_all() #tells alchemy we are creating the database for this current app
        print('Created Database!')
