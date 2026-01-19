"""
CSC3003S Capstone Project - AI Content Detector
Year: 2025
Author: Meekaaeel Booley

"""

import sqlite3
import json
import datetime
import os
from typing import Optional, Dict, Any, List

class SQLiteManager:
    def __init__(self, db_path='sessions.db'):
        self.db_path = db_path
        self.connected = True
        self._init_db()
        print(f"SQLiteManager initialized with database: {db_path}")
    
    def _init_db(self):
        """Initialize database and tables"""
        try:
            os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
            
            conn = self._get_connection()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    session_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            print("SQLite database initialized successfully")
        except Exception as e:
            print(f"Error initializing SQLite database: {e}")
    
    def _get_connection(self):
        """Get a new database connection"""
        return sqlite3.connect(self.db_path)
    
    def is_connected(self):
        return True
    
    def _convert_datetime_to_string(self, obj):
        """Recursively convert datetime objects to ISO format strings"""
        if isinstance(obj, dict):
            return {k: self._convert_datetime_to_string(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetime_to_string(item) for item in obj]
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return obj
    
    def _convert_string_to_datetime(self, obj):
        """Recursively convert ISO format strings back to datetime objects"""
        if isinstance(obj, dict):
            return {k: self._convert_string_to_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_string_to_datetime(item) for item in obj]
        elif isinstance(obj, str):
            try:
                return datetime.datetime.fromisoformat(obj)
            except (ValueError, TypeError):
                return obj
        else:
            return obj
    
    def store_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save session data to SQLite with comprehensive debugging"""
        try:
            print(f"DEBUG STORE: Storing session {session_id}")
            
            # Convert datetime objects to strings for JSON serialization
            session_data_serializable = self._convert_datetime_to_string(session_data)
            
            # Debug: check what we're storing
            if 'analyses' in session_data_serializable:
                print(f"DEBUG STORE: Storing {len(session_data_serializable['analyses'])} analyses")
                if session_data_serializable['analyses']:
                    print(f"DEBUG STORE: First analysis ID: {session_data_serializable['analyses'][0].get('id', 'No ID')}")
            
            conn = self._get_connection()
            conn.execute('''
                INSERT OR REPLACE INTO sessions (session_id, session_data, updated_at)
                VALUES (?, ?, ?)
            ''', (session_id, json.dumps(session_data_serializable), datetime.datetime.now()))
            conn.commit()
            conn.close()
            
            # Verify storage worked
            verified = self.get_session(session_id)
            if verified:
                print(f"DEBUG STORE: Successfully stored and verified session {session_id}")
                if 'analyses' in verified:
                    print(f"DEBUG STORE: Verified {len(verified['analyses'])} analyses in storage")
                return True
            else:
                print(f"DEBUG STORE: Failed to verify storage for session {session_id}")
                return False
            
        except Exception as e:
            print(f"Error storing session in SQLite: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from SQLite with comprehensive debugging"""
        try:
            print(f"DEBUG GET: Retrieving session {session_id}")
            
            conn = self._get_connection()
            cursor = conn.execute('SELECT session_data FROM sessions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                session_data = json.loads(row[0])
                converted_data = self._convert_string_to_datetime(session_data)
                
                # Debug: check what we retrieved
                if 'analyses' in converted_data:
                    print(f"DEBUG GET: Retrieved {len(converted_data['analyses'])} analyses for session {session_id}")
                    if converted_data['analyses']:
                        print(f"DEBUG GET: First analysis ID: {converted_data['analyses'][0].get('id', 'No ID')}")
                else:
                    print(f"DEBUG GET: No analyses key in session data for {session_id}")
                
                return converted_data
            else:
                print(f"DEBUG GET: No session found for {session_id}")
                return None
            
        except Exception as e:
            print(f"Error getting session from SQLite: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_session_analyses(self, session_id: str, analysis: Dict[str, Any]) -> bool:
        """Add a new analysis to an existing session with comprehensive debugging"""
        try:
            print(f"DEBUG UPDATE: Adding analysis to session {session_id}")
            print(f"DEBUG UPDATE: Analysis ID: {analysis.get('id', 'No ID')}")
            
            session_data = self.get_session(session_id)
            
            # If session doesn't exist, create a new one
            if not session_data:
                print(f"DEBUG UPDATE: Creating new session for {session_id}")
                session_data = {
                    'created_at': datetime.datetime.now(),
                    'analyses': []
                }
            
            # Make sure analyses list exists
            if 'analyses' not in session_data:
                print(f"DEBUG UPDATE: Initializing analyses list for {session_id}")
                session_data['analyses'] = []
            
            print(f"DEBUG UPDATE: Current analyses count: {len(session_data['analyses'])}")
            
            # Add the new analysis to the list
            session_data['analyses'].append(analysis)
            print(f"DEBUG UPDATE: New analyses count: {len(session_data['analyses'])}")
            
            # Save updated session back to SQLite
            result = self.store_session(session_id, session_data)
            print(f"DEBUG UPDATE: Store session result: {result}")
            
            return result
            
        except Exception as e:
            print(f"Error updating session analyses in SQLite: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear_session_analyses(self, session_id: str) -> bool:
        """Remove all analyses from a session"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                # Empty the analyses list but keep the session metadata
                session_data['analyses'] = []
                return self.store_session(session_id, session_data)
            return True
        except Exception as e:
            print(f"Error clearing session analyses in SQLite: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Completely remove a session from SQLite"""
        try:
            conn = self._get_connection()
            cursor = conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except Exception as e:
            print(f"Error deleting session from SQLite: {e}")
            return False
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions (mainly for debugging)"""
        try:
            sessions = []
            conn = self._get_connection()
            cursor = conn.execute('SELECT session_id, session_data FROM sessions')
            
            for row in cursor.fetchall():
                session_id, session_data_json = row
                session_data = json.loads(session_data_json)
                sessions.append({
                    'session_id': session_id,
                    'data': self._convert_string_to_datetime(session_data)
                })
            
            conn.close()
            return sessions
        except Exception as e:
            print(f"Error getting all sessions from SQLite: {e}")
            return []
    
    def store_analysis_result(self, analysis_id: str, result: Dict[str, Any]) -> bool:
        """Store a single analysis result"""
        try:
            conn = self._get_connection()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    analysis_id TEXT PRIMARY KEY,
                    result_data TEXT NOT NULL,
                    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute(
                'INSERT OR REPLACE INTO analysis_results (analysis_id, result_data) VALUES (?, ?)',
                (analysis_id, json.dumps(result))
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing analysis result in SQLite: {e}")
            return False
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get a single analysis result"""
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                'SELECT result_data FROM analysis_results WHERE analysis_id = ?', 
                (analysis_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            print(f"Error getting analysis result from SQLite: {e}")
            return None


# Create a global instance that other files can use
sqlite_manager = SQLiteManager()