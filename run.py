from app import app
from waitress import serve
from paste.translogger import TransLogger

if app.config['ENVIRONMENT'].lower() == 'development':
    app.run(debug=True, host="0.0.0.0", port=app.config['SERVER_PORT'])
elif app.config['ENVIRONMENT'].lower() == 'production':
    app.run(debug=True, host='0.0.0.0', port=app.config['SERVER_PORT'])  # WAITRESS!
else:
    app.logger.error('Invalid environment variable option. Variable ENVIRONMENT set to %s. Valid Choices are PRODUCTION'
                     ' or DEVELOPMENT' % app.config['ENVIRONMENT'])
