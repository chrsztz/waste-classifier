import os
import time
import cv2
import numpy as np
from datetime import datetime

class Camera:
    """
    Camera module to capture images of waste for classification.
    Uses OpenCV to interface with the camera.
    """
    
    def __init__(self, camera_id=0, image_width=640, image_height=480):
        """
        Initialize camera with specified ID and resolution
        
        Args:
            camera_id: Camera device ID (default 0)
            image_width: Width of captured image
            image_height: Height of captured image
        """
        self.camera_id = camera_id
        self.image_width = image_width
        self.image_height = image_height
        self.camera = None
        self.is_initialized = False
    
    def initialize(self):
        """Initialize camera connection"""
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            
            # Set resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
            
            # Check if camera initialized successfully
            if not self.camera.isOpened():
                print("Error: Could not open camera.")
                return False
            
            # Wait for camera to initialize
            time.sleep(1)
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self):
        """
        Capture a single image from the camera
        
        Returns:
            Image as numpy array or None if capture failed
        """
        if not self.is_initialized and not self.initialize():
            return None
        
        # Capture frame
        ret, frame = self.camera.read()
        
        if not ret or frame is None:
            print("Error: Failed to capture image.")
            return None
        
        return frame
    
    def save_image(self, directory="captured_images"):
        """
        Capture an image and save it to disk
        
        Args:
            directory: Directory to save image
            
        Returns:
            Path to saved image or None if failed
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Capture image
        image = self.capture_image()
        if image is None:
            return None
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/waste_{timestamp}.jpg"
        
        # Save image
        try:
            cv2.imwrite(filename, image)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def capture_for_classification(self, preprocess=True):
        """
        Capture an image specifically for classification
        
        Args:
            preprocess: Whether to preprocess the image for the model
            
        Returns:
            Preprocessed image as numpy array or None if failed
        """
        image = self.capture_image()
        if image is None:
            return None
        
        if preprocess:
            # Common preprocessing for classification models:
            # 1. Resize to model input size (assuming YOLOv11s-cls uses 224x224)
            image = cv2.resize(image, (224, 224))
            
            # 2. Convert BGR to RGB (OpenCV uses BGR, most models use RGB)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 3. Normalize pixel values
            image = image / 255.0
        
        return image
    
    def release(self):
        """Release camera resources"""
        if self.is_initialized and self.camera is not None:
            self.camera.release()
            self.is_initialized = False 