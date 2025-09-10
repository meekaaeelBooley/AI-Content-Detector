from flask import Flask, request, jsonify, session
from flask_cors import CORS
import uuid
import datetime
from functools import wraps
import os
import traceback
from file_processor import FileProcessor
from text_analyser import TextAnalyser
from functools import wraps

# Import the Redis manager we created
from redis_manager import redis_manager

# pip install torch transformers flask flask-cors PyPDF2 python-docx werkzeug redis

API_KEYS = {"jackboys25"}

def require_api_key(f):
    """
    Decorator to require API key authentication.
    Checks for API key in headers (X-API-Key) or query parameters (api_key).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers or query parameters
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key or api_key not in API_KEYS:
            return jsonify({
                'error': 'Valid API key required',
                'message': 'Use X-API-Key header or api_key query parameter'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change in production
CORS(app)

app.config['UPLOAD_FOLDER'] = FileProcessor().upload_folder
app.config['MAX_CONTENT_LENGTH'] = FileProcessor.MAX_FILE_SIZE

# In-memory session data as a fallback if Redis is unavailable
session_data = {}

file_processor = FileProcessor()
text_analyser = TextAnalyser()

def ensure_session(f):
    """
    Decorator to ensure each request has a valid session.
    Creates new session in Redis if it doesn't exist.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        sid = session['session_id']
        
        # Check if session exists in Redis, create if not
        # This replaces the in-memory session_data dictionary
        session_data = redis_manager.get_session(sid)
        if not session_data:
            session_data = {
                'created_at': datetime.datetime.now(),
                'analyses': []
            }
            redis_manager.store_session(sid, session_data)
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with system information"""
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'supported_formats': list(FileProcessor.ALLOWED_EXTENSIONS),
        'max_file_size_mb': FileProcessor.MAX_FILE_SIZE / (1024 * 1024),
        'redis_status': redis_status
    })

@app.route('/api/detect', methods=['POST'])
@require_api_key
@ensure_session
def detect_ai():
    # Main endpoint for AI detection - handles both text and file input
    try:
        text = None
        filename = None
        source_type = 'text'
        
        # Check if it's a file upload (multipart/form-data)
        if 'file' in request.files:
            file = request.files['file']
            text, filename = file_processor.process_file(file)
            source_type = 'file'
        
        # Check if it's JSON text input (application/json)
        elif request.is_json:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({
                    'error': 'Provide text field in JSON'
                }), 400
            text = data['text'].strip()
            source_type = 'text'
        
        # Check if it's form text input (application/x-www-form-urlencoded)
        elif 'text' in request.form:
            text = request.form['text'].strip()
            source_type = 'text'
        
        else:
            return jsonify({
                'error': 'Either upload a file or provide text input'
            }), 400
        
        if not text:
            return jsonify({
                'error': 'No text content found'
            }), 400
        
        if len(text) < 10:
            return jsonify({
                'error': 'Text must be at least 10 characters long'
            }), 400

        if len(text) > text_analyser.MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text must be less than {text_analyser.MAX_TEXT_LENGTH:,} characters'
            }), 400

        # Check for force_single_analysis flag
        force_single_analysis = False
        if request.is_json and request.get_json().get('force_single_analysis', False):
            force_single_analysis = True
        elif 'force_single_analysis' in request.form:
            force_single_analysis = True
        
        # Analyze the text
        try:
            analysis_result = text_analyser.analyse_text(
                text, 
                source_type=source_type, 
                filename=filename, 
                force_single_analysis=force_single_analysis
            )
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print("ANALYSIS ERROR TRACEBACK:")
            print(traceback.format_exc())
            return jsonify({
                'error': 'Text analysis failed',
                'message': str(e)
            }), 500

        # Store analysis in session data
        analysis_id = str(uuid.uuid4())
        
        # Build session storage data
        session_analysis = {
            'id': analysis_id,
            'text_preview': text[:200] + ('...' if len(text) > 200 else ''),
            'timestamp': datetime.datetime.now(),
            'text_length': len(text),
            'source_type': source_type,
            'filename': filename,
            **analysis_result['session_data']  # Merge in the analysis-specific data
        }

        # Store analysis in Redis instead of in-memory session_data
        try:
            # Primary storage: Redis
            if redis_manager and redis_manager.update_session_analyses(session['session_id'], session_analysis):
                print(f"{analysis_result['analysis_type']} analysis stored in Redis")
            else:
                # Fallback to in-memory storage if Redis fails
                print("Redis storage failed, falling back to in-memory session storage")
                session_data[session['session_id']]['analyses'].append(session_analysis)
                print(f"{analysis_result['analysis_type']} analysis stored in session (fallback)")
                
        except Exception as e:
            print("SESSION APPEND ERROR:\n", traceback.format_exc())
            return jsonify({
                'error': 'Failed to store analysis in session',
                'message': 'Redis storage error'
            }), 500

        # Return the API response (already formatted by TextAnalyzer)
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'analysis_type': analysis_result['analysis_type'],
            'result': analysis_result['result'],
            **({'sentence_results': analysis_result['sentence_results']} if 'sentence_results' in analysis_result else {}),
            'session_id': session['session_id']
        })
        
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
@require_api_key
@ensure_session
def get_history():
    # Get analysis history for current session
    try:
        session_id = session['session_id']
        session_data = redis_manager.get_session(session_id)
        
        # Handle case where session doesn't exist in Redis (shouldn't happen with ensure_session)
        if not session_data:
            return jsonify({
                'success': True,
                'analyses': [],
                'total_analyses': 0,
                'session_id': session_id
            })
        
        analyses = session_data.get('analyses', [])
        
        # Return last 20 analyses to prevent large responses
        recent_analyses = analyses[-20:] if len(analyses) > 20 else analyses
        
        return jsonify({
            'success': True,
            'analyses': recent_analyses,
            'total_analyses': len(analyses),
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@require_api_key
@ensure_session
def get_analysis(analysis_id):
    # Get specific analysis by ID
    try:
        session_id = session['session_id']
        session_data = redis_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        analyses = session_data.get('analyses', [])
        analysis = next((a for a in analyses if a['id'] == analysis_id), None)
        
        if not analysis:
            return jsonify({
                'error': 'Analysis not found'
            }), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/session', methods=['GET'])
@require_api_key
@ensure_session
def get_session_info():
    # Get current session information
    try:
        session_id = session['session_id']
        session_data = redis_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'created_at': session_data.get('created_at', '').isoformat() if session_data.get('created_at') else None,
            'total_analyses': len(session_data.get('analyses', []))
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/clear-history', methods=['DELETE'])
@require_api_key
@ensure_session
def clear_history():
    # Clear analysis history for current session
    try:
        session_id = session['session_id']
        if not redis_manager.clear_session_analyses(session_id):
            return jsonify({
                'error': 'Failed to clear history'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'History cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'File too large',
        'max_size_mb': FileProcessor.MAX_FILE_SIZE / (1024 * 1024)
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

if __name__ == '__main__':
    # Check Redis connection before starting
    if not redis_manager.is_connected():
        print("WARNING: Redis connection failed. Sessions will not be persisted.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)