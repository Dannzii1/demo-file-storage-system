from flask import render_template

from flask import current_app


def page_not_found(error):
    """Custom 404 page."""
    current_app.logger.debug(error)
    return render_template('error_message/404.html'), 404


def internal_error(error):
    """Custom 500 page."""
    current_app.logger.debug(error)
    return render_template('error_message/500.html'), 500


def forbidden(error):
    """Custom 403 page."""
    current_app.logger.debug(error)
    return render_template('error_message/403.html'), 403
