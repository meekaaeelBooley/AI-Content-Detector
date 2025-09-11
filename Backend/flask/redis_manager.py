import redis
import json
import datetime
import os

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """Connect to Redis server"""
        try:
            # Create Redis connection
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Makes responses easier to work with
            )
            # Test if connection works
            self.redis_client.ping()
            print("Connected to Redis successfully")
        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            raise
    
    def is_connected(self):
        """Check if we're connected to Redis"""
        try:
            return self.redis_client.ping()
        except:
            return False
    
    def store_session(self, session_id, session_data):
        """Save session data to Redis (no expiration)"""
        try:
            key = f"session:{session_id}"
            
            # Convert datetime objects to strings so they can be stored as JSON
            if 'created_at' in session_data and isinstance(session_data['created_at'], datetime.datetime):
                session_data['created_at'] = session_data['created_at'].isoformat()
            
            # Convert timestamps in each analysis
            if 'analyses' in session_data:
                for analysis in session_data['analyses']:
                    if 'timestamp' in analysis and isinstance(analysis['timestamp'], datetime.datetime):
                        analysis['timestamp'] = analysis['timestamp'].isoformat()
            
            # Store without expiration (stays forever until manually deleted)
            self.redis_client.set(key, json.dumps(session_data))
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id):
        """Get session data from Redis"""
        try:
            key = f"session:{session_id}"
            data = self.redis_client.get(key)
            
            if data:
                session_data = json.loads(data)
                
                # Convert string timestamps back to datetime objects
                if 'created_at' in session_data:
                    session_data['created_at'] = datetime.datetime.fromisoformat(session_data['created_at'])
                
                # Convert analysis timestamps
                if 'analyses' in session_data:
                    for analysis in session_data['analyses']:
                        if 'timestamp' in analysis:
                            analysis['timestamp'] = datetime.datetime.fromisoformat(analysis['timestamp'])
                
                return session_data
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def update_session_analyses(self, session_id, analysis):
        """Add a new analysis to an existing session"""
        try:
            # Get current session data
            session_data = self.get_session(session_id)
            
            # If session doesn't exist, create a new one
            if not session_data:
                session_data = {
                    'created_at': datetime.datetime.now(),
                    'analyses': []
                }
            
            # Make sure analyses list exists
            if 'analyses' not in session_data:
                session_data['analyses'] = []
            
            # Add the new analysis to the list
            session_data['analyses'].append(analysis)
            
            # Save updated session back to Redis
            return self.store_session(session_id, session_data)
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def clear_session_analyses(self, session_id):
        """Remove all analyses from a session"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                # Empty the analyses list
                session_data['analyses'] = []
                return self.store_session(session_id, session_data)
            return True
        except Exception as e:
            print(f"Error clearing analyses: {e}")
            return False
    
    def delete_session(self, session_id):
        """Completely remove a session from Redis"""
        try:
            key = f"session:{session_id}"
            # Delete returns number of keys removed (1 if successful)
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_all_sessions(self):
        """Get all sessions - mainly for debugging"""
        try:
            sessions = []
            # Find all keys that start with "session:"
            keys = self.redis_client.keys("session:*")
            
            for key in keys:
                # Extract session ID from the key
                session_id = key.split(":")[1]
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
        """Store a single analysis result (no expiration)"""
        try:
            key = f"analysis:{analysis_id}"
            # Store without expiration
            self.redis_client.set(key, json.dumps(result))
            return True
        except Exception as e:
            print(f"Error storing analysis: {e}")
            return False
    
    def get_analysis_result(self, analysis_id):
        """Get a single analysis result"""
        try:
            key = f"analysis:{analysis_id}"
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting analysis: {e}")
            return None

# Create a global instance that other files can use
redis_manager = RedisManager()

# Test code that runs only if this file is executed directly
if __name__ == "__main__":
    # Test if Redis connection works
    manager = RedisManager()
    
    if manager.is_connected():
        print("Redis connection test: PASSED")
        
        # Create test session data
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
        
        # Test storing and retrieving
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