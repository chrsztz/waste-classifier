import time
import RPi.GPIO as GPIO

class IRSensor:
    """
    IR sensor to detect waste at the entrance of the system.
    When an object breaks the IR beam, the sensor triggers.
    """
    
    def __init__(self, pin):
        """Initialize IR sensor with GPIO pin"""
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN)
    
    def is_object_detected(self):
        """
        Check if an object is detected by the IR sensor
        Returns True if object is detected, False otherwise
        """
        # IR sensor typically outputs LOW when object is detected
        return not GPIO.input(self.pin)
    
    def wait_for_object(self, timeout=None):
        """
        Wait for an object to be detected
        timeout: maximum time to wait in seconds (None for indefinite)
        Returns True if object detected, False if timeout occurred
        """
        start_time = time.time()
        while timeout is None or (time.time() - start_time) < timeout:
            if self.is_object_detected():
                return True
            time.sleep(0.01)  # Small delay to reduce CPU usage
        return False


class UltrasonicSensor:
    """
    Ultrasonic sensor to measure the fill level of bins.
    Uses echo time to calculate distance.
    """
    
    def __init__(self, trigger_pin, echo_pin):
        """Initialize ultrasonic sensor with trigger and echo pins"""
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)
        
        # Ensure trigger is low
        GPIO.output(trigger_pin, False)
        time.sleep(0.1)
    
    def measure_distance(self):
        """
        Measure distance using ultrasonic sensor
        Returns distance in centimeters
        """
        # Send 10us pulse to trigger
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(self.trigger_pin, False)
        
        # Get time when pulse was sent and received
        pulse_start = time.time()
        pulse_timeout = pulse_start + 0.05  # 50ms timeout
        
        # Wait for echo to go high (pulse sent)
        while not GPIO.input(self.echo_pin):
            pulse_start = time.time()
            if pulse_start > pulse_timeout:
                return -1  # Timeout occurred
        
        # Wait for echo to go low (pulse received)
        pulse_end = time.time()
        pulse_timeout = pulse_end + 0.05  # 50ms timeout
        
        while GPIO.input(self.echo_pin):
            pulse_end = time.time()
            if pulse_end > pulse_timeout:
                return -1  # Timeout occurred
        
        # Calculate distance based on time difference
        pulse_duration = pulse_end - pulse_start
        distance_cm = pulse_duration * 17150  # Speed of sound in cm/s divided by 2
        
        return round(distance_cm, 2)
    
    def get_multiple_readings(self, count=3, delay=0.1):
        """
        Take multiple distance readings and return average
        Helps reduce measurement errors
        """
        total = 0
        valid_readings = 0
        
        for _ in range(count):
            distance = self.measure_distance()
            if distance > 0:  # Only count valid readings
                total += distance
                valid_readings += 1
            time.sleep(delay)
        
        if valid_readings > 0:
            return total / valid_readings
        else:
            return -1  # No valid readings


class BinSensors:
    """
    Manager for all four ultrasonic sensors used to measure bin fill levels.
    """
    
    # Maximum depth of each bin in cm
    MAX_BIN_DEPTH = 30
    
    def __init__(self, paper_pins, glass_pins, metal_pins, others_pins):
        """
        Initialize all bin sensors with their trigger and echo pins
        Each pins parameter should be a tuple of (trigger_pin, echo_pin)
        """
        self.paper_sensor = UltrasonicSensor(*paper_pins)
        self.glass_sensor = UltrasonicSensor(*glass_pins)
        self.metal_sensor = UltrasonicSensor(*metal_pins)
        self.others_sensor = UltrasonicSensor(*others_pins)
    
    def get_paper_fill_percentage(self):
        """Get paper bin fill percentage (0-100)"""
        distance = self.paper_sensor.get_multiple_readings()
        if distance <= 0:
            return -1  # Error in reading
        
        # Convert distance to fill percentage
        # Empty bin = MAX_BIN_DEPTH (0% full)
        # Full bin = 0cm distance (100% full)
        fill_percentage = ((self.MAX_BIN_DEPTH - distance) / self.MAX_BIN_DEPTH) * 100
        return max(0, min(100, fill_percentage))  # Clamp between 0-100
    
    def get_glass_fill_percentage(self):
        """Get glass bin fill percentage (0-100)"""
        distance = self.glass_sensor.get_multiple_readings()
        if distance <= 0:
            return -1  # Error in reading
        
        fill_percentage = ((self.MAX_BIN_DEPTH - distance) / self.MAX_BIN_DEPTH) * 100
        return max(0, min(100, fill_percentage))
    
    def get_metal_fill_percentage(self):
        """Get metal bin fill percentage (0-100)"""
        distance = self.metal_sensor.get_multiple_readings()
        if distance <= 0:
            return -1  # Error in reading
        
        fill_percentage = ((self.MAX_BIN_DEPTH - distance) / self.MAX_BIN_DEPTH) * 100
        return max(0, min(100, fill_percentage))
    
    def get_others_fill_percentage(self):
        """Get others bin fill percentage (0-100)"""
        distance = self.others_sensor.get_multiple_readings()
        if distance <= 0:
            return -1  # Error in reading
        
        fill_percentage = ((self.MAX_BIN_DEPTH - distance) / self.MAX_BIN_DEPTH) * 100
        return max(0, min(100, fill_percentage))
    
    def get_all_fill_percentages(self):
        """Get fill percentages for all bins"""
        return {
            'paper': self.get_paper_fill_percentage(),
            'glass': self.get_glass_fill_percentage(),
            'metal': self.get_metal_fill_percentage(),
            'others': self.get_others_fill_percentage()
        } 