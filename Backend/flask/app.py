from flask import Flask, request, jsonify, session
from model import AIDetectionModel
from flask_cors import CORS
import uuid
import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import tempfile
import traceback
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

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 5000  # Increased for file uploads

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize the AI detection model
model = AIDetectionModel()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file using PyPDF2"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path):
    """Extract text from DOCX file using python-docx"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_path):
    """Extract text from TXT file with encoding fallback"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error reading TXT file: {str(e)}")

def process_uploaded_file(file):
    """
    Process uploaded file and extract text.
    Handles multiple file types and ensures proper cleanup of temp files.
    """
    if not file or file.filename == '':
        raise ValueError("No file selected")
    
    if not allowed_file(file.filename):
        raise ValueError("File type not supported. Please upload PDF, DOCX, or TXT files.")
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    
    try:
        file.save(file_path)
        
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            text = extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            text = extract_text_from_txt(file_path)
        else:
            raise ValueError("Unsupported file type")
        
        # Clean up temp file
        os.remove(file_path)
        
        return text, filename
        
    except Exception as e:
        # Clean up temp file if it exists (important for security)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

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
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
        'redis_status': redis_status
    })

@app.route('/api/detect', methods=['POST'])
@require_api_key
@ensure_session
def detect_ai():
    """
    Main endpoint for AI detection - handles both text and file input.
    Now stores session data in Redis instead of in-memory.
    """
    try:
        text = None
        filename = None
        source_type = 'text'
        
        # Check if it's a file upload (multipart/form-data)
        if 'file' in request.files:
            file = request.files['file']
            text, filename = process_uploaded_file(file)
            source_type = 'file'
        
        # Check if it's JSON text input (application/json)
        elif request.is_json:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({
                    'error': 'Either upload a file or provide text field in JSON'
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
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text must be less than {MAX_TEXT_LENGTH:,} characters'
            }), 400

        # Get AI model prediction
        try:
            prediction = model.predict(text)
        except Exception as e:
            print("MODEL ERROR TRACEBACK:")
            print(traceback.format_exc())
            return jsonify({
                'error': 'Model prediction failed',
                'message': str(e)
            }), 500

        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        analysis = {
            'id': analysis_id,
            'text_preview': text[:200] + ('...' if len(text) > 200 else ''),
            'result': prediction,
            'timestamp': datetime.datetime.now(),
            'text_length': len(text),
            'source_type': source_type,
            'filename': filename
        }

        # Store analysis in Redis instead of in-memory session_data
        if not redis_manager.update_session_analyses(session['session_id'], analysis):
            return jsonify({
                'error': 'Failed to store analysis in session',
                'message': 'Redis storage error'
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

@app.route('/api/batch-detect', methods=['POST'])
@require_api_key
@ensure_session
def batch_detect():
    """
    Endpoint for batch text analysis - supports multiple files or texts.
    Now uses Redis for session storage.
    """
    try:
        results = []
        
        # Handle multiple file uploads
        if 'files' in request.files:
            files = request.files.getlist('files')
            
            if len(files) > 10:
                return jsonify({
                    'error': 'Maximum 10 files allowed per batch'
                }), 400
            
            for idx, file in enumerate(files):
                try:
                    text, filename = process_uploaded_file(file)
                    
                    if len(text) < 10:
                        results.append({
                            'index': idx,
                            'filename': filename,
                            'error': 'Text must be at least 10 characters long'
                        })
                        continue
                    
                    if len(text) > MAX_TEXT_LENGTH:
                        results.append({
                            'index': idx,
                            'filename': filename,
                            'error': f'Text must be less than {MAX_TEXT_LENGTH:,} characters'
                        })
                        continue
                    
                    # AI model prediction
                    prediction = model.predict(text)
                    
                    analysis_id = str(uuid.uuid4())
                    analysis = {
                        'id': analysis_id,
                        'text_preview': text[:200] + ('...' if len(text) > 200 else ''),
                        'result': prediction,
                        'timestamp': datetime.datetime.now(),
                        'text_length': len(text),
                        'source_type': 'file',
                        'filename': filename
                    }
                    
                    # Store in Redis instead of in-memory
                    if not redis_manager.update_session_analyses(session['session_id'], analysis):
                        results.append({
                            'index': idx,
                            'filename': filename,
                            'error': 'Failed to store analysis in session'
                        })
                        continue
                    
                    results.append({
                        'index': idx,
                        'analysis_id': analysis_id,
                        'filename': filename,
                        'result': {
                            'ai_probability': prediction['ai_probability'],
                            'human_probability': prediction['human_probability'],
                            'confidence': prediction['confidence'],
                            'classification': 'AI-generated' if prediction['ai_probability'] > 0.5 else 'Human-written',
                            'text_length': len(text)
                        }
                    })
                    
                except Exception as e:
                    results.append({
                        'index': idx,
                        'filename': file.filename if file else 'unknown',
                        'error': str(e)
                    })
        
        # Handle JSON array of texts
        elif request.is_json:
            data = request.get_json()
            
            if not data or 'texts' not in data:
                return jsonify({
                    'error': 'texts field is required (array of strings)'
                }), 400
            
            texts = data['texts']
            
            if not isinstance(texts, list) or len(texts) == 0:
                return jsonify({
                    'error': 'texts must be a non-empty array'
                }), 400
            
            if len(texts) > 10:
                return jsonify({
                    'error': 'Maximum 10 texts allowed per batch'
                }), 400
            
            for idx, text in enumerate(texts):
                if not isinstance(text, str):
                    results.append({
                        'index': idx,
                        'error': 'Text must be a string'
                    })
                    continue
                    
                text = text.strip()
                
                if len(text) < 10:
                    results.append({
                        'index': idx,
                        'error': 'Text must be at least 10 characters long'
                    })
                    continue
                
                if len(text) > MAX_TEXT_LENGTH:
                    results.append({
                        'index': idx,
                        'error': f'Text must be less than {MAX_TEXT_LENGTH:,} characters'
                    })
                    continue

                prediction = model.predict(text)

                analysis_id = str(uuid.uuid4())
                analysis = {
                    'id': analysis_id,
                    'text_preview': text[:200] + ('...' if len(text) > 200 else ''),
                    'result': prediction,
                    'timestamp': datetime.datetime.now(),
                    'text_length': len(text),
                    'source_type': 'text',
                    'filename': None
                }
                
                # Store in Redis instead of in-memory
                if not redis_manager.update_session_analyses(session['session_id'], analysis):
                    results.append({
                        'index': idx,
                        'error': 'Failed to store analysis in session'
                    })
                    continue
                
                results.append({
                    'index': idx,
                    'analysis_id': analysis_id,
                    'result': {
                        'ai_probability': prediction['ai_probability'],
                        'human_probability': prediction['human_probability'],
                        'confidence': prediction['confidence'],
                        'classification': 'AI-generated' if prediction['ai_probability'] > 0.5 else 'Human-written',
                        'text_length': len(text)
                    }
                })
        
        else:
            return jsonify({
                'error': 'Either upload files or provide texts array in JSON'
            }), 400
        
        return jsonify({
            'success': True,
            'results': results,
            'session_id': session['session_id']
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
@require_api_key
@ensure_session
def get_history():
    """
    Get analysis history for current session from Redis.
    Returns last 20 analyses to prevent excessive data transfer.
    """
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
    """
    Get specific analysis by ID from Redis session data.
    """
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
    """
    Get current session information from Redis.
    """
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
    """
    Clear analysis history for current session in Redis.
    """
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
    """Handle file size limit exceeded errors"""
    return jsonify({
        'error': 'File too large',
        'max_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Check Redis connection before starting
    if not redis_manager.is_connected():
        print("WARNING: Redis connection failed. Sessions will not be persisted.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)