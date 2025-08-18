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

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change in production
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_TEXT_LENGTH = 50000  # Increased for file uploads

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# In-memory storage for session data (use Redis in production)
session_data = {}

model_path = "C:\\Users\\mubas\\OneDrive\\Desktop\\CSC 3003S\\Capstone\\checkpoint-4250"
model = AIDetectionModel(model_path)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
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
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error reading TXT file: {str(e)}")

def process_uploaded_file(file):
    """Process uploaded file and extract text"""
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
        # Clean up temp file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

def ensure_session(f):
    """Decorator to ensure each request has a session ID"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session_data[session['session_id']] = {
                'created_at': datetime.datetime.now(),
                'analyses': []
            }
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    })

@app.route('/api/detect', methods=['POST'])
@ensure_session
def detect_ai():
    """Main endpoint for AI detection - handles both text and file input"""
    try:
        text = None
        filename = None
        source_type = 'text'
        
        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            text, filename = process_uploaded_file(file)
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
        prediction = model.predict(text)
        
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
        
        session_data[session['session_id']]['analyses'].append(analysis)
        
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
@ensure_session
def batch_detect():
    """Endpoint for batch text analysis - supports multiple files or texts"""
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
                    
                    # Simulate AI model prediction
                    prediction = model.predict(text)
                    
                    analysis_id = str(uuid.uuid4())
                    analysis = {
                        'id': analysis_id,
                        'text_preview': text[:200] + ('...' if len(text) > 200 else ''),
                        'result': prediction,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'text_length': len(text),
                        'source_type': 'file',
                        'filename': filename
                    }
                    
                    session_data[session['session_id']]['analyses'].append(analysis)
                    
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
                    'timestamp': datetime.datetime.now().isoformat(),
                    'text_length': len(text),
                    'source_type': 'text',
                    'filename': None
                }
                
                session_data[session['session_id']]['analyses'].append(analysis)
                
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
@ensure_session
def get_history():
    """Get analysis history for current session"""
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
    """Get specific analysis by ID"""
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
    """Get current session information"""
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
    """Clear analysis history for current session"""
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
        'max_size_mb': MAX_FILE_SIZE / (1024 * 1024)
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