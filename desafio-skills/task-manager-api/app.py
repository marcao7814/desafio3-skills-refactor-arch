import datetime

from flask import Flask
from flask_cors import CORS

from config.settings import SECRET_KEY, DATABASE_URL, DEBUG, PORT
from database import db
from views.task_routes import task_bp
from views.user_routes import user_bp
from views.category_routes import category_bp
from views.report_routes import report_bp
from middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.datetime.now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
