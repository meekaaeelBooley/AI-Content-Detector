import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AIDetectionModel:
    def __init__(self, model_path):
        # Initialize the AI detection model with the given path
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        
        # Set up device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, text):
        # Predict whether text is AI-generated or human-written
        # Returns a dictionary with probabilities and confidence

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

            probabilities = F.softmax(logits, dim=-1)
            
            # Extract individual probabilities
            human_prob = probabilities[0][0].item()   # Class 0 (human)
            ai_prob = probabilities[0][1].item()      # Class 1 (ai)
            
            # Calculate confidence score (probability of predicted class)
            confidence_score = max(human_prob, ai_prob)
        
        return {
            'human_probability': human_prob,
            'ai_probability': ai_prob,
            'confidence': confidence_score
        }
    
    def predict_with_confidence(self, text):
        # Predict with additional confidence level categorization
        result = self.predict(text)
        
        prediction = 1 if result['ai_probability'] > result['human_probability'] else 0
        confidence_score = result['confidence']
        
        # Determine confidence level
        if confidence_score >= 0.9:
            confidence_level = "Very High"
        elif confidence_score >= 0.8:
            confidence_level = "High"
        elif confidence_score >= 0.7:
            confidence_level = "Medium"
        elif confidence_score >= 0.6:
            confidence_level = "Low"
        else:
            confidence_level = "Very Low"
        
        # Create label map
        label_map = {0: "human", 1: "ai"}
        predicted_class = label_map[prediction]
        
        return {
            'prediction': predicted_class,
            'confidence_level': confidence_level,
            'confidence_score': confidence_score,
            'human_probability': result['human_probability'],
            'ai_probability': result['ai_probability']
        }
    
    def batch_predict(self, texts):
        # Predict for multiple texts
        results = []
        for text in texts:
            result = self.predict(text)
            results.append(result)
        return results


# For backwards compatibility and standalone testing
def create_model(model_path):
    return AIDetectionModel(model_path)


# Standalone testing code (only runs when script is executed directly)
if __name__ == "__main__":
    # Test model path - adjust as needed
    model_path = "/content/drive/MyDrive/SecondModelData/checkpoint-4250"
    
    # Create model instance
    detector = AIDetectionModel(model_path)

    test_sentence = """Cook was clear in positioning privacy as a central pillar of Apple's AI value proposition. The private cloud compute architecture, designed to minimize the amount of user data leaving the device, is a counterpoint to competitors that require extensive cloud data processing.

The CEO argued that this hybrid approach — balancing on-device AI with selective, secure server-based computing — offers "the best way for users to experience the full potential of generative AI" without sacrificing security or personal data integrity."""

    result = detector.predict_with_confidence(test_sentence)
    
    print("="*50)
    print("AI Detection Results")
    print("="*50)
    print(f"Prediction: {result['prediction'].upper()}")
    print(f"Confidence Level: {result['confidence_level']}")
    print(f"Confidence Score: {result['confidence_score']:.4f}")
    print()
    print("Detailed Probabilities:")
    print(f"Human Probability: {result['human_probability']:.4f} ({result['human_probability']*100:.2f}%)")
    print(f"AI Probability: {result['ai_probability']:.4f} ({result['ai_probability']*100:.2f}%)")
    
    test_sentences = [
        "I feel like a lot of what people think of as a failing of GPT-5 is really a failing of the router.",
        "The router is just not good at knowing when to switch models, or into a mode that uses tools.",
        "The router is supposed to be saving them money by having the people who always use thinking modes sometimes use the basic modes, and to increase the access to thinking modes by those that always use the basic modes.",
        "Cook was clear in positioning privacy as a central pillar of Apple's AI value proposition. The private cloud compute architecture, designed to minimize the amount of user data leaving the device, is a counterpoint to competitors that require extensive cloud data processing."
    ]
    
    print("\n" + "="*50)
    print("Batch Testing Results")
    print("="*50)
    
    batch_results = detector.batch_predict(test_sentences)
    for i, (sentence, result) in enumerate(zip(test_sentences, batch_results)):
        print(f"\n--- Sentence {i+1} ---")
        print(f"Text: {sentence[:100]}{'...' if len(sentence) > 100 else ''}")
        predicted_class = "AI" if result['ai_probability'] > result['human_probability'] else "Human"
        print(f"Prediction: {predicted_class} (Confidence: {result['confidence']:.3f})")
        print(f"Human: {result['human_probability']:.3f}, AI: {result['ai_probability']:.3f}")