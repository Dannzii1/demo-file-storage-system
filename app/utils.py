from functools import wraps
from app import app
from flask_login import current_user
from werkzeug.exceptions import abort

from app.models import Documents
import os
from _datetime import datetime


def has_document_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        file = Documents.query.filter_by(id=kwargs['file_id']).first()

        if file and file.user_id == current_user.id:
            return func(*args, **kwargs)
        abort(404)

    return wrapper


def generate_institution_document_paths(current_institution):
    relative_path = os.path.normpath(os.path.join(current_institution, datetime.now().strftime('%Y')))
    absolute_path = os.path.normpath(os.path.join(app.config['DOCUMENTS_UPLOAD_FOLDER'], relative_path))
    return absolute_path, relative_path