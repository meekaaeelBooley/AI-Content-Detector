from flask import Blueprint, request, jsonify, session
from functools import wraps
import uuid
import datetime
import os
import traceback
from app.services.file_processor import FileProcessor
from app.services.text_analyser import TextAnalyser
from app.database.redis_manager import redis_manager

# Create a Blueprint to organize API routes
api_bp = Blueprint('api', __name__)
# Creates a Flask Blueprint called 'api' that groups related routes together
# It's like a mini-application within the main Flask app that handles all the API endpoints

# Hardcoded API keys for authentication
API_KEYS = {"jackboys25"}

# Fallback session storage if Redis fails
session_data = {}

# Decorator to require API key for protected routes
def require_api_key(f):
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

# Decorator to ensure session exists for each request
def ensure_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create session ID if it doesn't exist
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        sid = session['session_id']
        
        # Try to get session data from Redis, create if not exists
        session_data_redis = redis_manager.get_session(sid)
        if not session_data_redis:
            session_data_redis = {
                'created_at': datetime.datetime.now(),
                'analyses': []
            }
            redis_manager.store_session(sid, session_data_redis)
        
        return f(*args, **kwargs)
    return decorated_function

# Initialize service classes for file processing and text analysis
file_processor = FileProcessor()
text_analyser = TextAnalyser()

# Health check endpoint to verify service status
@api_bp.route('/health', methods=['GET'])
def health_check():
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'supported_formats': list(FileProcessor.ALLOWED_EXTENSIONS),
        'max_file_size_kb': FileProcessor.MAX_FILE_SIZE / 1024,
        'max_text_length': TextAnalyser.MAX_TEXT_LENGTH,
        'redis_status': redis_status
    })

# Main AI detection endpoint. Accepts both text input and file uploads
@api_bp.route('/detect', methods=['POST'])
@require_api_key
@ensure_session
def detect_ai():

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
                error_msg = str(e).lower()
                if 'security' in error_msg or 'malicious' in error_msg or 'signature' in error_msg:
                    return jsonify({
                        'error': 'File security validation failed',
                        'message': str(e),
                        'type': 'security error'
                    }), 400
                elif 'timeout' in error_msg or 'timed out' in error_msg:
                    return jsonify({
                        'error': 'File processing timed out',
                        'message': str(e),
                        'type': 'timeout error'
                    }), 400
                else:
                    return jsonify({
                        'error': 'File processing failed',
                        'message': str(e),
                        'type': 'processing error'
                    }), 400
            except Exception as e:
                return jsonify({
                    'error': 'File processing failed',
                    'message': str(e),
                    'type': 'processing error'
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
        
        # Handle form data text input
        elif 'text' in request.form:
            text = request.form['text'].strip()
            source_type = 'text'
        
        else:
            return jsonify({
                'error': 'Either upload a file or provide text input'
            }), 400
        
        # Validate text content exists
        if not text:
            return jsonify({
                'error': 'No text content found'
            }), 400
        
        # Different validation for file uploads vs direct text
        if is_file_upload:
            if len(text) < 10:
                return jsonify({
                    'error': 'Extracted text must be at least 10 characters long'
                }), 400
        else:
            if len(text) < 10:
                return jsonify({
                    'error': 'Text must be at least 10 characters long'
                }), 400

            if len(text) > text_analyser.MAX_TEXT_LENGTH:
                return jsonify({
                    'error': f'Text must be less than {text_analyser.MAX_TEXT_LENGTH:,} characters'
                }), 400

        # Check if user wants to force single analysis instead of sentence-level
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

        # Generate unique ID for this analysis and prepare session storage
        analysis_id = str(uuid.uuid4())
        text_preview = text[:1000] + '...' if len(text) > 1000 else text # Limit preview to first 1000 chars
        
        session_analysis = {
            'id': analysis_id,
            'text_preview': text_preview,
            'timestamp': datetime.datetime.now(),
            'text_length': len(text),
            'source_type': source_type,
            'filename': filename,
            **analysis_result['session_data']
        }

        # Debug logging for session management
        print(f"=== SESSION DEBUG ===")
        print(f"Session ID: {session['session_id']}")
        print(f"Analysis stored with ID: {analysis_id}")
        session_data_redis = redis_manager.get_session(session['session_id'])
        
        if session_data_redis:
                print(f"Analyses in Redis: {len(session_data_redis.get('analyses', []))}")
        else:
                print("No session data found in Redis")
                print("=====================")

        # Store analysis results in Redis or fallback to memory
        try:
            if redis_manager and redis_manager.update_session_analyses(session['session_id'], session_analysis):
                print(f"{analysis_result['analysis_type']} analysis stored in Redis")
            else:
                print("Redis storage failed, falling back to in-memory session storage")
                if session['session_id'] not in session_data:
                    session_data[session['session_id']] = {'analyses': []}
                session_data[session['session_id']]['analyses'].append(session_analysis)
                print(f"{analysis_result['analysis_type']} analysis stored in session (fallback)")
                
        except Exception as e:
            print("SESSION APPEND ERROR:\n", traceback.format_exc())
            return jsonify({
                'error': 'Failed to store analysis in session',
                'message': 'Redis storage error'
            }), 500

        # Return successful analysis results
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
        print("MAIN ERROR TRACEBACK:")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Get analysis history for current session
@api_bp.route('/history', methods=['GET'])
@require_api_key
@ensure_session
def get_history():
    try:
        session_id = session['session_id']
        session_data_redis = redis_manager.get_session(session_id)
        
        # Handle case where session doesn't exist in Redis
        if not session_data_redis:
            return jsonify({
                'success': True,
                'analyses': [],
                'total_analyses': 0,
                'session_id': session_id
            })
        
        analyses = session_data_redis.get('analyses', [])
        
        # Return last 20 analyses to prevent large responses
        recent_analyses = analyses[-20:] if len(analyses) > 20 else analyses
        
        return jsonify({
            'success': True,
            'analyses': recent_analyses,
            'total_analyses': len(analyses),
            'session_id': session_id
        })
        
    except Exception as e:
        print("HISTORY ERROR TRACEBACK:")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Get specific analysis by ID
@api_bp.route('/analysis/<analysis_id>', methods=['GET'])
@require_api_key
@ensure_session
def get_analysis(analysis_id):
    try:
        session_id = session['session_id']
        session_data_redis = redis_manager.get_session(session_id)
        
        if not session_data_redis:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        analyses = session_data_redis.get('analyses', [])
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
        print("GET ANALYSIS ERROR TRACEBACK:")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Get current session information
@api_bp.route('/session', methods=['GET'])
@require_api_key
@ensure_session
def get_session_info():
    try:
        session_id = session['session_id']
        session_data_redis = redis_manager.get_session(session_id)
        
        if not session_data_redis:
            return jsonify({
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'created_at': session_data_redis.get('created_at', '').isoformat() if session_data_redis.get('created_at') else None,
            'total_analyses': len(session_data_redis.get('analyses', []))
        })
        
    except Exception as e:
        print("SESSION INFO ERROR TRACEBACK:")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Clear analysis history for current session
@api_bp.route('/clear-history', methods=['DELETE'])
@require_api_key
@ensure_session
def clear_history():
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
        print("CLEAR HISTORY ERROR TRACEBACK:")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Error handlers for common HTTP errors
@api_bp.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'File too large',
        'max_size_mb': FileProcessor.MAX_FILE_SIZE / (1024 * 1024)
    }), 413

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed'
    }), 405

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500