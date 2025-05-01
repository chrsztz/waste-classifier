# Waste Classifier Static UI Mockups

This folder contains static HTML mockups of the waste classifier web interface. These mockups are designed to demonstrate the UI/UX without requiring the full application to be running.

## Files

- `index.html`: Main user interface with real-time bin status, current classification, and history
- `admin.html`: Admin panel with statistics, bin utilization, and detailed classification history
- `template.html`: Base template with common CSS and JavaScript

## Features Represented

### Main Interface (`index.html`)
- Bin status indicators showing fill levels for each category
- Current classification display with image and confidence level
- User correction interface for misclassifications
- Recent classification history table
- System status indicators
- Link to admin panel

### Admin Panel (`admin.html`)
- Comprehensive statistics dashboard
- Interactive charts for classification distribution
- Bin fill level visualization
- Detailed classification history with timestamps
- Detailed view modal for each classification with confidence scores
- Toggle between statistics view and detailed history

## How to Use

Simply open the HTML files in a web browser to view the static interfaces. No server or backend is required.

```
# Example with Python's built-in HTTP server
cd static-pages
python -m http.server 8000
```

Then visit `http://localhost:8000` in your browser.

## Design Notes

- The interface uses Tailwind CSS for styling
- Font Awesome is used for icons
- Chart.js is used for data visualization in the admin panel
- The design is responsive and mobile-friendly
- Color coding is used consistently across the UI:
  - Paper/Cardboard: Yellow (#fcd34d)
  - Glass: Blue (#60a5fa)
  - Metal: Gray (#9ca3af)
  - Others/Plastic/Trash: Green (#a3e635) 