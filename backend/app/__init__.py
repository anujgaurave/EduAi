from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.db import db
import logging
import os

def create_app(config_name='development'):
    """Application factory for Flask"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup logging
    if not app.debug:
        os.makedirs('logs', exist_ok=True)
        handler = logging.FileHandler('logs/app.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        app.logger.addHandler(handler)
    
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid tokens"""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Invalid token error: {error}")
        return jsonify({'error': 'Invalid token. Please login again.'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired tokens"""
        return jsonify({'error': 'Token expired. Please login again.'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing tokens"""
        return jsonify({'error': 'Authorization required'}), 401
    
    # Connect to database
    if not db.connect():
        app.logger.error("Failed to connect to MongoDB")
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db.db is not None else 'disconnected'
        }), 200
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.notes import notes_bp
    from app.routes.assessments import assessments_bp
    from app.routes.progress import progress_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(progress_bp)

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
