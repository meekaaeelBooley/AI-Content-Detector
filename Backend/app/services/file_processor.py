import os
import tempfile
import stat
from typing import Tuple, Optional
import PyPDF2
import docx
import re
from contextlib import contextmanager

class FileValidator:
    @staticmethod
    def scan_for_malicious_patterns(file_path: str) -> bool:
        # Check if file contains dangerous code patterns
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
                # Common malicious code patterns to block
                known_malicious_patterns = [b'<script', b'javascript', b'eval(', b'<?php']
                file_content = file_content.lower()
                for pattern in known_malicious_patterns:
                    if pattern in file_content:
                        return False  # Malicious content found
            return True  # File is safe
        except Exception as e:
            print(f"Error scanning for malicious patterns: {e}")
            return True  # Assume safe if scan fails

class FilenameSanitizer:
    MAX_FILENAME_LENGTH = 100
    # Patterns that could be used for path traversal attacks
    dangerous_patterns = [r'\.\./', r'\\', r'/', r'^\.',r'[\x00-\x1f]', r'[<>:"|?*]']
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        # Clean filename to prevent security issues
        if not filename or len(filename) > FilenameSanitizer.MAX_FILENAME_LENGTH:
            return None
        
        # Remove dangerous characters and patterns
        for pattern in FilenameSanitizer.dangerous_patterns:
            filename = re.sub(pattern, '', filename)
            
        # Ensure filename has proper extension
        parts = filename.split('.')
        if len(parts) < 2:
            filename = parts[0] + '.' + parts[-1]
            
        filename = filename.strip('. ')
        
        # Final validation
        if not filename or filename.startswith('.'):
            return None
        return filename

class SecureTempFile:
    @staticmethod
    @contextmanager
    def create_secure_temp_file(suffix: str = '', prefix: str = 'secure_'):
        # Create a temporary file that gets automatically deleted
        fd = None
        file_path = None
        try:
            # Create temporary file with secure permissions
            fd, file_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # Only user can read/write
            yield fd, file_path  # Give file to caller
        finally:
            # Always clean up, even if errors occur
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if file_path and os.path.exists(file_path):
                SecureTempFile.secure_delete_file(file_path)
                
    @staticmethod
    def secure_delete_file(file_path: str) -> None:
        # Safely delete temporary file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Delete error for {file_path}: {e}")

class FileProcessor:
    # Supported file types and size limits
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    MAX_FILE_SIZE = 500 * 1024  # 500KB limit
    
    def __init__(self, upload_folder=None):
        self.upload_folder = upload_folder or tempfile.gettempdir()
        self.validate_upload_folder()
        
    def validate_upload_folder(self):
        # Ensure upload directory exists and is writable
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, mode=0o700)  # Secure permissions
        if not os.access(self.upload_folder, os.W_OK):
            raise PermissionError(f"Upload folder '{self.upload_folder}' is not writable")
        
    def allowed_file(self, filename):
        # Check if file extension is supported
        if not filename or '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.ALLOWED_EXTENSIONS

    def validate_uploaded_file(self, file) -> Tuple[bool, Optional[str]]:
        # Comprehensive file validation
        if not file or not file.filename:
            return False, "No file provided"

        if not self.allowed_file(file.filename):
            return False, "File type not supported. Please upload PDF, DOCX, or TXT files."

        sanitised_filename = FilenameSanitizer.sanitize_filename(file.filename)
        if not sanitised_filename:
            return False, "Invalid filename. Please use a simpler filename without special characters."
        
        return True, sanitised_filename

    def extract_text_from_pdf(self, file_path):
        # Extract text content from PDF files
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ''  # Return empty string on failure

    def extract_text_from_docx(self, file_path):
        # Extract text content from Word documents
        try:
            doc = docx.Document(file_path)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ''

    def extract_text_from_txt(self, file_path):
        # Extract text content from plain text files
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try alternative encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Error extracting text from TXT: {e}")
                return ''
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ''

    def process_file(self, uploaded_file, upload_folder=None):
        # Main method to handle file upload and processing
        if not uploaded_file or not uploaded_file.filename:
            raise ValueError("No file provided")
        
        # Validate file before processing
        is_valid, result = self.validate_uploaded_file(uploaded_file)
        if not is_valid:
            raise ValueError(result)
            
        filename = result
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Use secure temporary file to prevent attacks
        with SecureTempFile.create_secure_temp_file(
            suffix=f'_{filename}', 
            prefix='upload_'
        ) as (fd, file_path):
            
            try:
                # Save uploaded file to temporary location
                with os.fdopen(fd, 'wb') as temp_file:
                    uploaded_file.stream.seek(0)
                    chunk_size = 8192
                    while True:
                        chunk = uploaded_file.stream.read(chunk_size)
                        if not chunk:
                            break
                        temp_file.write(chunk)
                
                # Security check for malicious content
                if not FileValidator.scan_for_malicious_patterns(file_path):
                    raise ValueError("Security scan failed - potentially malicious content detected")
                
                # Extract text based on file type
                if file_extension == 'pdf':
                    text = self.extract_text_from_pdf(file_path)
                elif file_extension == 'docx':
                    text = self.extract_text_from_docx(file_path)
                elif file_extension == 'txt':
                    text = self.extract_text_from_txt(file_path)
                else:
                    raise ValueError("Unsupported file type")
                
                # Return extracted text and original filename
                return text, filename
            
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                raise e  # Re-raise exception for caller to handle