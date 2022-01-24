import os.path
from logging.config import dictConfig

from flask import Flask
from flask_login import LoginManager
from flask_minify import minify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import MetaData
from dotenv import load_dotenv
from os import getenv
from flask_mail import Mail

from flask_wtf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from app.app_error_handling import page_not_found, internal_error
load_dotenv()

# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#             'class': 'logging.StreamHandler',
#             'stream': 'ext://flask.logging.wsgi_errors_stream',
#             'formatter': 'default'
#         }, 'app': {
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': os.path.join(getenv('LOG_PATH'), 'app.log'),
#             'formatter': 'default',
#             'when': 'midnight',
#             'encoding': 'utf-8',
#             'backupCount': 5
#         }
#     },
#     'root': {
#         'level': getenv('LOGGER_LEVEL').upper(),
#         'handlers': ['wsgi', 'app']
#     }
# })

app = Flask(__name__)
csrf = CSRFProtect(app)

bcrypt = Bcrypt(app)
app.config['TEMPLATES_AUTO_RELOAD'] = getenv('IS_SECURED')
app.config['ENVIRONMENT'] = getenv('ENVIRONMENT')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')
app.config['PW_RESET_TIMEOUT'] = getenv('PW_RESET_TIMEOUT')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SERVER_PORT'] = getenv('SERVER_PORT')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

DOCUMENTS_UPLOAD_FOLDER = getenv('DOCUEMENTS')

# SECRET_KEY is needed for session security, the flash() method in this case stores the message in a session
SECRET_KEY = getenv('SECRET_KEY')
DEFAULT_PASSWORD = getenv('DEFAULT_PASSWORD')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

app.config.from_object(__name__)
minify(app=app, html=True, js=True, cssless=True)
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_error)
db = SQLAlchemy(app, metadata=metadata)

allowed_uploads = getenv('ALLOWED_UPLOADS').split(',')
app.config['MAX_CONTENT_LENGTH_PER_UPLOAD'] = float(getenv('MAX_CONTENT_LENGTH_PER_UPLOAD'))

app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = getenv('TLS_PORT')
app.config['MAIL_USERNAME'] = getenv('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = getenv('IS_SECURED')
app.config['MAIL_SENDER'] = 'jtecmoe@gmail.com'

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from app import views
