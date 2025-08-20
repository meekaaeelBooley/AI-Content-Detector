# AI Detection API Documentation

This Flask API provides AI content detection capabilities, supporting both text input and file uploads (PDF, DOCX, TXT).

## Setup and Configuration

### Model Path Configuration

To test locally or change the model path, update the following line in `app.py`:

```python
# Line 26 in app.py
model_path = "C:\\Model"
```

Replace this path with your local model directory path.

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the API is running and get configuration information.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-15T10:30:00.123456",
    "supported_formats": ["txt", "pdf", "docx"],
    "max_file_size_mb": 16
}
```

---

### 2. AI Detection (Single Text/File)
**POST** `/api/detect`

Detect AI content in a single text or uploaded file.

#### Input Options:

**Option 1: JSON Text Input**
```json
{
    "text": "Your text content here..."
}
```

**Option 2: Form Text Input**
```
Content-Type: application/x-www-form-urlencoded

text=Your text content here...
```

**Option 3: File Upload**
```
Content-Type: multipart/form-data

file: [PDF/DOCX/TXT file]
```

#### Response:
```json
{
    "success": true,
    "analysis_id": "uuid-string",
    "result": {
        "ai_probability": 0.85,
        "human_probability": 0.15,
        "confidence": 0.85,
        "classification": "AI-generated",
        "text_length": 1250,
        "source_type": "text",  // or "file"
        "filename": "document.pdf"  // only for file uploads
    },
    "session_id": "session-uuid"
}
```

#### Error Responses:
```json
{
    "error": "Text must be at least 10 characters long"
}
```

---

### 3. Batch AI Detection
**POST** `/api/batch-detect`

Analyze multiple texts or files in a single request.

#### Input Options:

**Option 1: Multiple Files**
```
Content-Type: multipart/form-data

files: [file1.pdf, file2.docx, file3.txt, ...]
```

**Option 2: JSON Array of Texts**
```json
{
    "texts": [
        "First text to analyze...",
        "Second text to analyze...",
        "Third text to analyze..."
    ]
}
```

#### Response:
```json
{
    "success": true,
    "results": [
        {
            "index": 0,
            "analysis_id": "uuid-1",
            "filename": "document1.pdf",  // for file uploads
            "result": {
                "ai_probability": 0.72,
                "human_probability": 0.28,
                "confidence": 0.72,
                "classification": "AI-generated",
                "text_length": 890
            }
        },
        {
            "index": 1,
            "error": "Text must be at least 10 characters long"
        }
    ],
    "session_id": "session-uuid"
}
```

#### Limitations:
- Maximum 10 files/texts per batch
- Each text must be 10-50,000 characters
- File size limit: 16MB per file

---

### 4. Analysis History
**GET** `/api/history`

Get the analysis history for the current session (last 20 analyses).

#### Response:
```json
{
    "success": true,
    "analyses": [
        {
            "id": "analysis-uuid",
            "text_preview": "First 200 characters of analyzed text...",
            "result": {
                "ai_probability": 0.65,
                "human_probability": 0.35,
                "confidence": 0.65
            },
            "timestamp": "2025-01-15T10:30:00.123456",
            "text_length": 1200,
            "source_type": "file",
            "filename": "document.pdf"
        }
    ],
    "total_analyses": 15,
    "session_id": "session-uuid"
}
```

---

### 5. Get Specific Analysis
**GET** `/api/analysis/{analysis_id}`

Retrieve details for a specific analysis by its ID.

#### Response:
```json
{
    "success": true,
    "analysis": {
        "id": "analysis-uuid",
        "text_preview": "First 200 characters...",
        "result": {
            "ai_probability": 0.78,
            "human_probability": 0.22,
            "confidence": 0.78
        },
        "timestamp": "2025-01-15T10:30:00.123456",
        "text_length": 950,
        "source_type": "text",
        "filename": null
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

### 6. Session Information
**GET** `/api/session`

Get information about the current session.

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

### 7. Clear History
**DELETE** `/api/clear-history`

Clear all analysis history for the current session.

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
- Maximum file size: 10MB
- Maximum text length: 5000 characters
- Minimum text length: 10 characters

### Text Extraction
The API automatically extracts text from uploaded files:
- **PDF**: Uses PyPDF2 to extract text from all pages
- **DOCX**: Extracts text from all paragraphs
- **TXT**: Reads file content with UTF-8 encoding (falls back to latin-1)

---

## Session Management

The API uses Flask sessions to track user activity:
- Each user gets a unique session ID
- Analysis history is stored per session
- Sessions are maintained using browser cookies
- Session data is stored in memory (use Redis for production)

---

## Error Handling

### Common Error Codes

**400 Bad Request**
- Invalid input format
- Text too short/long
- Unsupported file type
- Missing required fields

**404 Not Found**
- Analysis ID not found
- Invalid endpoint

**413 Payload Too Large**
- File size exceeds 10MB limit

**500 Internal Server Error**
- Model prediction failure
- File processing error
- Server configuration issues

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

# Text analysis
response = requests.post('http://localhost:5000/api/detect', 
                        json={'text': 'Your text here'})
result = response.json()

# File upload
with open('document.pdf', 'rb') as f:
    response = requests.post('http://localhost:5000/api/detect', 
                           files={'file': f})
result = response.json()

# Batch analysis
response = requests.post('http://localhost:5000/api/batch-detect',
                        json={'texts': ['Text 1', 'Text 2', 'Text 3']})
results = response.json()
```

### JavaScript Example
```javascript
// Text analysis
const response = await fetch('/api/detect', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: 'Your text here'})
});
const result = await response.json();

// File upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
const response = await fetch('/api/detect', {
    method: 'POST',
    body: formData
});
const result = await response.json();
```

---

## Development Notes

### Model Integration
The API uses the `AIDetectionModel` class from `model.py`. The model is loaded once during application startup for efficiency.

### Session Storage
Currently uses in-memory storage. For production deployment, consider:
- Redis for session storage
- Database for persistent analysis history
- Proper session cleanup mechanisms

### Security Considerations
- Change the secret key in production
- Implement rate limiting
- Add authentication if needed
- Validate file types more strictly
- Implement virus scanning for uploaded files