from api.app import app

if __name__ == '__main__':
    # Check Redis connection before starting
    from services.redis_manager import redis_manager
    if not redis_manager.is_connected():
        print("WARNING: Redis connection failed. Sessions will not be persisted.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)  # Set debug=False for production