# AI Detection API Documentation

This Flask API provides AI content detection capabilities, supporting both text input and file uploads (PDF, DOCX, TXT). The API uses Redis for session management and requires API key authentication.

## Setup and Configuration

### Prerequisites
- Redis server running (for session management)
- API key configured as environment variable
- Required Python packages (Flask, Redis, etc.)

### Environment Variables
```bash
export API_KEY="your-api-key-here"
export SECRET_KEY="your-secret-key-here"
export REDIS_URL="redis://localhost:6379/0"  # Optional, defaults to localhost
```

### Starting the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000` by default.

## Authentication

All API endpoints (except health check) require authentication using an API key.

### Methods:
1. **Header**: `X-API-Key: your-api-key`
2. **Query Parameter**: `?api_key=your-api-key`

### Error Response (401):
```json
{
    "error": "Valid API key required",
    "message": "Use X-API-Key header or api_key query parameter"
}
```

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running and get system status (no authentication required).

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-15T10:30:00.123456",
    "supported_formats": ["txt", "pdf", "docx"],
    "max_file_size_mb": 5.0,
    "redis_status": "connected"
}
```

---

### 2. AI Detection
**POST** `/api/detect`

Detect AI content in text or uploaded file. Supports both single analysis and sentence-by-sentence analysis.

#### Authentication Required:
- Header: `X-API-Key: your-api-key`
- Or query parameter: `?api_key=your-api-key`

#### Input Options:

**Option 1: JSON Text Input**
```json
{
    "text": "Your text content here...",
    "force_single_analysis": false  // optional, defaults to false
}
```

**Option 2: Form Text Input**
```
Content-Type: application/x-www-form-urlencoded

text=Your text content here...
force_single_analysis=true  // optional
```

**Option 3: File Upload**
```
Content-Type: multipart/form-data

file: [PDF/DOCX/TXT file]
force_single_analysis: true  // optional form field
```

#### Response (Single Analysis):
```json
{
    "success": true,
    "analysis_id": "uuid-string",
    "analysis_type": "single",
    "result": {
        "ai_probability": 0.85,
        "human_probability": 0.15,
        "confidence": 0.85,
        "classification": "AI-generated",
        "text_length": 1250,
        "source_type": "text",
        "filename": null
    },
    "session_id": "session-uuid"
}
```

#### Response (Sentence Analysis):
```json
{
    "success": true,
    "analysis_id": "uuid-string",
    "analysis_type": "sentence",
    "result": {
        "overall_ai_probability": 0.72,
        "overall_human_probability": 0.28,
        "overall_confidence": 0.72,
        "overall_classification": "AI-generated",
        "text_length": 1250,
        "source_type": "file",
        "filename": "document.pdf",
        "sentence_count": 8
    },
    "sentence_results": [
        {
            "sentence": "First sentence text...",
            "ai_probability": 0.65,
            "human_probability": 0.35,
            "confidence": 0.65,
            "classification": "AI-generated"
        }
    ],
    "session_id": "session-uuid"
}
```

#### Error Responses:
```json
{
    "error": "Text must be at least 10 characters long"
}
```

```json
{
    "error": "Text must be less than 50,000 characters"
}
```

---

### 3. Analysis History
**GET** `/api/history`

Get the analysis history for the current session (last 20 analyses).

#### Authentication Required:
- Header: `X-API-Key: your-api-key`

#### Response:
```json
{
    "success": true,
    "analyses": [
        {
            "id": "analysis-uuid",
            "text_preview": "First 200 characters of analyzed text...",
            "timestamp": "2025-01-15T10:30:00.123456",
            "text_length": 1200,
            "source_type": "file",
            "filename": "document.pdf",
            "analysis_type": "sentence",
            "overall_result": {
                "ai_probability": 0.65,
                "human_probability": 0.35,
                "confidence": 0.65,
                "classification": "AI-generated"
            }
        }
    ],
    "total_analyses": 15,
    "session_id": "session-uuid"
}
```

---

### 4. Get Specific Analysis
**GET** `/api/analysis/{analysis_id}`

Retrieve details for a specific analysis by its ID.

#### Authentication Required:
- Header: `X-API-Key: your-api-key`

#### Response:
```json
{
    "success": true,
    "analysis": {
        "id": "analysis-uuid",
        "text_preview": "First 200 characters...",
        "timestamp": "2025-01-15T10:30:00.123456",
        "text_length": 950,
        "source_type": "text",
        "filename": null,
        "analysis_type": "single",
        "overall_result": {
            "ai_probability": 0.78,
            "human_probability": 0.22,
            "confidence": 0.78,
            "classification": "AI-generated"
        }
    }
}
```

#### Error Response:
```json
{
    "error": "Analysis not found"
}
```

---

### 5. Session Information
**GET** `/api/session`

Get information about the current session.

#### Authentication Required:
- Header: `X-API-Key: your-api-key`

#### Response:
```json
{
    "success": true,
    "session_id": "session-uuid",
    "created_at": "2025-01-15T09:00:00.123456",
    "total_analyses": 8
}
```

---

### 6. Clear History
**DELETE** `/api/clear-history`

Clear all analysis history for the current session.

#### Authentication Required:
- Header: `X-API-Key: your-api-key`

#### Response:
```json
{
    "success": true,
    "message": "History cleared successfully"
}
```

---

## File Upload Requirements

### Supported Formats
- **PDF** (.pdf)
- **Word Document** (.docx)  
- **Text File** (.txt)

### Limitations
- Maximum file size: Configured in `FileProcessor.MAX_FILE_SIZE`
- Maximum text length: Configured in `TextAnalyser.MAX_TEXT_LENGTH`
- Minimum text length: 10 characters

### Text Extraction
The API automatically extracts text from uploaded files using the `FileProcessor` class.

---

## Session Management

The API uses Redis for persistent session management:
- Each user gets a unique session ID stored in Flask session cookies
- Analysis history is stored in Redis with session-based keys
- Sessions persist across server restarts
- Fallback to in-memory storage if Redis is unavailable

### Redis Configuration
- Default connection: `redis://localhost:6379/0`
- Override with `REDIS_URL` environment variable
- Sessions expire based on Redis configuration

---

## Analysis Types

### Single Analysis (`force_single_analysis=true`)
- Analyzes the entire text as one unit
- Faster processing
- Single probability score for the whole text

### Sentence Analysis (default)
- Splits text into individual sentences
- Analyzes each sentence separately
- Provides both overall and per-sentence results
- More detailed insights but slower processing

---

## Error Handling

### Common Error Codes

**400 Bad Request**
- Invalid input format
- Text too short/long  
- Unsupported file type
- Missing required fields

**401 Unauthorized**
- Missing or invalid API key

**404 Not Found**
- Analysis ID not found
- Session not found
- Invalid endpoint

**413 Payload Too Large**
- File size exceeds configured limit

**500 Internal Server Error**
- Text analysis failure
- Redis connection issues
- File processing errors

### Error Response Format
```json
{
    "error": "Description of the error",
    "message": "Additional details (for 500 errors)"
}
```

---

## Example Usage

### Python Example
```python
import requests

# Headers with API key
headers = {'X-API-Key': 'your-api-key-here'}

# Text analysis
response = requests.post('http://localhost:5000/api/detect', 
                        headers=headers,
                        json={'text': 'Your text here'})
result = response.json()

# File upload with sentence analysis
with open('document.pdf', 'rb') as f:
    response = requests.post('http://localhost:5000/api/detect',
                           headers=headers,
                           files={'file': f})
result = response.json()

# Single analysis mode
response = requests.post('http://localhost:5000/api/detect',
                        headers=headers,
                        json={
                            'text': 'Your text here',
                            'force_single_analysis': True
                        })
result = response.json()

# Get history
response = requests.get('http://localhost:5000/api/history',
                       headers=headers)
history = response.json()
```

### JavaScript Example
```javascript
// Headers with API key
const headers = {
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json'
};

// Text analysis
const response = await fetch('/api/detect', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        text: 'Your text here',
        force_single_analysis: false
    })
});
const result = await response.json();

// File upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
const response = await fetch('/api/detect', {
    method: 'POST',
    headers: {'X-API-Key': 'your-api-key-here'},
    body: formData
});
const result = await response.json();
```

### cURL Example
```bash
# Text analysis
curl -X POST http://localhost:5000/api/detect \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text content here"}'

# File upload
curl -X POST http://localhost:5000/api/detect \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@document.pdf"

# Get history
curl -X GET http://localhost:5000/api/history \
  -H "X-API-Key: your-api-key-here"
```

---

## Development Notes

### Dependencies
- `FileProcessor`: Handles file upload and text extraction
- `TextAnalyser`: Performs AI detection analysis
- `RedisManager`: Manages Redis connections and session storage

### Architecture
- Flask application with CORS enabled
- Redis for session persistence with in-memory fallback
- Decorator-based authentication and session management
- Structured error handling with proper HTTP status codes
