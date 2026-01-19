"""
CSC3003S Capstone Project - AI Content Detector
Year: 2025
Authors: Meekaaeel Booley(BLYMEE001), Mubashir Dawood(DWDMUB001), 

This Flask backend follows a typical REST API structure with these key components:

    1. Authentication: Uses API keys (basic protection) and session management
    2. File Processing: Handles PDF, DOCX, and TXT file uploads
    3. AI Detection: Uses a pre-trained model ( electra) to analyze text for AI/human classification
    4. Session Storage: SQLite for persistence with memory fallback
    5. Error Handling: Comprehensive error handling for different scenarios

The main flow for AI detection:

    -User submits text or file
    -Validate input
    -Split into sentences (if long)
    -Run AI model on each
    -Aggregate results
    -Store in session
    -Return JSON response

Key design choices:

    - Sentence-level analysis for better accuracy on long texts
    - Session-based history to track user analyses
    - CORS enabled for frontend communication
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import uuid
import datetime
from functools import wraps
import os
from services.file_processor import FileProcessor
from services.text_analyser import TextAnalyser
from services.sqlite_manager import sqlite_manager

# API keys for basic authentication... in a non-academic project we'd use environment variables
API_KEYS = {"jackboys25"}

# Decorator to require API key for protected routes
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers or query parameters
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key or api_key not in API_KEYS:
            return jsonify({
                'error': 'Valid API key required'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configure upload settings from FileProcessor class
app.config['UPLOAD_FOLDER'] = FileProcessor().upload_folder
app.config['MAX_CONTENT_LENGTH'] = FileProcessor.MAX_FILE_SIZE

# Session security settings
app.config.update(
    SESSION_COOKIE_SECURE=False,       # Should be True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE='Lax',         # CSRF protection
    PERMANENT_SESSION_LIFETIME=86400,  # 24 hours
    SESSION_REFRESH_EACH_REQUEST=True,
)

# Enable CORS for frontend communication
CORS(app, 
     supports_credentials=True,
     origins=[
         "http://localhost:5173", 
         "http://localhost:3000", 
         "http://127.0.0.1:3000", 
         "http://localhost:4173", 
         "http://16.171.92.37",
         "https://staging.d1ye07gtovsf9d.amplifyapp.com",
         "https://app.aicd.online",  
         "https://api.aicd.online",
         "https://d1ye07gtovsf9d.amplifyapp.com"
     ],
     allow_headers=["Content-Type", "X-API-Key", "X-Session-ID", "Cookie", "Set-Cookie", "Access-Control-Allow-Credentials"],
     expose_headers=["Set-Cookie", "X-Session-ID"],
     methods=["GET", "POST", "DELETE", "OPTIONS"])

# Fallback session storage if SQLite fails
session_data = {}

# Initialize our main service classes
file_processor = FileProcessor()
text_analyser = TextAnalyser()

# Decorator to ensure session exists for each request - FIXED VERSION
def ensure_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session ID in multiple places - prioritize custom header
        session_id = None
        
        # 1. First, check for custom header (for localStorage approach)
        if 'X-Session-ID' in request.headers:
            session_id = request.headers['X-Session-ID']
            print(f"DEBUG: Using session ID from X-Session-ID header: {session_id}")
            # Store it in Flask session for consistency
            session['session_id'] = session_id
        
        # 2. Check if we already have a session in Flask session
        elif 'session_id' in session:
            session_id = session['session_id']
            print(f"DEBUG: Found session ID in Flask session: {session_id}")
        
        # 3. Check cookies (standard way) - Flask's session cookie
        elif request.cookies.get('session'):
            # Flask uses its own session cookie named 'session'
            # We'll extract from it or create new
            print(f"DEBUG: Found Flask session cookie")
            # Let Flask handle its own session - we'll create our own session_id
        
        # 4. Create new if none exists
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"DEBUG: Creating new session ID: {session_id}")
            session['session_id'] = session_id
        
        # Store the session ID in request for easy access
        request.session_id = session_id
        
        # Try to get session from SQLite, create if not exists
        session_data_sqlite = sqlite_manager.get_session(session_id)
        if not session_data_sqlite:
            print(f"DEBUG: Creating new session in SQLite for ID: {session_id}")
            session_data_sqlite = {
                'created_at': datetime.datetime.now(),
                'analyses': []
            }
            sqlite_manager.store_session(session_id, session_data_sqlite)
        else:
            print(f"DEBUG: Found existing session in SQLite with {len(session_data_sqlite.get('analyses', []))} analyses")
        
        # Store session data in request context for easy access
        request.session_data = session_data_sqlite
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check endpoint to verify API is running"""
    db_status = "connected" if sqlite_manager.is_connected() else "disconnected"
    db_type = "SQLite"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'supported_formats': list(FileProcessor.ALLOWED_EXTENSIONS),
        'max_file_size_kb': FileProcessor.MAX_FILE_SIZE / 1024,
        'max_text_length': TextAnalyser.MAX_TEXT_LENGTH,
        'database_status': db_status,
        'database_type': db_type
    })

@app.route('/api/detect', methods=['POST'])
@require_api_key
@ensure_session
def detect_ai():
    """Main endpoint for AI detection... accepts both file uploads and raw text"""
    try:
        text = None
        filename = None
        source_type = 'text'
        is_file_upload = False
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            try:
                text, filename = file_processor.process_file(file)
                source_type = 'file'
                is_file_upload = True
            except ValueError as e:
                return jsonify({
                    'error': str(e)
                }), 400
            except Exception as e:
                return jsonify({
                    'error': 'File processing failed'
                }), 400
        
        # Handle JSON text input
        elif request.is_json:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({
                    'error': 'Provide text field in JSON'
                }), 400
            text = data['text'].strip()
            source_type = 'text'
        
        # Handle form-encoded text input
        elif 'text' in request.form:
            text = request.form['text'].strip()
            source_type = 'text'
        
        else:
            return jsonify({
                'error': 'Either upload a file or provide text input'
            }), 400
        
        # Validate we actually got some text
        if not text:
            return jsonify({
                'error': 'No text content found'
            }), 400
        
        # Different validation for files vs direct text input
        if is_file_upload:
            if len(text) < 10:
                return jsonify({
                    'error': 'Extracted text must be at least 10 characters long'
                }), 400
        else:
            word_count = len(text.split())
            if word_count < 10:
                return jsonify({
                    'error': 'Text must be at least 10 words long'
                }), 400

            if len(text) > text_analyser.MAX_TEXT_LENGTH:
                return jsonify({
                    'error': f'Text must be less than {text_analyser.MAX_TEXT_LENGTH:,} characters'
                }), 400

        # Check if user wants to force single analysis (ignore sentence splitting)
        force_single_analysis = False
        if request.is_json and request.get_json().get('force_single_analysis', False):
            force_single_analysis = True
        elif 'force_single_analysis' in request.form:
            force_single_analysis = True
        
        # Perform the actual AI detection analysis
        try:
            analysis_result = text_analyser.analyse_text(
                text, 
                source_type=source_type, 
                filename=filename, 
                force_single_analysis=force_single_analysis,
            )
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({
                'error': 'Text analysis failed'
            }), 500

        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Prepare session data for storage
        session_analysis = {
            'id': analysis_id,
            'text_preview': text[:500] + ('...' if len(text) > 500 else ''),  # Limit preview length
            'timestamp': datetime.datetime.now(),
            'text_length': len(text),
            'source_type': source_type,
            'filename': filename,
            **analysis_result['session_data']  # Merge analysis results
        }

        # Debug output to help with development
        print(f"=== SESSION DEBUG ===")
        print(f"Session ID: {request.session_id}")
        print(f"Analysis stored with ID: {analysis_id}")
        
        # Get current session to check before update
        session_data_sqlite = sqlite_manager.get_session(request.session_id)
        if session_data_sqlite:
            print(f"Analyses in SQLite BEFORE update: {len(session_data_sqlite.get('analyses', []))}")
        else:
            print("No session data found in SQLite before update")
        print("=====================")

        # Store analysis in session (SQLite preferred, fallback to memory)
        try:
            if sqlite_manager and sqlite_manager.update_session_analyses(request.session_id, session_analysis):
                print(f"{analysis_result['analysis_type']} analysis stored in SQLite")
                
                # Verify storage worked
                updated_session = sqlite_manager.get_session(request.session_id)
                if updated_session:
                    print(f"Analyses in SQLite AFTER update: {len(updated_session.get('analyses', []))}")
                    if updated_session.get('analyses'):
                        print(f"Latest analysis ID: {updated_session['analyses'][-1].get('id', 'No ID')}")
            else:
                print("SQLite storage failed, falling back to in-memory session storage")
                if request.session_id not in session_data:
                    session_data[request.session_id] = {'analyses': []}
                session_data[request.session_id]['analyses'].append(session_analysis)
                print(f"{analysis_result['analysis_type']} analysis stored in session (fallback)")
                
        except Exception as e:
            print(f"Error storing analysis: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Failed to store analysis in session'
            }), 500

        # Return success response with analysis results - INCLUDING SESSION ID
        response_data = {
            'success': True,
            'analysis_id': analysis_id,
            'analysis_type': analysis_result['analysis_type'],
            'result': analysis_result['result'],
            'session_id': request.session_id  # CRITICAL: Always include session ID
        }
        
        # Add sentence results if available
        if 'sentence_results' in analysis_result:
            response_data['sentence_results'] = analysis_result['sentence_results']
            
        return jsonify(response_data)
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"Unexpected error in /detect: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/history', methods=['GET'])
@require_api_key
@ensure_session
def get_history():
    """Get analysis history for current session"""
    try:
        session_id = request.session_id
        print(f"DEBUG HISTORY: Getting history for session: {session_id}")
        
        session_data_sqlite = sqlite_manager.get_session(session_id)
        
        if not session_data_sqlite:
            print(f"DEBUG HISTORY: No session data found for {session_id}")
            return jsonify({
                'success': True,
                'analyses': [],
                'total_analyses': 0,
                'session_id': session_id
            })
        
        # Make sure we're getting the analyses list
        analyses = session_data_sqlite.get('analyses', [])
        print(f"DEBUG HISTORY: Retrieved {len(analyses)} analyses from SQLite for session {session_id}")
        
        if analyses:
            print(f"DEBUG HISTORY: First analysis ID: {analyses[0].get('id', 'No ID')}")
            print(f"DEBUG HISTORY: Last analysis ID: {analyses[-1].get('id', 'No ID')}")
        
        # Return only recent analyses to avoid huge responses
        recent_analyses = analyses[-20:] if len(analyses) > 20 else analyses
        
        return jsonify({
            'success': True,
            'analyses': recent_analyses,
            'total_analyses': len(analyses),
            'session_id': session_id  # Include session ID in response
        })
        
    except Exception as e:
        print(f"Error in get_history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@require_api_key
@ensure_session
def get_analysis(analysis_id):
    """Get specific analysis by ID"""
    try:
        session_id = request.session_id
        session_data_sqlite = sqlite_manager.get_session(session_id)
        
        if not session_data_sqlite:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        analyses = session_data_sqlite.get('analyses', [])
        # Find the specific analysis by ID
        analysis = next((a for a in analyses if a['id'] == analysis_id), None)
        
        if not analysis:
            return jsonify({
                'error': 'Analysis not found'
            }), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error in get_analysis: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/session', methods=['GET'])
@require_api_key
@ensure_session
def get_session_info():
    """Get basic session information"""
    try:
        session_id = request.session_id
        session_data_sqlite = sqlite_manager.get_session(session_id)
        
        if not session_data_sqlite:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        analyses_count = len(session_data_sqlite.get('analyses', []))
        
        return jsonify({
            'success': True,
            'session_id': session_id,  # Always include session ID
            'created_at': session_data_sqlite.get('created_at', '').isoformat() if session_data_sqlite.get('created_at') else None,
            'total_analyses': analyses_count
        })
        
    except Exception as e:
        print(f"Error in get_session_info: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/clear-history', methods=['DELETE'])
@require_api_key
@ensure_session
def clear_history():
    """Clear all analysis history for current session"""
    try:
        session_id = request.session_id
        print(f"DEBUG CLEAR: Clearing history for session: {session_id}")
        
        if not sqlite_manager.clear_session_analyses(session_id):
            return jsonify({
                'error': 'Failed to clear history'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'History cleared successfully',
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error in clear_history: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/debug/sessions', methods=['GET'])
@require_api_key
def debug_sessions():
    """Debug endpoint to see all sessions (for development only)"""
    try:
        all_sessions = sqlite_manager.get_all_sessions()
        
        simplified_sessions = []
        for s in all_sessions:
            session_data = s['data']
            simplified_sessions.append({
                'session_id': s['session_id'],
                'analysis_count': len(session_data.get('analyses', [])),
                'created_at': session_data.get('created_at'),
                'data_size': len(str(session_data))
            })
        
        return jsonify({
            'success': True,
            'total_sessions': len(all_sessions),
            'sessions': simplified_sessions
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/debug/session/<session_id>', methods=['GET'])
@require_api_key
def debug_session_detail(session_id):
    """Debug endpoint to see specific session details"""
    try:
        session_data = sqlite_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        # Create a safe version without full text
        safe_data = {
            'session_id': session_id,
            'created_at': session_data.get('created_at'),
            'analysis_count': len(session_data.get('analyses', [])),
            'analyses_preview': []
        }
        
        for i, analysis in enumerate(session_data.get('analyses', [])[:5]):  # Limit to 5
            safe_data['analyses_preview'].append({
                'index': i,
                'id': analysis.get('id'),
                'text_preview': analysis.get('text_preview', '')[:100] + ('...' if len(analysis.get('text_preview', '')) > 100 else ''),
                'text_length': analysis.get('text_length', 0),
                'source_type': analysis.get('source_type')
            })
        
        return jsonify({
            'success': True,
            'session': safe_data
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
        
# Error handlers for common HTTP errors
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'File too large'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500
