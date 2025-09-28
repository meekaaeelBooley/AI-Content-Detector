# API Caller Documentation (`api_caller.js`)

**CSC3003S Capstone Project - 2025**  
**Team: JackBoys**  
**Members:** Zubair Elliot (ELLZUB001), Mubashir Dawood (DWDMUB001), Meekaaeel Booley (BLYMEE001)

## Overview
The `api_caller.js` file provides a comprehensive HTTP client interface for communicating with the AI Content Detector backend API. It handles authentication, session management, and error handling for all frontend-backend communications.


## Key Features

- **Axios-based HTTP client** with pre-configured defaults
- **API key authentication** for all requests
- **Session persistence** via cookie handling
- **Request/response logging** for debugging
- **Comprehensive error handling** with user-friendly messages
- **File upload support** for document analysis

## Configuration

### Base URL
```javascript
// Production (commented out)
// const API_BASE_URL = 'http://16.171.92.37:5000/api';

// Development
const API_BASE_URL = 'http://127.0.0.1:5000/api';
```

### Authentication
- API key is read from environment variable `REACT_APP_API_KEY`
- Falls back to default key `'jackboys25'` if not set
- Automatically included in all request headers as `X-API-Key`

### Session Management
```javascript
withCredentials: true  // Crucial for session cookie persistence
```

## API Methods

### Core Detection Methods

#### `detectAI(text, forceSingleAnalysis)`
Analyzes text content for AI generation.

**Parameters:**
- `text` (string): Text content to analyze
- `forceSingleAnalysis` (boolean): Optional, bypasses sentence-level analysis

**Returns:** Promise with analysis results

#### `detectAIFile(file, forceSingleAnalysis)`
Uploads and analyzes document files.

**Parameters:**
- `file` (File): PDF, DOCX, or TXT file
- `forceSingleAnalysis` (boolean): Optional, bypasses sentence-level analysis

**Returns:** Promise with analysis results

### Session Management Methods

#### `getSessionInfo()`
Retrieves current session information including session ID and analysis count.

#### `getHistory()`
Gets analysis history for current session (last 20 analyses).

#### `getAnalysis(analysisId)`
Retrieves specific analysis by ID.

#### `clearHistory()`
Clears all analysis history for current session.

### Utility Methods

#### `healthCheck()`
Checks backend connectivity and API status.

#### `checkBackendConnection()`
Comprehensive backend connectivity check with user-friendly status messages.

## Error Handling

### `handleApiError(error)`
Processes API errors and returns user-friendly messages:

- **400**: Bad request - input validation failed
- **401**: Invalid API key
- **404**: Endpoint not found
- **413**: File too large (>500KB)
- **500**: Server error
- **Network**: Connection issues

## Request/Response Logging

The module includes interceptors that log:
- Request URLs and headers
- Response status codes
- Session IDs from responses
- Set-Cookie headers for session debugging

## Usage Example

```javascript
import { apiService, handleApiError } from './api_caller.js';

// Analyze text
apiService.detectAI("Sample text to analyze")
  .then(response => {
    console.log("Analysis result:", response.data);
  })
  .catch(error => {
    const errorMessage = handleApiError(error);
    console.error("Analysis failed:", errorMessage);
  });

// Check backend connection
apiService.checkBackendConnection()
  .then(status => {
    if (status.connected) {
      console.log("Backend is ready");
    }
  });
```

## Dependencies

- **axios**: HTTP client library
- **Environment variables**: `REACT_APP_API_KEY` for authentication

## Security Features

- API key authentication on all requests
- Session cookie handling for user persistence
- CORS configuration compatible with frontend origins
- Input validation and error sanitization

## File Support

The file upload method supports:
- **PDF** (.pdf)
- **Word Documents** (.docx)  
- **Text Files** (.txt)
- **Maximum size**: 500KB

