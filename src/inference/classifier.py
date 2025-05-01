import os
import torch
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from ultralytics import YOLO

class WasteClassifier:
    """
    Waste classifier using YOLOv11s-cls model to classify waste into
    paper, glass, metal, or others categories.
    """
    
    # Original model classes
    MODEL_CLASSES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
    
    # Output bin categories
    BIN_CLASSES = ['paper', 'glass', 'metal', 'others']
    
    # Mapping from model classes to bin categories
    CLASS_MAPPING = {
        'cardboard': 'paper',
        'glass': 'glass',
        'metal': 'metal',
        'paper': 'paper',
        'plastic': 'others',
        'trash': 'others'
    }
    
    def __init__(self, model_path="model/weights/yolov11s-cls.pt"):
        """
        Initialize waste classifier with YOLOv11s-cls model
        
        Args:
            model_path: Path to the YOLOv11s-cls model weights
        """
        self.model_path = model_path
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Standard preprocessing transforms for YOLO models
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self):
        """Load the YOLOv11s-cls model"""
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at {self.model_path}")
            
            # Load model with Ultralytics YOLO
            self.model = YOLO(self.model_path)
            print(f"Model loaded successfully from {self.model_path}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def preprocess_image(self, image):
        """
        Preprocess image for model inference
        
        Args:
            image: Input image (numpy array from OpenCV or path to image file)
            
        Returns:
            Preprocessed tensor ready for model inference
        """
        try:
            # If image is a file path, load it
            if isinstance(image, str):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"Image file not found at {image}")
                image = Image.open(image).convert('RGB')
            
            # If image is a numpy array (from OpenCV), convert to PIL Image
            elif isinstance(image, np.ndarray):
                # If image is already preprocessed (values in [0, 1])
                if image.max() <= 1.0:
                    image = (image * 255).astype(np.uint8)
                image = Image.fromarray(image.astype(np.uint8))
            
            # Apply preprocessing transforms
            tensor = self.transform(image)
            
            # Add batch dimension
            tensor = tensor.unsqueeze(0)
            
            return tensor.to(self.device)
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def classify(self, image):
        """
        Classify waste image into one of the four categories
        
        Args:
            image: Input image (numpy array from OpenCV or path to image file)
            
        Returns:
            Dictionary with classification results:
            {
                'class': Predicted bin category,
                'original_class': Original model prediction,
                'confidence': Confidence score,
                'all_scores': Dictionary of all class scores (mapped to bin categories)
            }
        """
        # Ensure model is loaded
        if self.model is None and not self.load_model():
            return {'error': 'Model could not be loaded'}
        
        try:
            # Using ultralytics YOLO for prediction
            results = self.model.predict(image, verbose=False)
            
            # Get the classification results
            probabilities = results[0].probs.data.cpu().numpy()
            
            # Get predicted class index and confidence
            class_idx = np.argmax(probabilities)
            confidence = probabilities[class_idx]
            
            # Map model class to original class name
            if class_idx < len(self.MODEL_CLASSES):
                original_class = self.MODEL_CLASSES[class_idx]
            else:
                original_class = f"unknown_class_{class_idx}"
            
            # Map original class to bin category
            if original_class in self.CLASS_MAPPING:
                bin_class = self.CLASS_MAPPING[original_class]
            else:
                bin_class = 'others'  # Default to others for unknown classes
            
            # Create dictionary of all class scores (combined by bin category)
            original_scores = {}
            for i, score in enumerate(probabilities):
                if i < len(self.MODEL_CLASSES):
                    original_scores[self.MODEL_CLASSES[i]] = float(score)
                else:
                    original_scores[f"unknown_class_{i}"] = float(score)
            
            # Combine scores for bin categories
            bin_scores = {}
            for bin_class in self.BIN_CLASSES:
                bin_scores[bin_class] = 0.0
            
            # Sum up scores for each bin category
            for original_class, score in original_scores.items():
                if original_class in self.CLASS_MAPPING:
                    bin_category = self.CLASS_MAPPING[original_class]
                    bin_scores[bin_category] += score
            
            return {
                'class': bin_class,
                'original_class': original_class,
                'confidence': float(confidence),
                'all_scores': bin_scores,
                'original_scores': original_scores
            }
            
        except Exception as e:
            print(f"Error during classification: {e}")
            return {'error': str(e)}
    
    def classify_file(self, image_path):
        """Classify waste from an image file"""
        return self.classify(image_path)
    
    def classify_array(self, image_array):
        """Classify waste from a numpy array (from OpenCV)"""
        return self.classify(image_array) 