import os
import uuid
import tempfile
from werkzeug.utils import secure_filename
import PyPDF2
import docx

class FileProcessor:
    # handles file upload processing and text extraction
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self, upload_folder=None):
        self.upload_folder = upload_folder or tempfile.gettempdir()
        
    def allowed_file(self, filename):
        # Check if file extension is allowed
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def extract_text_from_pdf(self, file_path):
        # Extract text from PDF file
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ''

    def extract_text_from_docx(self, file_path):
        # Extract text from DOCX file
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
        # Extract text from TXT file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e:
                print(f"Error extracting text from TXT: {e}")
                return ''
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return ''

    def process_file(self, file):
        # Process uploaded file and extract text
        if not file or file.filename == '':
            raise ValueError("No file provided")
        
        if not self.allowed_file(file.filename):
            raise ValueError("File type not supported. Please upload PDF, DOCX, or TXT files.")
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(self.upload_folder, f"{uuid.uuid4().hex}_{filename}")
        
        try:
            file.save(file_path)
            
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_extension == 'docx':
                text = self.extract_text_from_docx(file_path)
            elif file_extension == 'txt':
                text = self.extract_text_from_txt(file_path)
            else:
                raise ValueError("Unsupported file type")
            
            os.remove(file_path)  # Clean up the saved file
            
            return text, filename
        
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e