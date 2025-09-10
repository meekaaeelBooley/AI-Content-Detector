from flask import Flask, request, jsonify, session
from model import AIDetectionModel
from flask_cors import CORS
import uuid
import datetime
from functools import wraps
import os
import traceback
from file_processor import FileProcessor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change in production
CORS(app)

# Configuration
MAX_TEXT_LENGTH = 5000  # Increased for file uploads
MIN_SENTENCE_LENGTH = 5 

app.config['UPLOAD_FOLDER'] = FileProcessor.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = FileProcessor.MAX_FILE_SIZE

# In-memory storage for session data (use Redis in production)
session_data = {}

file_processor = FileProcessor()
model = AIDetectionModel()

def ensure_session(f):
    # Decorator to ensure each request has a session ID
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        sid = session['session_id']
        if sid not in session_data:
            session_data[sid] = {
                'created_at': datetime.datetime.now(),
                'analyses': []
            }
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    # Health check endpoint
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'supported_formats': list(FileProcessor.ALLOWED_EXTENSIONS),
        'max_file_size_mb': FileProcessor.MAX_FILE_SIZE / (1024 * 1024)
    })

@app.route('/api/detect', methods=['POST'])
@ensure_session
def detect_ai():
    # Main endpoint for AI detection - handles both text and file input 
    try:
        text = None
        filename = None
        source_type = 'text'
        
        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            text, filename = file_processor.process_uploaded_file(file)
            source_type = 'file'
        
        # Check if it's JSON text input
        elif request.is_json:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({
                    'error': 'Either upload a file or provide text field in JSON'
                }), 400
            text = data['text'].strip()
            source_type = 'text'
        
        # Check if it's form text input
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
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text must be less than {MAX_TEXT_LENGTH:,} characters'
            }), 400

        # Simulate AI model prediction
        try:
            prediction = model.predict(text)
        except Exception as e:
            print("MODEL ERROR TRACEBACK:")
            print(traceback.format_exc())
            return jsonify({
                'error': 'Model prediction failed',
                'message': str(e)
            }), 500

        
        # Store analysis in session data
        analysis_id = str(uuid.uuid4())
        analysis = {
            'id': analysis_id,
            'text_preview': text[:200] + ('...' if len(text) > 200 else ''),
            'result': prediction,
            'timestamp': datetime.datetime.now().isoformat(),
            'text_length': len(text),
            'source_type': source_type,
            'filename': filename
        }

        try:
            session_data[session['session_id']]['analyses'].append(analysis)
            print("Analysis stored in session")
        except Exception as e:
            print("SESSION APPEND ERROR:\n", traceback.format_exc())
            return jsonify({
                'error': 'Failed to store analysis in session',
                'message': str(e)
            }), 500

        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'result': {
                'ai_probability': prediction['ai_probability'],
                'human_probability': prediction['human_probability'],
                'confidence': prediction['confidence'],
                'classification': 'AI-generated' if prediction['ai_probability'] > 0.5 else 'Human-written',
                'text_length': len(text),
                'source_type': source_type,
                'filename': filename
            },
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
@ensure_session
def get_history():
    # Get analysis history for current session
    try:
        session_id = session['session_id']
        analyses = session_data.get(session_id, {}).get('analyses', [])
        
        # Return last 20 analyses
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
@ensure_session
def get_analysis(analysis_id):
    # Get specific analysis by ID
    try:
        session_id = session['session_id']
        analyses = session_data.get(session_id, {}).get('analyses', [])
        
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
@ensure_session
def get_session_info():
    # Get current session information
    try:
        session_id = session['session_id']
        session_info = session_data.get(session_id, {})
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'created_at': session_info.get('created_at', '').isoformat() if session_info.get('created_at') else None,
            'total_analyses': len(session_info.get('analyses', []))
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/clear-history', methods=['DELETE'])
@ensure_session
def clear_history():
    # Clear analysis history for current session
    try:
        session_id = session['session_id']
        if session_id in session_data:
            session_data[session_id]['analyses'] = []
        
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
    app.run(debug=True, host='0.0.0.0', port=5000)