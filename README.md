# Sorting Algorithm Visualizer - Setup Instructions

## Requirements

- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation Steps

### 1. Create Project Directory Structure

```bash
mkdir sorting-visualizer
cd sorting-visualizer
```

### 2. Create the following directory structure:

```
sorting-visualizer/
│
├── app.py              # Python backend (provided)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # HTML frontend (provided)
└── static/
    ├── styles.css     # CSS styles (provided)
    └── script.js      # JavaScript frontend (provided)
```

### 3. Create requirements.txt file:

```txt
Flask==2.3.3
Flask-SocketIO==5.3.4
python-socketio==5.9.0
eventlet==0.33.3
```

### 4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 5. Place the provided files in their respective directories:

- Save the Python backend code as `app.py`
- Save the HTML code in `templates/index.html`
- Save the CSS code in `static/styles.css`
- Save the JavaScript code in `static/script.js`

### 6. Run the application:

```bash
python app.py
```

### 7. Open your browser and navigate to:

```
http://localhost:5000
```

## Features Overview

### Sorting Algorithms Implemented:
1. **Bubble Sort** - Simple comparison-based algorithm
2. **Selection Sort** - Finds minimum and places at beginning
3. **Insertion Sort** - Builds sorted array one element at a time
4. **Merge Sort** - Divide-and-conquer algorithm
5. **Quick Sort** - Efficient divide-and-conquer algorithm
6. **Heap Sort** - Comparison-based sorting using heap data structure

### User Controls:
- **Algorithm Selection** - Dropdown to choose sorting algorithm
- **Array Size** - Slider to adjust number of elements (10-100)
- **Speed Control** - Slider to adjust animation speed (10-500ms)
- **Start/Pause/Resume** - Control sorting execution
- **Shuffle** - Generate new random array
- **Reverse** - Arrange array in descending order
- **Reset** - Return to initial state

### Visual Features:
- **Color Coding**:
  - Gray: Unsorted elements
  - Orange: Elements being compared
  - Red: Elements being swapped
  - Green: Sorted elements
  - Purple: Pivot element (Quick Sort)
  - Blue: Active range (Merge Sort)

- **Animations**:
  - Smooth transitions for all operations
  - Progress-based background gradient
  - Completion animation
  - Hover tooltips showing values

- **Real-time Statistics**:
  - Current algorithm display
  - Status updates
  - Comparison counter
  - Swap counter

## Troubleshooting

### Common Issues:

1. **Port already in use**:
   - Change the port in `app.py`: `socketio.run(app, port=5001)`

2. **Module not found errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

3. **WebSocket connection issues**:
   - Check firewall settings
   - Ensure eventlet is installed correctly

4. **Slow performance**:
   - Reduce array size
   - Increase animation speed
   - Use a modern browser

## Optional Enhancements

1. **Add more algorithms**:
   - Shell Sort
   - Radix Sort
   - Counting Sort

2. **Additional features**:
   - Sound effects for comparisons/swaps
   - Algorithm complexity information
   - Step-by-step explanation mode
   - Save/load array configurations

3. **Performance optimizations**:
   - Use requestAnimationFrame for smoother animations
   - Implement virtual scrolling for large arrays
   - Add WebWorkers for heavy computations

## Browser Compatibility

The application works best on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is provided as educational material. Feel free to modify and extend it for learning purposes.v