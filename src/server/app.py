import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Import modules from our project
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hardware.camera import Camera
from hardware.sensors import IRSensor, BinSensors
from hardware.servos import ServoController
from inference.classifier import WasteClassifier

# Initialize Flask app
app = Flask(__name__, static_folder='../../web/build')
CORS(app)  # Enable Cross-Origin Resource Sharing
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
camera = None
ir_sensor = None
bin_sensors = None
servo_controller = None
classifier = None

# Configuration
CONFIG = {
    'ir_sensor_pin': 16,
    'paper_ultrasonic_pins': (11, 12),
    'glass_ultrasonic_pins': (13, 14),
    'metal_ultrasonic_pins': (18, 19),
    'others_ultrasonic_pins': (20, 21),
    'model_path': 'model/weights/yolov11s-cls.pt',
    'image_save_dir': 'captured_images',
    'classification_history_file': 'classification_history.json'
}

# Classification history
classification_history = []

# Initialize hardware components
def initialize_hardware():
    global camera, ir_sensor, bin_sensors, servo_controller, classifier
    
    try:
        # Initialize camera
        camera = Camera()
        if not camera.initialize():
            print("Failed to initialize camera")
        
        # Initialize IR sensor
        ir_sensor = IRSensor(CONFIG['ir_sensor_pin'])
        
        # Initialize ultrasonic sensors for bin levels
        bin_sensors = BinSensors(
            CONFIG['paper_ultrasonic_pins'],
            CONFIG['glass_ultrasonic_pins'],
            CONFIG['metal_ultrasonic_pins'],
            CONFIG['others_ultrasonic_pins']
        )
        
        # Initialize servo controller
        servo_controller = ServoController()
        
        # Initialize classifier
        classifier = WasteClassifier(CONFIG['model_path'])
        classifier.load_model()
        
        return True
    
    except Exception as e:
        print(f"Error initializing hardware: {e}")
        return False

# Load classification history from file
def load_classification_history():
    global classification_history
    
    history_file = CONFIG['classification_history_file']
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                classification_history = json.load(f)
        except Exception as e:
            print(f"Error loading classification history: {e}")
            classification_history = []
    else:
        classification_history = []

# Save classification history to file
def save_classification_history():
    try:
        with open(CONFIG['classification_history_file'], 'w') as f:
            json.dump(classification_history, f)
    except Exception as e:
        print(f"Error saving classification history: {e}")

# Broadcast bin levels to clients
def broadcast_bin_levels():
    if bin_sensors:
        levels = bin_sensors.get_all_fill_percentages()
        socketio.emit('bin_levels', levels)

# Classification process
def process_waste():
    if not all([camera, classifier, servo_controller]):
        return {'error': 'System not fully initialized'}
    
    try:
        # Capture image
        image = camera.capture_for_classification(preprocess=False)
        if image is None:
            return {'error': 'Failed to capture image'}
        
        # Save image to disk
        image_path = camera.save_image(CONFIG['image_save_dir'])
        
        # Classify waste
        result = classifier.classify_array(image)
        if 'error' in result:
            return result
        
        # Add timestamp and image path to result
        result['timestamp'] = datetime.now().isoformat()
        result['image_path'] = image_path
        
        # Emit result to connected clients
        socketio.emit('classification_result', result)
        
        # Wait for user feedback before routing (timeout after 10 seconds)
        # This allows users to correct the classification if needed
        for _ in range(10):
            time.sleep(1)
            # Check if user provided feedback (this would update the result)
            # For now, we'll just proceed with the original classification
        
        # Route waste based on classification
        servo_controller.route_by_category(result['class'])
        
        # Add to classification history
        classification_history.append(result)
        save_classification_history()
        
        # Update bin levels
        broadcast_bin_levels()
        
        return result
    
    except Exception as e:
        return {'error': str(e)}

# Background task to monitor IR sensor and process waste
def background_monitor():
    while True:
        if ir_sensor and ir_sensor.is_object_detected():
            print("Object detected! Processing...")
            process_waste()
            # Wait a bit to avoid repeated detections
            time.sleep(3)
        time.sleep(0.1)  # Small delay to reduce CPU usage

# Serve static React app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Serve captured images
@app.route('/captured_images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.abspath(CONFIG['image_save_dir']), filename)

# Serve diagnostic images
@app.route('/diagnostic_images/<path:filename>')
def serve_diagnostic_image(filename):
    return send_from_directory(os.path.abspath('diagnostic_images'), filename)

# API endpoints
@app.route('/api/bin_levels', methods=['GET'])
def get_bin_levels():
    if bin_sensors:
        return jsonify(bin_sensors.get_all_fill_percentages())
    return jsonify({'error': 'Bin sensors not initialized'})

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(classification_history)

@app.route('/api/classify', methods=['POST'])
def classify_manual():
    """Manually trigger classification (for testing without IR sensor)"""
    return jsonify(process_waste())

@app.route('/api/correct', methods=['POST'])
def correct_classification():
    """Allow user to correct a classification"""
    try:
        data = request.json
        if not data or 'class' not in data or 'timestamp' not in data:
            return jsonify({'error': 'Invalid correction data'})
        
        # Find the classification in history by timestamp
        for item in classification_history:
            if item['timestamp'] == data['timestamp']:
                # Update the class
                old_class = item['class']
                item['class'] = data['class']
                item['corrected'] = True
                item['original_class'] = old_class
                save_classification_history()
                
                # Route waste to correct bin
                if servo_controller:
                    servo_controller.route_by_category(data['class'])
                
                return jsonify({'success': True})
        
        return jsonify({'error': 'Classification not found'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current bin levels to newly connected client
    if bin_sensors:
        emit('bin_levels', bin_sensors.get_all_fill_percentages())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_manual_classification')
def handle_manual_classification():
    """Allow client to request classification via WebSocket"""
    result = process_waste()
    emit('classification_result', result)

@socketio.on('correct_classification')
def handle_correct_classification(data):
    """Allow user to correct classification via WebSocket"""
    try:
        if not data or 'class' not in data or 'timestamp' not in data:
            emit('correction_result', {'error': 'Invalid correction data'})
            return
        
        # Find the classification in history by timestamp
        for item in classification_history:
            if item['timestamp'] == data['timestamp']:
                # Update the class
                old_class = item['class']
                item['class'] = data['class']
                item['corrected'] = True
                item['original_class'] = old_class
                save_classification_history()
                
                # Route waste to correct bin
                if servo_controller:
                    servo_controller.route_by_category(data['class'])
                
                emit('correction_result', {'success': True})
                return
        
        emit('correction_result', {'error': 'Classification not found'})
    
    except Exception as e:
        emit('correction_result', {'error': str(e)})

if __name__ == '__main__':
    # Initialize hardware
    initialize_hardware()
    
    # Load classification history
    load_classification_history()
    
    # Start the background monitoring in a separate thread
    import threading
    threading.Thread(target=background_monitor, daemon=True).start()
    
    # Start the server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 