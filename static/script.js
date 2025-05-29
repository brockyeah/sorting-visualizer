/**
 * Sorting Algorithm Visualizer - Frontend JavaScript
 * Handles UI interactions, WebSocket communication, and visualization rendering
 */

// Global variables
let socket = null;
let array = [];
let arraySize = 50;
let isSorting = false;
let isPaused = false;
let comparisons = 0;
let swaps = 0;

// DOM elements
const algorithmSelect = document.getElementById('algorithm-select');
const arraySizeSlider = document.getElementById('array-size');
const sizeValue = document.getElementById('size-value');
const speedSlider = document.getElementById('speed-control');
const speedValue = document.getElementById('speed-value');
const startBtn = document.getElementById('start-btn');
const pauseBtn = document.getElementById('pause-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const reverseBtn = document.getElementById('reverse-btn');
const resetBtn = document.getElementById('reset-btn');
const barsContainer = document.getElementById('bars-container');
const currentAlgorithmDisplay = document.getElementById('current-algorithm');
const statusDisplay = document.getElementById('status');
const comparisonsDisplay = document.getElementById('comparisons');
const swapsDisplay = document.getElementById('swaps');

// Initialize WebSocket connection
function initializeSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to server');
        updateStatus('Connected');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateStatus('Disconnected');
    });
    
    socket.on('update_state', (state) => {
        updateVisualization(state);
    });
    
    socket.on('sorting_complete', () => {
        isSorting = false;
        isPaused = false;
        updateStatus('Completed');
        updateButtonStates();
        animateCompletion();
    });
    
    socket.on('paused', () => {
        updateStatus('Paused');
    });
    
    socket.on('resumed', () => {
        updateStatus('Sorting');
    });
}

// Initialize the application
function init() {
    initializeSocket();
    generateArray();
    renderBars();
    setupEventListeners();
    updateCurrentAlgorithm();
}

// Generate a random array
function generateArray() {
    array = [];
    for (let i = 0; i < arraySize; i++) {
        array.push(Math.floor(Math.random() * 90) + 10);
    }
}

// Render bars based on array values
function renderBars() {
    barsContainer.innerHTML = '';
    const containerWidth = barsContainer.clientWidth;
    const barWidth = Math.max(1, Math.floor(containerWidth / array.length) - 2);
    
    array.forEach((value, index) => {
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = `${value}%`;
        bar.style.width = `${barWidth}px`;
        bar.dataset.index = index;
        bar.dataset.value = value;
        
        // Add hover effect
        bar.addEventListener('mouseenter', (e) => showTooltip(e, value));
        bar.addEventListener('mouseleave', hideTooltip);
        
        barsContainer.appendChild(bar);
    });
}

// Update visualization based on state
function updateVisualization(state) {
    const bars = document.querySelectorAll('.bar');
    
    // Update array values and bar heights
    if (state.array) {
        state.array.forEach((value, index) => {
            if (bars[index]) {
                bars[index].style.height = `${value}%`;
                bars[index].dataset.value = value;
            }
        });
    }
    
    // Reset all bar classes
    bars.forEach(bar => {
        bar.className = 'bar';
    });
    
    // Apply state-specific classes
    if (state.comparing) {
        state.comparing.forEach(index => {
            if (bars[index]) bars[index].classList.add('comparing');
        });
        comparisons++;
        comparisonsDisplay.textContent = comparisons;
    }
    
    if (state.swapping) {
        state.swapping.forEach(index => {
            if (bars[index]) bars[index].classList.add('swapping');
        });
        swaps++;
        swapsDisplay.textContent = swaps;
    }
    
    if (state.sorted) {
        state.sorted.forEach(index => {
            if (bars[index]) bars[index].classList.add('sorted');
        });
    }
    
    if (state.pivot !== undefined && bars[state.pivot]) {
        bars[state.pivot].classList.add('pivot');
    }
    
    if (state.range) {
        for (let i = state.range[0]; i <= state.range[1]; i++) {
            if (bars[i] && !bars[i].classList.contains('comparing') && 
                !bars[i].classList.contains('swapping')) {
                bars[i].classList.add('range');
            }
        }
    }
    
    // Update background gradient based on progress
    if (state.sorted) {
        const progress = (state.sorted.length / array.length) * 100;
        updateBackgroundProgress(progress);
    }
}

// Update background gradient based on sorting progress
function updateBackgroundProgress(progress) {
    const gradient = document.querySelector('.background-gradient');
    const hue = Math.floor((progress / 100) * 60); // 0 to 60 (red to green)
    gradient.style.background = `linear-gradient(135deg, 
        hsl(${hue}, 50%, 10%) 0%, 
        hsl(${hue + 20}, 40%, 20%) 50%, 
        hsl(${hue}, 50%, 10%) 100%)`;
}

// Animate completion
function animateCompletion() {
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        setTimeout(() => {
            bar.classList.add('sorted');
            bar.style.transform = 'scaleY(1.1)';
            setTimeout(() => {
                bar.style.transform = 'scaleY(1)';
            }, 200);
        }, index * 20);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Array size slider
    arraySizeSlider.addEventListener('input', (e) => {
        arraySize = parseInt(e.target.value);
        sizeValue.textContent = arraySize;
        if (!isSorting) {
            generateArray();
            renderBars();
        }
    });
    
    // Speed slider
    speedSlider.addEventListener('input', (e) => {
        const speed = parseInt(e.target.value);
        speedValue.textContent = speed;
        if (socket) {
            socket.emit('update_speed', { speed });
        }
    });
    
    // Algorithm selection
    algorithmSelect.addEventListener('change', updateCurrentAlgorithm);
    
    // Control buttons
    startBtn.addEventListener('click', startSorting);
    pauseBtn.addEventListener('click', pauseSorting);
    shuffleBtn.addEventListener('click', shuffleArray);
    reverseBtn.addEventListener('click', reverseArray);
    resetBtn.addEventListener('click', resetVisualizer);
}

// Start sorting
function startSorting() {
    if (isSorting && !isPaused) return;
    
    if (isPaused) {
        resumeSorting();
        return;
    }
    
    isSorting = true;
    isPaused = false;
    comparisons = 0;
    swaps = 0;
    comparisonsDisplay.textContent = '0';
    swapsDisplay.textContent = '0';
    
    const algorithm = algorithmSelect.value;
    const speed = parseInt(speedSlider.value);
    
    updateStatus('Sorting');
    updateButtonStates();
    
    socket.emit('start_sort', {
        algorithm,
        array: array.slice(),
        speed
    });
}

// Pause sorting
function pauseSorting() {
    if (!isSorting || isPaused) return;
    
    isPaused = true;
    socket.emit('pause_sort');
    updateButtonStates();
}

// Resume sorting
function resumeSorting() {
    if (!isSorting || !isPaused) return;
    
    isPaused = false;
    socket.emit('resume_sort');
    updateButtonStates();
}

// Shuffle array
function shuffleArray() {
    if (isSorting) return;
    
    generateArray();
    renderBars();
    updateStatus('Ready');
    
    // Add shuffle animation
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        bar.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            bar.style.transform = 'translateY(0)';
        }, index * 10);
    });
}

// Reverse array
function reverseArray() {
    if (isSorting) return;
    
    array = array.sort((a, b) => b - a);
    renderBars();
    updateStatus('Ready');
    
    // Add reverse animation
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, index) => {
        bar.style.transform = 'scaleX(-1)';
        setTimeout(() => {
            bar.style.transform = 'scaleX(1)';
        }, 200);
    });
}

// Reset visualizer
function resetVisualizer() {
    if (isSorting) {
        socket.emit('stop_sort');
    }
    
    isSorting = false;
    isPaused = false;
    comparisons = 0;
    swaps = 0;
    comparisonsDisplay.textContent = '0';
    swapsDisplay.textContent = '0';
    
    generateArray();
    renderBars();
    updateStatus('Ready');
    updateButtonStates();
    updateBackgroundProgress(0);
}

// Update button states
function updateButtonStates() {
    if (isSorting) {
        startBtn.disabled = isPaused ? false : true;
        startBtn.textContent = isPaused ? 'Resume' : 'Start';
        pauseBtn.disabled = isPaused ? true : false;
        shuffleBtn.disabled = true;
        reverseBtn.disabled = true;
        algorithmSelect.disabled = true;
        arraySizeSlider.disabled = true;
    } else {
        startBtn.disabled = false;
        startBtn.textContent = 'Start';
        pauseBtn.disabled = true;
        shuffleBtn.disabled = false;
        reverseBtn.disabled = false;
        algorithmSelect.disabled = false;
        arraySizeSlider.disabled = false;
    }
}

// Update current algorithm display
function updateCurrentAlgorithm() {
    const algorithm = algorithmSelect.value;
    const algorithmNames = {
        'bubble': 'Bubble Sort',
        'selection': 'Selection Sort',
        'insertion': 'Insertion Sort',
        'merge': 'Merge Sort',
        'quick': 'Quick Sort',
        'heap': 'Heap Sort'
    };
    currentAlgorithmDisplay.textContent = algorithmNames[algorithm];
}

// Update status display
function updateStatus(status) {
    statusDisplay.textContent = status;
    
    // Add visual feedback
    statusDisplay.style.opacity = '0';
    setTimeout(() => {
        statusDisplay.style.opacity = '1';
    }, 100);
}

// Tooltip functions
function showTooltip(event, value) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = `Value: ${value}`;
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
    
    setTimeout(() => {
        tooltip.classList.add('show');
    }, 10);
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);