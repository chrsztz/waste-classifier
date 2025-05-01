#!/usr/bin/env python3
"""
Main entry point for the Waste Classification System.
"""

import os
import sys
import signal
import argparse
import atexit
from src.hardware.camera import Camera
from src.hardware.sensors import IRSensor, BinSensors
from src.hardware.servos import ServoController
from src.inference.classifier import WasteClassifier
from src.server.app import app, socketio, initialize_hardware, load_classification_history, background_monitor

# Define pin configurations
PIN_CONFIG = {
    'ir_sensor_pin': 16,
    'paper_ultrasonic_pins': (11, 12),
    'glass_ultrasonic_pins': (13, 14),
    'metal_ultrasonic_pins': (18, 19),
    'others_ultrasonic_pins': (20, 21),
}

# Global variables for hardware components
camera = None
ir_sensor = None
bin_sensors = None
servo_controller = None
classifier = None

def cleanup():
    """Clean up resources on exit"""
    print("Cleaning up resources...")
    
    # Clean up servo resources
    if servo_controller:
        servo_controller.cleanup()
    
    # Release camera
    if camera:
        camera.release()
    
    print("Cleanup complete. Exiting...")

def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) to clean up resources"""
    print("\nInterrupt received. Shutting down...")
    cleanup()
    sys.exit(0)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Waste Classification System')
    parser.add_argument('--no-hardware', action='store_true', 
                        help='Run without hardware components (for development/testing)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port for the web server (default: 5000)')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host for the web server (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    return parser.parse_args()

def main():
    """Main function to start the system"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create necessary directories
    os.makedirs('captured_images', exist_ok=True)
    
    # Initialize hardware (if not disabled)
    if not args.no_hardware:
        print("Initializing hardware components...")
        if initialize_hardware():
            print("Hardware initialization successful")
        else:
            print("Hardware initialization failed")
            if not args.debug:
                print("Exiting due to hardware initialization failure. Use --no-hardware to run without hardware.")
                return
    else:
        print("Running without hardware components")
    
    # Load classification history
    load_classification_history()
    
    # Start background monitoring thread if hardware is enabled
    if not args.no_hardware:
        import threading
        print("Starting background monitoring thread...")
        threading.Thread(target=background_monitor, daemon=True).start()
    
    # Start the Flask server
    print(f"Starting web server on {args.host}:{args.port}")
    socketio.run(app, host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 