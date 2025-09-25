from flask import Flask
from flask_cors import CORS
from .api.endpoints import api_bp
from .database.redis_manager import redis_manager

def create_app(config_class='default'):
    # Create the main Flask application instance
    app = Flask(__name__)
    
    # Load configuration settings based on environment (development/production)
    from config import config
    app.config.from_object(config[config_class])
    
    # Configure Cross Origin Resource Sharing (CORS) for frontend & backend communication
    # This allows the React frontend on localhost:5173 to make requests to this backend
    CORS(app, 
         supports_credentials=True,  # Allows cookies and authentication
         origins=["http://localhost:5173"],  # Only allow requests from frontend
         allow_headers=["Content-Type", "X-API-Key"],  # Allowed request headers
         methods=["GET", "POST", "DELETE", "OPTIONS"])  # Allowed HTTP methods
    
    # Register the API blueprint. Organizes routes into modular components
    app.register_blueprint(api_bp, url_prefix='/api')
    # This will make the routes accessible at /api/health, /api/detect, etc
    # The url_prefix ensures all API routes start with /api
    
    # Initialize Redis connection for session storage and caching
    redis_manager.connect()
    
    return app  # Return the fully configured application instance