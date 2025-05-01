import time
import RPi.GPIO as GPIO

class ServoController:
    """
    Controller for the three servo motors that route waste to appropriate bins.
    - Upper servo (pin 15): Initial direction
    - Lower servos (pins 32, 33): Final bin placement
    
    Each servo has 90° as equilibrium, and can turn to 0° and 180° for different pathways.
    """
    
    # Servo pin definitions
    UPPER_SERVO_PIN = 15
    LOWER_SERVO_1_PIN = 32
    LOWER_SERVO_2_PIN = 33
    
    # Servo angle definitions
    EQUILIBRIUM = 90
    LEFT_ANGLE = 0
    RIGHT_ANGLE = 180
    
    # PWM frequency (Hz)
    PWM_FREQ = 50
    
    def __init__(self):
        # Initialize GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.UPPER_SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.LOWER_SERVO_1_PIN, GPIO.OUT)
        GPIO.setup(self.LOWER_SERVO_2_PIN, GPIO.OUT)
        
        # Initialize PWM for each servo
        self.upper_servo = GPIO.PWM(self.UPPER_SERVO_PIN, self.PWM_FREQ)
        self.lower_servo_1 = GPIO.PWM(self.LOWER_SERVO_1_PIN, self.PWM_FREQ)
        self.lower_servo_2 = GPIO.PWM(self.LOWER_SERVO_2_PIN, self.PWM_FREQ)
        
        # Start PWM with equilibrium position
        self.upper_servo.start(self._angle_to_duty_cycle(self.EQUILIBRIUM))
        self.lower_servo_1.start(self._angle_to_duty_cycle(self.EQUILIBRIUM))
        self.lower_servo_2.start(self._angle_to_duty_cycle(self.EQUILIBRIUM))
        
        # Wait for servos to reach position
        time.sleep(0.5)
    
    def _angle_to_duty_cycle(self, angle):
        """Convert angle (0-180) to duty cycle (2.5-12.5)"""
        return 2.5 + (angle / 180) * 10
    
    def set_upper_servo(self, angle):
        """Set upper servo to specified angle"""
        self.upper_servo.ChangeDutyCycle(self._angle_to_duty_cycle(angle))
        time.sleep(0.3)  # Allow time for servo to reach position
    
    def set_lower_servo_1(self, angle):
        """Set lower servo 1 to specified angle"""
        self.lower_servo_1.ChangeDutyCycle(self._angle_to_duty_cycle(angle))
        time.sleep(0.3)  # Allow time for servo to reach position
        
    def set_lower_servo_2(self, angle):
        """Set lower servo 2 to specified angle"""
        self.lower_servo_2.ChangeDutyCycle(self._angle_to_duty_cycle(angle))
        time.sleep(0.3)  # Allow time for servo to reach position
    
    def route_to_paper(self):
        """Route waste to paper bin"""
        self.set_upper_servo(self.LEFT_ANGLE)
        self.set_lower_servo_1(self.LEFT_ANGLE)
        time.sleep(1)  # Wait for waste to pass through
        self.reset_positions()
    
    def route_to_glass(self):
        """Route waste to glass bin"""
        self.set_upper_servo(self.LEFT_ANGLE)
        self.set_lower_servo_1(self.RIGHT_ANGLE)
        time.sleep(1)  # Wait for waste to pass through
        self.reset_positions()
    
    def route_to_metal(self):
        """Route waste to metal bin"""
        self.set_upper_servo(self.RIGHT_ANGLE)
        self.set_lower_servo_2(self.LEFT_ANGLE)
        time.sleep(1)  # Wait for waste to pass through
        self.reset_positions()
    
    def route_to_others(self):
        """Route waste to others bin (trash, plastic)"""
        self.set_upper_servo(self.RIGHT_ANGLE)
        self.set_lower_servo_2(self.RIGHT_ANGLE)
        time.sleep(1)  # Wait for waste to pass through
        self.reset_positions()
    
    def reset_positions(self):
        """Reset all servos to equilibrium position"""
        self.set_upper_servo(self.EQUILIBRIUM)
        self.set_lower_servo_1(self.EQUILIBRIUM)
        self.set_lower_servo_2(self.EQUILIBRIUM)
    
    def route_by_category(self, category):
        """Route waste based on classification category"""
        category = category.lower()
        if category in ['paper', 'cardboard']:
            self.route_to_paper()
        elif category == 'glass':
            self.route_to_glass()
        elif category == 'metal':
            self.route_to_metal()
        else:  # 'others', 'trash', 'plastic'
            self.route_to_others()
    
    def cleanup(self):
        """Clean up GPIO pins"""
        self.upper_servo.stop()
        self.lower_servo_1.stop()
        self.lower_servo_2.stop()
        GPIO.cleanup([self.UPPER_SERVO_PIN, self.LOWER_SERVO_1_PIN, self.LOWER_SERVO_2_PIN]) 