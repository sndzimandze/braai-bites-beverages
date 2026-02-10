"""
Flask Application Factory
"""
import logging
from flask import Flask
from config import Config
from extensions import db

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(config_class)

    # Validate configuration
    try:
        config_class.validate_config()
    except ValueError as e:
        app.logger.error(f"Configuration error: {e}")
        raise

    # Initialize extensions
    db.init_app(app)

    # Setup logging
    setup_logging(app)

    # Register blueprints
    from app.routes import main_bp, product_bp
    from app.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(admin_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register error handlers
    register_error_handlers(app)

    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Production logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
    else:
        # Development logging
        logging.basicConfig(level=logging.DEBUG)

    app.logger.info('Braai Bites & Beverages application started')


def register_error_handlers(app):
    """Register error handlers for the application"""

    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        app.logger.error(f'Internal server error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}')
        db.session.rollback()
        from flask import render_template
        return render_template('errors/500.html'), 500
