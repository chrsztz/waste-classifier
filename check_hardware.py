#!/usr/bin/env python3
"""
Command-line script to check if all hardware components are working correctly.
This is a simple wrapper around the src/hardware/hardware_check.py module.
"""

import sys
import os
import argparse
from src.hardware.hardware_check import HardwareChecker

def main():
    """Main function to run hardware checks"""
    parser = argparse.ArgumentParser(description='Check waste classifier hardware components')
    parser.add_argument('--camera-only', action='store_true', help='Check only the camera')
    parser.add_argument('--ir-only', action='store_true', help='Check only the IR sensor')
    parser.add_argument('--ultrasonic-only', action='store_true', help='Check only the ultrasonic sensors')
    parser.add_argument('--servo-only', action='store_true', help='Check only the servo motors')
    parser.add_argument('--save-results', action='store_true', help='Save diagnostic results to a file')
    args = parser.parse_args()
    
    print("Waste Classifier Hardware Diagnostic Tool")
    print("========================================\n")
    
    # Create diagnostic images directory
    os.makedirs("diagnostic_images", exist_ok=True)
    
    # Initialize hardware checker
    checker = HardwareChecker()
    results = False
    
    # Run specific component check if requested
    if args.camera_only:
        print("Running camera check only...")
        results = checker.check_camera()
    elif args.ir_only:
        print("Running IR sensor check only...")
        results = checker.check_ir_sensor()
    elif args.ultrasonic_only:
        print("Running ultrasonic sensors check only...")
        results = checker.check_ultrasonic_sensors()
    elif args.servo_only:
        print("Running servo motors check only...")
        results = checker.check_servos()
    else:
        # Run all checks
        print("Running complete hardware diagnostic...\n")
        results = checker.run_all_checks()
    
    # Save results if requested
    if args.save_results:
        try:
            import json
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hardware_check_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(checker.results, f, indent=2)
            
            print(f"\nDiagnostic results saved to {filename}")
        except Exception as e:
            print(f"Error saving diagnostic results: {e}")
    
    # Return system exit code based on results
    return 0 if results else 1

if __name__ == "__main__":
    sys.exit(main()) 