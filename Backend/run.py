from app import create_app
from app.database.redis_manager import redis_manager

# Create the Flask application instance using development configuration
# This initializes all components (routes, database, etc.)
app = create_app('development')

if __name__ == '__main__':
    # Check if Redis connection is working before starting the server
    # Redis is used for session storage. If it fails, sessions won't be saved !!!!!!!!!!!
    if not redis_manager.is_connected():
        print("WARNING: Redis connection failed. Sessions will not be persisted...")
    
    # Start the Flask development server
    # debug=True enables auto reload and detailed error pages
    # host='0.0.0.0' makes the server accessible from other devices on the network
    # port=5000 uses the default Flask port
    app.run(debug=True, host='0.0.0.0', port=5000)