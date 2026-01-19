# AI Content Detector (AICD) Backend

**CSC3003S Capstone Project - 2025**  
**Team: JackBoys**  
**Members:** Zubair Elliot (ELLZUB001), Mubashir Dawood (DWDMUB001), Meekaaeel Booley (BLYMEE001)

A Flask-based REST API that uses machine learning to detect AI-generated vs human-written text. The system provides both single-text analysis and intelligent sentence-level analysis for longer documents.

## Features

- **AI Detection**: Pre-trained Electra transformer model for high-accuracy text classification
- **File Support**: PDF, DOCX, and TXT file processing with automatic text extraction
- **Sentence-Level Analysis**: Intelligent splitting and analysis of longer texts for better accuracy
- **Session Management**: SQLite-based persistent storage of analysis history
- **Comprehensive API**: RESTful endpoints with proper authentication and error handling
- **Batch Processing**: Support for analyzing multiple texts or sentences simultaneously

## Technology Stack

- **Backend**: Flask (Python 3.8+)
- **AI Model**: Electra transformer (via Hugging Face Transformers)
- **Database**: SQLite for session storage
- **File Processing**: PyPDF2 (PDF), python-docx (Word), custom text handlers
- **Authentication**: API key-based authentication
- **CORS**: Configured for frontend communication

## Project Structure

```
aicd-backend/
├── api/
│   └── app.py                 # Main Flask application with API endpoints
├── services/
│   ├── __init__.py            # Package initialization
│   ├── model.py               # AI detection model wrapper
│   ├── text_analyser.py       # Text processing and analysis logic
│   ├── file_processor.py      # File upload and text extraction
│   └── sqlite_manager.py      # SQLite session management
├── ai_detector_model/         # Pre-trained model files (not in repo)
├── install_quick.ps1          # Windows setup script
├── run.py                     # Application entry point
├── sessions.db                # SQLite database (created on first run)
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Windows (for PowerShell scripts) or Linux/macOS

### Quick Setup (Windows PowerShell)

```powershell
# Run the automated setup script
.\install_quick.ps1
```

This script will:
1. Create a Python virtual environment
2. Install all required Python packages
3. Download PyTorch CPU version

### Manual Setup

1. **Clone the repository and set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Python dependencies:**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers flask flask-cors PyPDF2 python-docx werkzeug
```

3. **Download the AI model:**
Place the pre-trained model files in `ai_detector_model/` directory at the project root.

## Running the Application

### Quick Start (Windows)
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application
python run.py
```

### Manual Start
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run the application
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

All endpoints require an API key sent as `X-API-Key` header or `api_key` query parameter.

**Default API Key:** `jackboys25`

### Core Endpoints

#### Health Check
```http
GET /api/health
```
Returns API status and configuration information including database status.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-19T10:30:00",
    "supported_formats": ["txt", "pdf", "docx"],
    "max_file_size_kb": 500,
    "max_text_length": 100000,
    "database_status": "connected",
    "database_type": "SQLite"
}
```

#### Text Analysis
```http
POST /api/detect
Content-Type: application/json
X-API-Key: jackboys25

{
    "text": "Your text to analyze here",
    "force_single_analysis": false
}
```

#### File Upload Analysis
```http
POST /api/detect
Content-Type: multipart/form-data
X-API-Key: jackboys25

file: [PDF/DOCX/TXT file]
```

#### Session Management
```http
GET /api/session           # Get session info
GET /api/history          # Get analysis history (last 20)
GET /api/analysis/{id}    # Get specific analysis by ID
DELETE /api/clear-history # Clear session history
```

#### Debug Endpoints (Development Only)
```http
GET /api/debug/sessions              # View all sessions
GET /api/debug/session/{session_id}  # View specific session details
```

### Session ID Handling

The backend supports multiple methods for session tracking:

1. **Custom Header (Recommended)**: Send `X-Session-ID` header with your session ID
2. **Flask Session Cookie**: Automatic session cookie management
3. **Auto-generation**: New session ID created if none provided

All API responses include the `session_id` field for client-side tracking.

### Response Format

#### Single Text Analysis
```json
{
    "success": true,
    "analysis_id": "uuid-here",
    "analysis_type": "single_text",
    "session_id": "session-uuid",
    "result": {
        "ai_probability": 0.8234,
        "human_probability": 0.1766,
        "confidence": 0.8234,
        "classification": "AI-generated",
        "text_length": 150,
        "source_type": "text",
        "filename": null
    }
}
```

#### Sentence-Level Analysis
```json
{
    "success": true,
    "analysis_id": "uuid-here",
    "analysis_type": "sentence_level",
    "session_id": "session-uuid",
    "result": {
        "overall_ai_probability": 0.7456,
        "overall_human_probability": 0.2544,
        "overall_confidence": 0.8123,
        "overall_classification": "AI-generated",
        "sentence_count": 4,
        "analyzed_sentences": 4,
        "ai_sentence_count": 3,
        "human_sentence_count": 1,
        "ai_percentage": 75.0,
        "confidence_range": {
            "min": 0.6789,
            "max": 0.9234,
            "std_dev": 0.1023
        },
        "text_length": 450,
        "source_type": "text",
        "filename": null
    },
    "sentence_results": [
        {
            "index": 0,
            "sentence_preview": "First sentence preview...",
            "sentence_length": 120,
            "result": {
                "ai_probability": 0.9234,
                "human_probability": 0.0766,
                "confidence": 0.9234,
                "classification": "AI-generated"
            }
        }
    ]
}
```

#### History Response
```json
{
    "success": true,
    "session_id": "session-uuid",
    "total_analyses": 15,
    "analyses": [
        {
            "id": "analysis-uuid",
            "text_preview": "Preview of analyzed text...",
            "timestamp": "2025-01-19T10:30:00",
            "text_length": 450,
            "source_type": "text",
            "filename": null,
            "result": { /* analysis results */ }
        }
    ]
}
```

## Configuration

### File Upload Limits
- **Maximum file size:** 500KB
- **Supported formats:** PDF, DOCX, TXT
- **Text length limit:** 100,000 characters
- **Minimum text length:** 10 words (direct text input) or 10 characters (file upload)

### Model Configuration
- **Model type:** Electra transformer
- **Maximum sequence length:** 512 tokens
- **Device:** CPU (configurable for GPU in `model.py`)
- **Model path:** `./ai_detector_model` (configurable in `model.py`)

### SQLite Configuration
- **Database file:** `sessions.db` (created automatically in project root)
- **Session persistence:** Indefinite (academic use)
- **Fallback:** In-memory storage if SQLite fails
- **Auto-migration:** Database schema created on first run

### CORS Configuration
Configured origins include:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (React dev server)
- `http://127.0.0.1:3000`
- `http://localhost:4173` (Vite preview)
- `http://16.171.92.37`
- `https://staging.d1ye07gtovsf9d.amplifyapp.com`
- `https://app.aicd.online` (Production)
- `https://api.aicd.online` (Production API)
- `https://d1ye07gtovsf9d.amplifyapp.com`

## Testing

### Model Tests
```bash
python tests/test_model.py
```
Tests core AI detection functionality including:
- Basic prediction accuracy
- Confidence calculation
- Batch processing
- Edge cases (empty text, very long text)
- Consistency checks

### Direct Model Testing
```bash
python services/model.py
```
Runs standalone model tests with sample sentences to verify model functionality.

## Architecture

### Analysis Pipeline

1. **Input Validation**: Check text length, file format, security
2. **Session Management**: Ensure session exists, retrieve or create
3. **Text Extraction**: Extract text from uploaded files (if applicable)
4. **Sentence Detection**: Smart splitting for multi-sentence texts
5. **AI Classification**: Run transformer model on each sentence
6. **Result Aggregation**: Combine sentence-level results
7. **Session Storage**: Save analysis to SQLite with unique ID
8. **Response Generation**: Return structured JSON response with session ID

### Sentence-Level Analysis

For texts with multiple sentences, the system:
- Uses regex-based sentence splitting (handles abbreviations like "Dr.", "Mr.", "U.S.A.")
- Analyzes each sentence independently
- Calculates weighted averages for overall scores
- Provides detailed per-sentence breakdown
- Handles mixed AI/human content accurately
- Automatically triggered for 2+ sentences (unless `force_single_analysis=True`)
- Filters out sentences shorter than 10 characters

### Session Management (SQLite)

- Each user gets a unique session ID (UUID)
- All analyses stored persistently in SQLite database
- Session data includes full text preview (500 chars), timestamps, and results
- Automatic datetime conversion for JSON serialization
- Comprehensive debugging with detailed logging
- Fallback to in-memory storage if SQLite unavailable
- API provides history retrieval and individual analysis lookup

### Session ID Flow

```
Client Request → Check X-Session-ID header → Use existing or create new
                ↓
         Store in Flask session
                ↓
    Retrieve/Create SQLite session data
                ↓
         Process analysis request
                ↓
    Store analysis in SQLite session
                ↓
    Return response with session_id
```

## Development

### Adding New File Types
1. Update `ALLOWED_EXTENSIONS` in `FileProcessor`
2. Add extraction method in `file_processor.py`
3. Update file type routing in `process_file()`

### Model Customization
1. Replace model files in `ai_detector_model/`
2. Update `model_path` in `model.py` (line 23)
3. Adjust confidence thresholds if needed
4. Test with `python services/model.py`

### API Extensions
1. Add new endpoints in `app.py`
2. Use `@require_api_key` decorator for authentication
3. Use `@ensure_session` for session-dependent endpoints
4. Follow existing error handling patterns

### Database Schema

**Sessions Table:**
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    session_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

Session data JSON structure:
```json
{
    "created_at": "ISO datetime",
    "analyses": [
        {
            "id": "uuid",
            "text_preview": "...",
            "timestamp": "ISO datetime",
            "text_length": 450,
            "source_type": "text|file",
            "filename": "optional",
            "result": { /* analysis results */ }
        }
    ]
}
```

## Production Deployment

### Security Considerations
- Change default API keys (update `API_KEYS` set in `app.py`)
- Use environment variables for secrets (`SECRET_KEY`)
- Enable HTTPS (set `SESSION_COOKIE_SECURE=True`)
- Configure proper CORS origins (update `origins` list)
- Add rate limiting
- Implement proper logging
- Secure file upload directory

### Performance Optimization
- Use GPU for model inference (update `device` in `model.py`)
- Add caching for repeated analyses
- Implement connection pooling for SQLite
- Add request queuing for high loads
- Consider model quantization
- Optimize sentence splitting for very long documents

### Monitoring
- Monitor SQLite database file size
- Track analysis accuracy over time
- Log performance bottlenecks
- Monitor session creation rate
- Track API endpoint usage

### Environment Variables

Recommended environment variables:
```bash
SECRET_KEY=your-production-secret-key-here
DEBUG=False
```

## Troubleshooting

### Common Issues

**Model loading fails:**
- Ensure `ai_detector_model/` directory exists with all required files
- Check Python path and working directory
- Verify sufficient RAM for model loading (~2GB recommended)
- Check console output for specific model loading errors

**SQLite connection fails:**
- Check write permissions in application directory
- Verify `sessions.db` file can be created
- Application will fall back to in-memory storage (with warning)
- Check debug output: "SQLite database connected successfully"

**Session not persisting:**
- Check browser is sending `X-Session-ID` header
- Verify CORS configuration allows credentials
- Check SQLite is connected (not using fallback)
- Review debug output in `/api/detect` response

**File upload errors:**
- Check file size under 500KB limit
- Verify file format is PDF, DOCX, or TXT
- Ensure sufficient disk space for temporary files
- Check `tempfile` module has write permissions

**Analysis accuracy concerns:**
- Very short texts (under 10 words) may be unreliable
- Mixed AI/human content benefits from sentence-level analysis
- Model works best with complete sentences and proper grammar
- File extraction quality depends on source file format

**CORS errors:**
- Verify frontend URL is in `origins` list
- Check `supports_credentials=True` for session cookies
- Ensure proper headers in frontend requests
- Review browser console for specific CORS errors

## Known Limitations

- Text analysis limited to 100,000 characters
- File uploads limited to 500KB
- CPU-based inference (slower than GPU)
- Sentence splitting may occasionally split incorrectly on complex punctuation
- Very short sentences (under 10 characters) are filtered out
- Debug mode is set to `False` in production (`run.py`)

## License

This project is developed for academic purposes as part of CSC3003S coursework at the University of Cape Town.

## Support

For questions or issues, contact the development team:
- Zubair Elliot (ELLZUB001)
- Mubashir Dawood (DWDMUB001)
- Meekaaeel Booley (BLYMEE001)