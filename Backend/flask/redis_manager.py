import redis
import json
import datetime
from typing import Dict, List, Any, Optional

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """Establish connection to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True  # Automatically decode responses to strings
            )
            # Test connection
            self.redis_client.ping()
            print("Redis connection established successfully")
        except redis.ConnectionError as e:
            print(f"Redis connection failed: {e}")
            raise
    
    def is_connected(self):
        """Check if Redis is connected"""
        try:
            return self.redis_client.ping()
        except:
            return False
    
    def store_session(self, session_id: str, session_data: Dict[str, Any], expire_hours: int = 8):
        """Store session data with expiration"""
        try:
            key = f"session:{session_id}"
            # Convert datetime objects to strings for JSON serialization
            if 'created_at' in session_data and isinstance(session_data['created_at'], datetime.datetime):
                session_data['created_at'] = session_data['created_at'].isoformat()
            
            # Convert analyses timestamps
            if 'analyses' in session_data:
                for analysis in session_data['analyses']:
                    if 'timestamp' in analysis and isinstance(analysis['timestamp'], datetime.datetime):
                        analysis['timestamp'] = analysis['timestamp'].isoformat()
            
            self.redis_client.setex(
                key,
                expire_hours * 3600,  # Convert hours to seconds
                json.dumps(session_data)
            )
            return True
        except Exception as e:
            print(f"Error storing session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
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
            print(f"Error retrieving session: {e}")
            return None
    
    def update_session_analyses(self, session_id: str, analysis: Dict[str, Any]):
        """Add analysis to session and update Redis"""
        try:
            session_data = self.get_session(session_id)
            if not session_data:
                # Create new session if it doesn't exist
                session_data = {
                    'created_at': datetime.datetime.now(),
                    'analyses': []
                }
            
            # Ensure analyses list exists
            if 'analyses' not in session_data:
                session_data['analyses'] = []
            
            # Add new analysis
            session_data['analyses'].append(analysis)
            
            # Store updated session
            return self.store_session(session_id, session_data)
        except Exception as e:
            print(f"Error updating session analyses: {e}")
            return False
    
    def clear_session_analyses(self, session_id: str):
        """Clear all analyses for a session"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                session_data['analyses'] = []
                return self.store_session(session_id, session_data)
            return True
        except Exception as e:
            print(f"Error clearing session analyses: {e}")
            return False
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        try:
            key = f"session:{session_id}"
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions (for debugging/admin purposes)"""
        try:
            sessions = []
            keys = self.redis_client.keys("session:*")
            for key in keys:
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
    
    def store_analysis_result(self, analysis_id: str, result: Dict[str, Any], expire_hours: int = 24):
        """Store individual analysis result with expiration"""
        try:
            key = f"analysis:{analysis_id}"
            self.redis_client.setex(
                key,
                expire_hours * 3600,
                json.dumps(result)
            )
            return True
        except Exception as e:
            print(f"Error storing analysis result: {e}")
            return False
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve individual analysis result"""
        try:
            key = f"analysis:{analysis_id}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error retrieving analysis result: {e}")
            return None

# Global Redis manager instance
redis_manager = RedisManager()

# For testing
if __name__ == "__main__":
    # Test Redis connection
    manager = RedisManager()
    
    if manager.is_connected():
        print("Redis connection test: PASSED")
        
        # Test session storage
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
        
        manager.store_session('test-session', test_session)
        retrieved = manager.get_session('test-session')
        print(f"Session storage test: {'PASSED' if retrieved else 'FAILED'}")
        
        # Clean up
        manager.delete_session('test-session')
    else:
        print("Redis connection test: FAILED")