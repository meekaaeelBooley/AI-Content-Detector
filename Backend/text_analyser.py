import re
import statistics
import html
from model import AIDetectionModel

class SecurityError(Exception):
    pass

class TextAnalyser:
    # Handles text analysis including sentence splitting and AI detection
    
    MIN_SENTENCE_LENGTH = 10
    MAX_TEXT_LENGTH = 100000

    BLOCKED_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript protocol
        r'vbscript:',                # VBScript protocol
        r'on\w+\s*=',                # Event handlers (onclick, onload, etc.)
    ]
    
    def __init__(self):
        self.model = AIDetectionModel()
        
    def validate_input_length(self, text, max_length=None):
        if max_length is None:
            max_length = self.MAX_TEXT_LENGTH
        if len(text) < 10:
            raise ValueError('Text must be at least 10 characters long')
        if len(text) > max_length:
            raise ValueError(f'Text exceeds maximum length of {max_length} characters')
    
    def detect_malicious_patterns(self, text):
        # Detect potentially malicious patterns in the text (simplified)
        text_lower = text.lower()
        
        # Check for blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                raise SecurityError('Malicious pattern detected in text')
    
    def sanitize_text(self, text):
        # Basic text sanitization
        text = html.unescape(text)   
        text = text.replace('\x00', '')  # Remove null bytes
        
        # Normalize whitespace
        text = re.sub(r'\r\n|\r', '\n', text) # Normalize newlines
        text = re.sub(r'\n+', ' ', text)      # Replace multiple newlines with single space
        text = re.sub(r'\t+', ' ', text)      # Replace tabs with single space
        text = re.sub(r' +', ' ', text)       # Replace multiple spaces with single space
        
        return text.strip()
    
    def perform_security_checks(self, text):
        # Perform essential security checks on the input text
        self.validate_input_length(text)                # Basic length check
        sanitized_text = self.sanitize_text(text)       # Sanitize text
        self.validate_input_length(sanitized_text)      # Re-check length after sanitization    
        self.detect_malicious_patterns(sanitized_text)  # Malicious pattern detection
        return sanitized_text

    def split_into_sentences(self, text):
        # Split text into sentences. Returns a list of sentences with their positions in the original text.
        # Enhanced sentence splitting pattern
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s+'
        
        # Split the text
        sentences = re.split(sentence_pattern, text.strip())
        
        # Filter out empty sentences and very short ones
        valid_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= self.MIN_SENTENCE_LENGTH:
                valid_sentences.append(sentence)
        
        return valid_sentences
    
    def calculate_overall_confidence(self, sentence_results):
        # Calculate overall confidence metrics from individual sentence results.
        if not sentence_results:
            return {
                'overall_ai_probability': 0.0,
                'overall_human_probability': 1.0,
                'overall_confidence': 0.0,
                'sentence_count': 0,
                'ai_sentence_count': 0,
                'human_sentence_count': 0
            }
        
        ai_probabilities = []
        human_probabilities = []
        confidences = []
        ai_count = 0
        human_count = 0
        
        for result in sentence_results:
            if 'error' not in result:
                ai_prob = result['result']['ai_probability']
                human_prob = result['result']['human_probability']
                confidence = result['result']['confidence']
                
                ai_probabilities.append(ai_prob)
                human_probabilities.append(human_prob)
                confidences.append(confidence)
                
                if ai_prob > 0.5:
                    ai_count += 1
                else:
                    human_count += 1
        
        if not ai_probabilities:
            return {
                'overall_ai_probability': 0.0,
                'overall_human_probability': 1.0,
                'overall_confidence': 0.0,
                'sentence_count': len(sentence_results),
                'ai_sentence_count': 0,
                'human_sentence_count': 0,
                'errors': len(sentence_results)
            }
        
        # Calculate weighted averages
        overall_ai_prob = statistics.mean(ai_probabilities)
        overall_human_prob = statistics.mean(human_probabilities)
        overall_confidence = statistics.mean(confidences)
        
        return {
            'overall_ai_probability': round(overall_ai_prob, 4),
            'overall_human_probability': round(overall_human_prob, 4),
            'overall_confidence': round(overall_confidence, 4),
            'overall_classification': 'AI-generated' if overall_ai_prob > 0.5 else 'Human-written',
            'sentence_count': len(sentence_results),
            'analyzed_sentences': len(ai_probabilities),
            'ai_sentence_count': ai_count,
            'human_sentence_count': human_count,
            'ai_percentage': round((ai_count / len(ai_probabilities)) * 100, 1) if ai_probabilities else 0,
            'confidence_range': {
                'min': round(min(confidences), 4),
                'max': round(max(confidences), 4),
                'std_dev': round(statistics.stdev(confidences), 4) if len(confidences) > 1 else 0
            }
        }
    
    def analyse_sentences(self, sentences):
        # Analyse multiple sentences using AI detection. Returns results for each sentence.
        results = []
        
        for idx, sentence in enumerate(sentences):
            try:
                if len(sentence.strip()) < self.MIN_SENTENCE_LENGTH:
                    results.append({
                        'index': idx,
                        'sentence_preview': sentence,
                        'error': f'Sentence must be at least {self.MIN_SENTENCE_LENGTH} characters long'
                    })
                    continue
                
                if len(sentence) > self.MAX_TEXT_LENGTH:
                    results.append({
                        'index': idx,
                        'sentence_preview': sentence,
                        'error': f'Sentence must be less than {self.MAX_TEXT_LENGTH:,} characters'
                    })
                    continue
                
                # AI model prediction for this sentence
                prediction = self.model.predict(sentence)
                
                results.append({
                    'index': idx,
                    'sentence': sentence,
                    'sentence_length': len(sentence),
                    'result': {
                        'ai_probability': prediction['ai_probability'],
                        'human_probability': prediction['human_probability'],
                        'confidence': prediction['confidence'],
                        'classification': 'AI-generated' if prediction['ai_probability'] > 0.5 else 'Human-written'
                    }
                })
            
            except SecurityError as e:
                results.append({
                    'index': idx,
                    'sentence_preview': sentence[:100] + ('...' if len(sentence) > 100 else ''),
                    'error': f'Security error: {str(e)}'
                })
            except Exception as e:
                results.append({
                    'index': idx,
                    'sentence_preview': sentence[:100] + ('...' if len(sentence) > 100 else ''),
                    'error': str(e)
                })
        
        return results
    
    def analyse_text(self, text, source_type='text', filename=None, force_single_analysis=False):
        # Main analysis method that automatically detects whether to use single-text or sentence-level analysis and returns API-ready JSON.

        try:
            # Perform security checks and sanitize input
            text = self.perform_security_checks(text)

            # detect if multiple sentences are present
            sentences = self.split_into_sentences(text)
            enable_sentence_analysis = len(sentences) > 1 and not force_single_analysis
            
            if enable_sentence_analysis:
                # Analyse each sentence
                sentence_results = self.analyse_sentences(sentences)

                # Calculate overall metrics
                overall_metrics = self.calculate_overall_confidence(sentence_results)
                
                return {
                    'analysis_type': 'sentence_level',
                    'result': {
                        'overall_ai_probability': overall_metrics['overall_ai_probability'],
                        'overall_human_probability': overall_metrics['overall_human_probability'],
                        'overall_confidence': overall_metrics['overall_confidence'],
                        'overall_classification': overall_metrics['overall_classification'],
                        'sentence_count': overall_metrics['sentence_count'],
                        'analyzed_sentences': overall_metrics['analyzed_sentences'],
                        'ai_sentence_count': overall_metrics['ai_sentence_count'],
                        'human_sentence_count': overall_metrics['human_sentence_count'],
                        'ai_percentage': overall_metrics['ai_percentage'],
                        'confidence_range': overall_metrics['confidence_range'],
                        'text_length': len(text),
                        'source_type': source_type,
                        'filename': filename
                    },
                    'sentence_results': sentence_results,
                    # Data for session storage
                    'session_data': {
                        'sentence_analysis': sentence_results,
                        'overall_result': overall_metrics,
                        'analysis_type': 'sentence_level'
                    }
                }
            else:
                # Single text analysis
                prediction = self.model.predict(text)
                
                return {
                    'analysis_type': 'single_text',
                    'result': {
                        'ai_probability': prediction['ai_probability'],
                        'human_probability': prediction['human_probability'],
                        'confidence': prediction['confidence'],
                        'classification': 'AI-generated' if prediction['ai_probability'] > 0.5 else 'Human-written',
                        'text_length': len(text),
                        'source_type': source_type,
                        'filename': filename
                    },
                    # Data for session storage
                    'session_data': {
                        'result': prediction,
                        'analysis_type': 'single_text'
                    }
                }
        except SecurityError as e:
            raise SecurityError(f'Security check failed: {str(e)}')
        except Exception as e:
            raise Exception(f'Analysis failed: {str(e)}')