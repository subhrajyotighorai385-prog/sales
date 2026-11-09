import os
from datetime import datetime
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, csrf
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.transactions import transactions_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)

    # Global context processor
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'app_name': 'High Value Sales',
            'platform_version': 'v3.2 Enterprise 3D'
        }

    # Template filters
    @app.template_filter('format_currency')
    def format_currency(value, symbol='₹'):
        if value is None:
            return f"{symbol}0.00"
        try:
            return f"{symbol}{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"{symbol}{value}"

    @app.template_filter('format_number')
    def format_number(value):
        if value is None:
            return "0"
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('404.html', message="Uploaded file exceeds the maximum allowed size (16MB)."), 413

    # Create tables
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=True)
