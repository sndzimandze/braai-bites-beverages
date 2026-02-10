"""
Database Management Script using Flask-Migrate

Usage:
    # Initialize migrations
    python manage.py db init

    # Create a migration
    python manage.py db migrate -m "description of changes"

    # Apply migrations
    python manage.py db upgrade

    # Rollback migrations
    python manage.py db downgrade
"""
from flask_migrate import Migrate, MigrateCommand
from flask.cli import FlaskGroup
from app import create_app
from extensions import db
from models import Product

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(create_app=create_app)

if __name__ == '__main__':
    cli()
