# File Processor Documentation

## Overview

The File Processor module provides secure file upload handling, validation, and text extraction capabilities for PDF, DOCX, and TXT files. It implements multiple layers of security validation to prevent malicious file uploads and ensures safe processing of user-submitted documents.

## Table of Contents

- [Architecture](#architecture)
- [Classes](#classes)
- [Security Features](#security-features)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Dependencies](#dependencies)

## Architecture

The module is built with a layered security approach:

1. **Input Validation Layer** - Filename sanitization and file type checking
2. **Security Validation Layer** - MIME type, file signature, and malicious pattern detection
3. **Structure Validation Layer** - Document structure verification
4. **Processing Layer** - Secure text extraction with timeout protection
5. **Cleanup Layer** - Secure temporary file deletion

## Classes

### TimeoutContext

A thread-based timeout context manager that works cross-platform including Windows.

```python
class TimeoutContext:
    def __init__(self, seconds: int)
```

**Methods:**
- `__enter__()` - Starts the timeout timer
- `__exit__()` - Cancels timer and raises TimeoutError if timed out

**Usage:**
```python
with TimeoutContext(30):
    # Operations that should timeout after 30 seconds
    pass
```

### FileValidator

Static class providing comprehensive file validation methods.

#### Supported File Types
- **PDF** (`application/pdf`)
- **DOCX** (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- **TXT** (`text/plain`)

#### Methods

##### `validate_mime_type(file_path: str, expected_extension: str) -> bool`
Validates the MIME type of a file against expected types.

**Parameters:**
- `file_path` - Path to the file to validate
- `expected_extension` - Expected file extension (pdf, docx, txt)

**Returns:** Boolean indicating if MIME type is valid

##### `validate_file_signature(file_path: str, expected_extension: str) -> bool`
Validates file signature (magic numbers) to detect file type spoofing.

**File Signatures:**
- PDF: `%PDF`
- DOCX: `PK\x03\x04` (ZIP signature)
- TXT: No specific signature

##### `scan_for_malicious_patterns(file_path: str) -> bool`
Scans file content for known malicious patterns.

**Detected Patterns:**
- `<script` - JavaScript injection
- `javascript` - JavaScript code
- `eval(` - JavaScript eval function
- `<?php` - PHP code injection

##### `validate_structure(file_path: str, expected_extension: str) -> bool`
Validates document structure by attempting to parse with appropriate libraries.

**Validation Methods:**
- **PDF**: Checks for `%PDF-` header and `%%EOF` trailer
- **DOCX**: Attempts to open with python-docx library
- **TXT**: Tests UTF-8 and Latin-1 encoding compatibility

### FilenameSanitizer

Static class for secure filename handling and path validation.

#### Configuration
- `MAX_FILENAME_LENGTH = 100` - Maximum allowed filename length
- `dangerous_patterns` - Regex patterns for dangerous characters

#### Methods

##### `sanitize_filename(filename: str) -> str`
Sanitizes filenames to prevent directory traversal and remove dangerous characters.

**Removed Patterns:**
- `../` - Directory traversal
- `\` and `/` - Path separators  
- `^\.` - Hidden files starting with dot
- `[\x00-\x1f]` - Control characters
- `[<>:"|?*]` - Windows reserved characters

**Returns:** Sanitized filename or None if invalid

### SecureTempFile

Static class providing secure temporary file operations.

#### Methods

##### `create_secure_temp_file(suffix='', prefix='secure_') -> Iterator[Tuple[int, str]]`
Context manager that creates a secure temporary file with restricted permissions.

**Security Features:**
- Owner read/write only permissions (`S_IRUSR | S_IWUSR`)
- Automatic cleanup on context exit
- Secure deletion with content overwriting

**Usage:**
```python
with SecureTempFile.create_secure_temp_file(suffix='_document.pdf') as (fd, temp_path):
    # Use temp_path for file operations
    # File is automatically cleaned up
```

##### `secure_delete_file(file_path: str) -> None`
Securely deletes a file by overwriting its content with random data.

**Process:**
1. Overwrite file content with random bytes
2. Flush and sync to disk
3. Remove file from filesystem

### FileProcessor

Main class for file processing operations.

#### Configuration
```python
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
VALIDATION_TIMEOUT = 30  # 30 seconds
```

#### Constructor
```python
def __init__(self, upload_folder=None)
```

**Parameters:**
- `upload_folder` - Custom upload directory (defaults to system temp directory)

#### Methods

##### `allowed_file(filename: str) -> bool`
Checks if file extension is in allowed list.

##### `validate_uploaded_file(file) -> Tuple[bool, Optional[str]]`
Validates uploaded file before processing.

**Returns:** Tuple of (is_valid, sanitized_filename_or_error_message)

##### `process_file(uploaded_file, upload_folder=None) -> Tuple[str, str]`
Main method for processing uploaded files.

**Process Flow:**
1. Validate uploaded file
2. Create secure temporary file
3. Save uploaded content to temporary location
4. Extract text based on file type
5. Automatic cleanup of temporary files

**Returns:** Tuple of (extracted_text, sanitized_filename)

**Raises:**
- `ValueError` - For validation failures, security issues, or processing errors

##### Text Extraction Methods

###### `extract_text_from_pdf(file_path: str) -> str`
Extracts text from PDF files using PyPDF2.

**Features:**
- Processes all pages
- Returns concatenated text with newlines
- Graceful error handling

###### `extract_text_from_docx(file_path: str) -> str`
Extracts text from DOCX files using python-docx.

**Features:**
- Processes all paragraphs
- Maintains paragraph structure
- Handles document formatting

###### `extract_text_from_txt(file_path: str) -> str`
Extracts text from TXT files with encoding detection.

**Features:**
- Primary UTF-8 encoding attempt
- Fallback to Latin-1 encoding
- Handles various text encodings

## Security Features

### Multi-Layer Validation
1. **Filename Security** - Prevents directory traversal and dangerous characters
2. **File Type Validation** - MIME type and file signature verification
3. **Content Scanning** - Detection of malicious patterns
4. **Structure Validation** - Document format integrity checks
5. **Timeout Protection** - Prevents processing of malicious files that cause hangs

### Secure File Handling
- Temporary files with restricted permissions (owner-only access)
- Secure deletion with content overwriting
- Automatic cleanup on success or failure
- Memory-safe chunk-based file operations

### Path Security
- Upload folder validation and creation
- Secure temporary file generation
- Prevention of path traversal attacks

## Usage Examples

### Basic File Processing
```python
from file_processor import FileProcessor

# Initialize processor
processor = FileProcessor()

# Process uploaded file (Flask example)
try:
    text, filename = processor.process_file(uploaded_file)
    print(f"Extracted {len(text)} characters from {filename}")
except ValueError as e:
    print(f"Processing failed: {e}")
```

### Custom Upload Directory
```python
processor = FileProcessor(upload_folder="/secure/uploads")
```

### Direct Validation
```python
from file_processor import FileValidator

# Validate file security
if not FileValidator.validate_mime_type("/path/to/file.pdf", "pdf"):
    print("MIME type validation failed")

if not FileValidator.scan_for_malicious_patterns("/path/to/file.pdf"):
    print("Malicious content detected")
```

### Secure Temporary Files
```python
from file_processor import SecureTempFile

with SecureTempFile.create_secure_temp_file(suffix='_processing.tmp') as (fd, temp_path):
    # Use temp_path for secure file operations
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
    # File automatically cleaned up here
```

## Error Handling

The module uses `ValueError` exceptions with descriptive messages for different error types:

### Security Errors
- `"File signature validation failed - file may be corrupted or malicious"`
- `"MIME type validation failed - file type mismatch"`
- `"Security scan failed - potentially malicious content detected"`

### Processing Errors
- `"No file provided"`
- `"File type not supported. Please upload PDF, DOCX, or TXT files."`
- `"Invalid filename. Please use a simpler filename without special characters."`
- `"File validation timed out - file may be too complex"`

### Structure Errors
- `"Invalid {extension} document structure"`

## Configuration

### Environment Variables
```python
# Optional: Set custom secret key
SECRET_KEY = "your-secret-key-here"
```

### File Size Limits
```python
# Default: 5MB maximum file size
MAX_FILE_SIZE = 5 * 1024 * 1024

# Configure in Flask app
app.config['MAX_CONTENT_LENGTH'] = FileProcessor.MAX_FILE_SIZE
```

### Timeout Settings
```python
# Default: 30 seconds validation timeout
VALIDATION_TIMEOUT = 30
```

## Dependencies

### Required Libraries
```python
import os
import uuid
import tempfile
import stat
import magic              # python-magic for MIME type detection
import mimetypes
import re
from typing import Dict, Set, Tuple, Optional, Iterator
from werkzeug.utils import secure_filename
import PyPDF2            # PDF text extraction
import docx              # DOCX text extraction
from threading import Timer
from contextlib import contextmanager
```

### System Requirements
- **python-magic** - Requires libmagic system library
  - **Linux**: `sudo apt-get install libmagic1`
  - **macOS**: `brew install libmagic`
  - **Windows**: Included with python-magic-bin

### Installation
```bash
pip install PyPDF2 python-docx python-magic werkzeug
In wsl:
sudo apt install python3-magic
```

## Performance Considerations

### Memory Usage
- Files are processed in 8KB chunks to handle large files efficiently
- Temporary files are used instead of loading entire files into memory
- Automatic cleanup prevents memory leaks

### Processing Speed
- Timeout protection prevents indefinite processing
- Efficient validation order (quick checks first)
- Minimal file I/O operations

### Scalability
- Thread-safe design for concurrent requests
- Secure temporary file isolation
- Configurable timeout and size limits

## Security Best Practices

### Deployment Recommendations
1. **Run with minimal privileges** - Use dedicated service account
2. **Isolate upload directory** - Separate from application code
3. **Monitor file processing** - Log security events and errors
4. **Regular updates** - Keep dependencies updated for security patches
5. **Resource limits** - Configure appropriate timeouts and file size limits

### Integration Guidelines
1. **Validate before processing** - Always use `validate_uploaded_file()`
2. **Handle exceptions** - Implement proper error handling for all methods
3. **Log security events** - Monitor for potential attacks
4. **Rate limiting** - Implement upload rate limiting in your application
5. **Virus scanning** - Consider additional antivirus integration for production

## Troubleshooting

### Common Issues

#### "Magic number" errors
- Ensure libmagic is properly installed
- On Windows, install python-magic-bin instead of python-magic

#### Permission errors
- Check upload directory permissions
- Ensure temporary directory is writable
- Run application with appropriate user privileges

#### Timeout errors
- Increase `VALIDATION_TIMEOUT` for large files
- Check system resources (CPU, memory)
- Monitor for potentially malicious files causing hangs

#### Encoding errors (TXT files)
- Files are tested with UTF-8 first, then Latin-1
- Consider adding additional encoding support if needed

### Debug Mode
Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License and Support

This file processor module is designed for secure file handling in web applications. For production deployments, ensure proper security testing and monitoring are in place.
