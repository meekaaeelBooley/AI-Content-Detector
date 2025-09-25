import redis
import json
import datetime

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        # Set up connection details for Redis server
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = None  # Will hold the actual connection
        self.connected = False    # Track connection status
        
    def connect(self):
        # Try to establish connection to Redis server
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Automatically convert bytes to strings
            )
            # Test the connection by sending a ping
            self.redis_client.ping()
            print("Connected to Redis successfully")
            self.connected = True
        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            self.connected = False
    
    def is_connected(self):
        # Check if we can communicate with Redis
        try:
            return self.redis_client.ping()
        except:
            return False
    
    def store_session(self, session_id, session_data):
        # Save session data to Redis as JSON
        try:
            key = f"session:{session_id}"  # Create unique key for this session
            
            # Convert datetime objects to strings for JSON storage
            if 'created_at' in session_data and isinstance(session_data['created_at'], datetime.datetime):
                session_data['created_at'] = session_data['created_at'].isoformat()
            
            if 'analyses' in session_data:
                for analysis in session_data['analyses']:
                    if 'timestamp' in analysis and isinstance(analysis['timestamp'], datetime.datetime):
                        analysis['timestamp'] = analysis['timestamp'].isoformat()
            
            # Store the session data as JSON string in Redis
            self.redis_client.set(key, json.dumps(session_data))
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id):
        # Retrieve session data from Redis
        try:
            key = f"session:{session_id}"
            data = self.redis_client.get(key)
            
            if data:
                # Convert JSON string back to python dictionary
                session_data = json.loads(data)
                
                # Convert string timestamps back to datetime objects
                if 'created_at' in session_data:
                    session_data['created_at'] = datetime.datetime.fromisoformat(session_data['created_at'])
                
                if 'analyses' in session_data:
                    for analysis in session_data['analyses']:
                        if 'timestamp' in analysis:
                            analysis['timestamp'] = datetime.datetime.fromisoformat(analysis['timestamp'])
                
                return session_data
            return None  # No session found
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def update_session_analyses(self, session_id, analysis):
        # Add a new analysis to an existing session
        try:
            # Get current session data
            session_data = self.get_session(session_id)
            
            # Create new session if it doesn exist
            if not session_data:
                session_data = {
                    'created_at': datetime.datetime.now(),
                    'analyses': []
                }
            
            # Ensure analyses list exists
            if 'analyses' not in session_data:
                session_data['analyses'] = []
            
            # Add the new analysis to the list
            session_data['analyses'].append(analysis)
            return self.store_session(session_id, session_data)
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def clear_session_analyses(self, session_id):
        # Remove all analyses from a session but keep the session itself
        try:
            session_data = self.get_session(session_id)
            if session_data:
                session_data['analyses'] = []  # Empty the analyses list
                return self.store_session(session_id, session_data)
            return True  # Session didn't exist, so nothing to clear
        except Exception as e:
            print(f"Error clearing analyses: {e}")
            return False
    
    def delete_session(self, session_id):
        # Completely remove a session from Redis
        try:
            key = f"session:{session_id}"
            return self.redis_client.delete(key) > 0  # Returns True if deleted
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_all_sessions(self):
        # Get all sessions from Redis (for admin purposes)
        try:
            sessions = []
            keys = self.redis_client.keys("session:*")  # Find all session keys
            
            for key in keys:
                session_id = key.split(":")[1]  # Extract session ID from key
                session_data = self.get_session(session_id)
                if session_data:
                    sessions.append({
                        'session_id': session_id,
                        'data': session_data
                    })
            return sessions
        except Exception as e:
            print(f"Error getting all sessions: {e}")
            return []
    
    def store_analysis_result(self, analysis_id, result):
        # Store individual analysis result with its own ID
        try:
            key = f"analysis:{analysis_id}"
            self.redis_client.set(key, json.dumps(result))
            return True
        except Exception as e:
            print(f"Error storing analysis: {e}")
            return False
    
    def get_analysis_result(self, analysis_id):
        # Retrieve individual analysis result by ID
        try:
            key = f"analysis:{analysis_id}"
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting analysis: {e}")
            return None

# Create a global instance that can be imported and used throughout the app
redis_manager = RedisManager()


# TESTING TESTING...


# Test code that runs only when this file is executed directly
if __name__ == "__main__":
    manager = RedisManager()
    manager.connect()
    
    if manager.is_connected():
        print("Redis connection test: PASSED")
        # Create test data to verify storage works
        test_session = {
            'created_at': datetime.datetime.now(),
            'analyses': [
                {
                    'id': 'test-1',
                    'text_preview': 'Test text...',
                    'result': {'ai_probability': 0.8, 'human_probability': 0.2},
                    'timestamp': datetime.datetime.now(),
                    'text_length': 100
                }
            ]
        }
        
        # Test storing and retrieving data
        manager.store_session('test-session', test_session)
        retrieved = manager.get_session('test-session')
        
        if retrieved:
            print("Session storage test: PASSED")
        else:
            print("Session storage test: FAILED")
        
        # Clean up test data
        manager.delete_session('test-session')
    else:
        print("Redis connection test: FAILED")