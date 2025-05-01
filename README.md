# Automatic Waste Classification System

## Overview
This project implements an automatic waste classification system using an NVIDIA Orin Nano with YOLOv11s-cls model. The system captures images of waste items, classifies them into four categories (paper, glass, metal, others), and routes them to the appropriate bins using servo motors.

## Hardware Components
- NVIDIA Orin Nano (main processor)
- Camera (for waste image capture)
- IR sensor (to detect waste at entrance)
- 3× SG90 servo motors (pins 15, 32, 33) for waste routing
- 4× Ultrasonic sensors (to measure bin utilization)
- 8-inch display (for user interface)

## System Architecture

### 1. Core Components
- **Waste Detection**: IR sensor detects when waste enters the system
- **Image Capture**: Camera takes a photo of the waste item
- **Classification**: YOLOv11s-cls model classifies the waste
- **Waste Routing**: Servo motors direct waste to appropriate bin
- **Utilization Monitoring**: Ultrasonic sensors track bin fullness
- **User Interface**: Web application for visualization and feedback

### 2. Classification System
The system uses a YOLOv11s-cls model that was trained on 6 waste classes:
- cardboard
- glass
- metal 
- paper
- plastic
- trash

These 6 classes are mapped to 4 bin categories:
- **Paper bin**: cardboard, paper
- **Glass bin**: glass
- **Metal bin**: metal
- **Others bin**: plastic, trash

### 3. Directory Structure
```
waste-classifier/
├── model/
│   └── weights/ # Pre-trained YOLOv11s-cls model
├── src/
│   ├── hardware/ # Hardware control code
│   │   ├── camera.py
│   │   ├── sensors.py
│   │   ├── servos.py
│   │   └── hardware_check.py
│   ├── inference/ # Model inference code
│   │   └── classifier.py
│   ├── server/ # Backend server for the web UI
│   │   ├── app.py
│   │   └── routes/
│   └── utils/ # Utility functions
├── web/ # React + Tailwind frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
├── check_hardware.py # Hardware diagnostic tool
└── main.py # Main application entry point
```

## Installation

### Prerequisites
- NVIDIA Orin Nano with Jetpack installed
- Python 3.8+
- Node.js 16+
- YOLOv11s-cls model weights in `model/weights/` directory

### Setting up the environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/waste-classifier.git
cd waste-classifier
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd web
npm install
npm run build
cd ..
```

4. Configure hardware pins (if needed):
   - Edit `main.py` to adjust pin configurations for your setup

### Hardware Setup
1. Connect the IR sensor to pin 16
2. Connect the servo motors to pins 15, 32, and 33
3. Connect the ultrasonic sensors to the configured pins
4. Set up the camera for image capture

## Usage

### Hardware Diagnostics

Before running the main system, it's recommended to check if all hardware components are working correctly:

```bash
# Check all hardware components
python check_hardware.py

# Check specific components
python check_hardware.py --camera-only
python check_hardware.py --ir-only
python check_hardware.py --ultrasonic-only
python check_hardware.py --servo-only

# Save diagnostic results to a file
python check_hardware.py --save-results
```

### Starting the System

1. Run the main application:
```bash
python main.py
```

2. For development or testing without hardware:
```bash
python main.py --no-hardware
```

3. Access the web interface:
   - Open a browser and go to `http://localhost:5000`
   - or `http://<orin-nano-ip>:5000` from another device

### Classification Workflow

1. System detects waste via IR sensor
2. Camera captures image of waste
3. YOLOv11s-cls model classifies waste into one of 6 classes
4. The 6 classes are mapped to 4 bin categories
5. Classification result displays on web interface
6. User can confirm or correct classification
7. Servo motors route waste to appropriate bin
8. Bin utilization updates on interface

### Admin Panel

The system includes an admin panel for monitoring and statistics:

1. Click the "Admin Panel" button in the top right corner
2. Enter the default password: `admin123`
3. The admin panel provides:
   - Bin utilization statistics
   - Classification accuracy metrics
   - Detailed classification history
   - Images of classified waste items
   - Correction statistics

## Classification Logic
1. Waste detected → Camera captures image
2. Image sent to YOLOv11s-cls model
3. Model classifies into: Cardboard, Glass, Metal, Paper, Plastic, Trash
4. Classes are mapped to bins: Paper, Glass, Metal, Others
5. Servos activated based on bin category

## Web Interface
- Real-time bin utilization display when idle
- Classification result visualization during active use
- User correction interface for feedback
- Historical classification data and statistics
- Admin panel for detailed analytics

## Troubleshooting

### Common Issues
1. **Hardware connection errors**:
   - Run `python check_hardware.py` to diagnose specific hardware issues
   - Check that all sensors and motors are properly connected
   - Verify GPIO pin configurations match your setup

2. **Model loading errors**:
   - Ensure model weights are in the correct location
   - Check for compatible CUDA version if using GPU

3. **Web interface not accessible**:
   - Verify the Flask server is running
   - Check for firewall issues or port conflicts

## License
This project is licensed under the MIT License - see the LICENSE file for details.