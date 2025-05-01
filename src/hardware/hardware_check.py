#!/usr/bin/env python3
"""
Diagnostic script to check if all hardware components are working correctly.
Tests the camera, IR sensor, ultrasonic sensors, and servo motors.
"""

import os
import time
import sys
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hardware.camera import Camera
from hardware.sensors import IRSensor, UltrasonicSensor, BinSensors
from hardware.servos import ServoController

# Configuration
PIN_CONFIG = {
    'ir_sensor_pin': 16,
    'paper_ultrasonic_pins': (11, 12),
    'glass_ultrasonic_pins': (13, 14),
    'metal_ultrasonic_pins': (18, 19),
    'others_ultrasonic_pins': (20, 21),
    'upper_servo_pin': 15,
    'lower_servo_1_pin': 32,
    'lower_servo_2_pin': 33
}

class HardwareChecker:
    """
    Class to check the status of all hardware components
    """
    
    def __init__(self):
        self.camera = None
        self.ir_sensor = None
        self.bin_sensors = None
        self.servo_controller = None
        self.results = {
            'camera': False,
            'ir_sensor': False,
            'ultrasonic_sensors': {
                'paper': False,
                'glass': False,
                'metal': False,
                'others': False
            },
            'servos': {
                'upper': False,
                'lower_1': False,
                'lower_2': False
            }
        }
    
    def check_camera(self, save_test_image=True):
        """Check if camera is working"""
        print("\n==== Checking Camera ====")
        try:
            self.camera = Camera()
            if not self.camera.initialize():
                print("❌ Camera initialization failed")
                return False
            
            print("✓ Camera initialized successfully")
            
            # Capture test image
            image = self.camera.capture_image()
            if image is None:
                print("❌ Failed to capture test image")
                return False
            
            print(f"✓ Test image captured: {image.shape}")
            
            # Save test image if requested
            if save_test_image:
                filename = self.camera.save_image(directory="diagnostic_images")
                if filename:
                    print(f"✓ Test image saved to: {filename}")
                else:
                    print("⚠️ Could not save test image, but capture was successful")
            
            self.results['camera'] = True
            return True
            
        except Exception as e:
            print(f"❌ Camera check failed with error: {e}")
            return False
        finally:
            if self.camera:
                self.camera.release()
    
    def check_ir_sensor(self):
        """Check if IR sensor is working"""
        print("\n==== Checking IR Sensor ====")
        try:
            self.ir_sensor = IRSensor(PIN_CONFIG['ir_sensor_pin'])
            
            # Check current state
            state = self.ir_sensor.is_object_detected()
            print(f"IR sensor current state: {'Object detected' if state else 'No object detected'}")
            
            print("Please place an object in front of the IR sensor within 5 seconds...")
            detected = self.ir_sensor.wait_for_object(timeout=5)
            
            if detected:
                print("✓ IR sensor detected an object")
                self.results['ir_sensor'] = True
                return True
            else:
                print("❌ IR sensor did not detect any object within timeout")
                return False
                
        except Exception as e:
            print(f"❌ IR sensor check failed with error: {e}")
            return False
    
    def check_ultrasonic_sensors(self):
        """Check if ultrasonic sensors are working"""
        print("\n==== Checking Ultrasonic Sensors ====")
        
        # Setup individual sensors for testing
        sensors = {
            'paper': UltrasonicSensor(*PIN_CONFIG['paper_ultrasonic_pins']),
            'glass': UltrasonicSensor(*PIN_CONFIG['glass_ultrasonic_pins']),
            'metal': UltrasonicSensor(*PIN_CONFIG['metal_ultrasonic_pins']),
            'others': UltrasonicSensor(*PIN_CONFIG['others_ultrasonic_pins'])
        }
        
        # Also test the combined BinSensors manager
        try:
            self.bin_sensors = BinSensors(
                PIN_CONFIG['paper_ultrasonic_pins'],
                PIN_CONFIG['glass_ultrasonic_pins'],
                PIN_CONFIG['metal_ultrasonic_pins'],
                PIN_CONFIG['others_ultrasonic_pins']
            )
            print("✓ BinSensors manager initialized")
        except Exception as e:
            print(f"❌ BinSensors manager initialization failed: {e}")
        
        all_working = True
        
        # Test each sensor
        for bin_type, sensor in sensors.items():
            try:
                print(f"\nTesting {bin_type} bin sensor...")
                distance = sensor.get_multiple_readings(count=3, delay=0.2)
                
                if distance > 0:
                    print(f"✓ {bin_type.capitalize()} sensor reading: {distance:.1f} cm")
                    self.results['ultrasonic_sensors'][bin_type] = True
                else:
                    print(f"❌ {bin_type.capitalize()} sensor failed to get valid reading")
                    all_working = False
                
            except Exception as e:
                print(f"❌ {bin_type.capitalize()} sensor check failed with error: {e}")
                all_working = False
        
        # Test bin levels if BinSensors initialized correctly
        if self.bin_sensors:
            try:
                print("\nGetting bin fill percentages...")
                levels = self.bin_sensors.get_all_fill_percentages()
                
                for bin_type, level in levels.items():
                    if level >= 0:
                        print(f"✓ {bin_type.capitalize()} bin level: {level:.1f}%")
                    else:
                        print(f"⚠️ {bin_type.capitalize()} bin level reading failed")
            except Exception as e:
                print(f"❌ Bin levels check failed with error: {e}")
        
        return all_working
    
    def check_servos(self):
        """Check if servo motors are working"""
        print("\n==== Checking Servo Motors ====")
        try:
            self.servo_controller = ServoController()
            print("✓ Servo controller initialized")
            
            # Test upper servo
            print("\nTesting upper servo...")
            print("Moving to left position (0°)...")
            self.servo_controller.set_upper_servo(self.servo_controller.LEFT_ANGLE)
            time.sleep(1)
            
            print("Moving to right position (180°)...")
            self.servo_controller.set_upper_servo(self.servo_controller.RIGHT_ANGLE)
            time.sleep(1)
            
            print("Moving back to equilibrium (90°)...")
            self.servo_controller.set_upper_servo(self.servo_controller.EQUILIBRIUM)
            time.sleep(1)
            
            self.results['servos']['upper'] = True
            print("✓ Upper servo test completed")
            
            # Test lower servo 1
            print("\nTesting lower servo 1...")
            print("Moving to left position (0°)...")
            self.servo_controller.set_lower_servo_1(self.servo_controller.LEFT_ANGLE)
            time.sleep(1)
            
            print("Moving to right position (180°)...")
            self.servo_controller.set_lower_servo_1(self.servo_controller.RIGHT_ANGLE)
            time.sleep(1)
            
            print("Moving back to equilibrium (90°)...")
            self.servo_controller.set_lower_servo_1(self.servo_controller.EQUILIBRIUM)
            time.sleep(1)
            
            self.results['servos']['lower_1'] = True
            print("✓ Lower servo 1 test completed")
            
            # Test lower servo 2
            print("\nTesting lower servo 2...")
            print("Moving to left position (0°)...")
            self.servo_controller.set_lower_servo_2(self.servo_controller.LEFT_ANGLE)
            time.sleep(1)
            
            print("Moving to right position (180°)...")
            self.servo_controller.set_lower_servo_2(self.servo_controller.RIGHT_ANGLE)
            time.sleep(1)
            
            print("Moving back to equilibrium (90°)...")
            self.servo_controller.set_lower_servo_2(self.servo_controller.EQUILIBRIUM)
            time.sleep(1)
            
            self.results['servos']['lower_2'] = True
            print("✓ Lower servo 2 test completed")
            
            # Test routing functions
            print("\nTesting routing functions...")
            
            print("Testing route to paper bin...")
            self.servo_controller.route_to_paper()
            time.sleep(1)
            
            print("Testing route to glass bin...")
            self.servo_controller.route_to_glass()
            time.sleep(1)
            
            print("Testing route to metal bin...")
            self.servo_controller.route_to_metal()
            time.sleep(1)
            
            print("Testing route to others bin...")
            self.servo_controller.route_to_others()
            time.sleep(1)
            
            print("✓ Routing functions test completed")
            
            return True
            
        except Exception as e:
            print(f"❌ Servo check failed with error: {e}")
            return False
        finally:
            if self.servo_controller:
                self.servo_controller.cleanup()
    
    def run_all_checks(self):
        """Run all hardware checks"""
        print("Starting hardware diagnostics...\n")
        
        camera_ok = self.check_camera()
        ir_sensor_ok = self.check_ir_sensor()
        ultrasonic_ok = self.check_ultrasonic_sensors()
        servos_ok = self.check_servos()
        
        # Print summary
        print("\n==== Diagnostic Summary ====")
        print(f"Camera: {'✓ Working' if camera_ok else '❌ Not working'}")
        print(f"IR Sensor: {'✓ Working' if ir_sensor_ok else '❌ Not working'}")
        
        print("\nUltrasonic Sensors:")
        for bin_type, status in self.results['ultrasonic_sensors'].items():
            print(f"  {bin_type.capitalize()}: {'✓ Working' if status else '❌ Not working'}")
        
        print("\nServo Motors:")
        for servo_name, status in self.results['servos'].items():
            print(f"  {servo_name.replace('_', ' ').capitalize()}: {'✓ Working' if status else '❌ Not working'}")
        
        # Overall status
        all_working = camera_ok and ir_sensor_ok and ultrasonic_ok and servos_ok
        print(f"\nOverall status: {'✓ All components working' if all_working else '❌ Some components not working'}")
        
        return all_working

def main():
    parser = argparse.ArgumentParser(description='Check waste classifier hardware components')
    parser.add_argument('--camera-only', action='store_true', help='Check only the camera')
    parser.add_argument('--ir-only', action='store_true', help='Check only the IR sensor')
    parser.add_argument('--ultrasonic-only', action='store_true', help='Check only the ultrasonic sensors')
    parser.add_argument('--servo-only', action='store_true', help='Check only the servo motors')
    args = parser.parse_args()
    
    checker = HardwareChecker()
    
    # Create diagnostic images directory
    os.makedirs("diagnostic_images", exist_ok=True)
    
    # If specific component check is requested
    if args.camera_only:
        checker.check_camera()
    elif args.ir_only:
        checker.check_ir_sensor()
    elif args.ultrasonic_only:
        checker.check_ultrasonic_sensors()
    elif args.servo_only:
        checker.check_servos()
    else:
        # Run all checks
        checker.run_all_checks()

if __name__ == "__main__":
    main() 