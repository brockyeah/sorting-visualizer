"""
Sorting Algorithm Visualizer - Backend Server
A Flask application that provides sorting algorithm implementations
and WebSocket support for real-time visualization updates.
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import json
from typing import List, Dict, Tuple
import os

# Initialize Flask app and SocketIO for real-time communication
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

class SortingVisualizer:
    """
    Main class handling all sorting algorithms and visualization logic.
    Each sorting method yields states for visualization.
    """
    
    def __init__(self):
        self.array = []
        self.sorting = False
        self.paused = False
        self.speed = 50  # Default delay in milliseconds
        
    def bubble_sort(self, arr: List[int]) -> Dict:
        """
        Bubble Sort implementation with visualization states.
        Compares adjacent elements and swaps if they're in wrong order.
        """
        n = len(arr)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                # Yield comparison state
                yield {
                    'array': arr.copy(),
                    'comparing': [j, j + 1],
                    'sorted': list(range(n - i, n)),
                    'type': 'compare'
                }
                
                if arr[j] > arr[j + 1]:
                    # Swap elements
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
                    
                    # Yield swap state
                    yield {
                        'array': arr.copy(),
                        'swapping': [j, j + 1],
                        'sorted': list(range(n - i, n)),
                        'type': 'swap'
                    }
            
            # If no swaps occurred, array is sorted
            if not swapped:
                break
        
        # Final sorted state
        yield {
            'array': arr.copy(),
            'sorted': list(range(n)),
            'type': 'complete'
        }
    
    def selection_sort(self, arr: List[int]) -> Dict:
        """
        Selection Sort implementation.
        Finds minimum element and places it at the beginning.
        """
        n = len(arr)
        for i in range(n):
            min_idx = i
            
            # Find minimum element in remaining unsorted array
            for j in range(i + 1, n):
                yield {
                    'array': arr.copy(),
                    'comparing': [min_idx, j],
                    'sorted': list(range(i)),
                    'type': 'compare'
                }
                
                if arr[j] < arr[min_idx]:
                    min_idx = j
            
            # Swap minimum element with first element
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                yield {
                    'array': arr.copy(),
                    'swapping': [i, min_idx],
                    'sorted': list(range(i + 1)),
                    'type': 'swap'
                }
        
        yield {
            'array': arr.copy(),
            'sorted': list(range(n)),
            'type': 'complete'
        }
    
    def insertion_sort(self, arr: List[int]) -> Dict:
        """
        Insertion Sort implementation.
        Builds sorted array one element at a time.
        """
        n = len(arr)
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            
            # Move elements greater than key one position ahead
            while j >= 0 and arr[j] > key:
                yield {
                    'array': arr.copy(),
                    'comparing': [j, j + 1],
                    'sorted': list(range(i)) if j == i - 1 else [],
                    'type': 'compare'
                }
                
                arr[j + 1] = arr[j]
                j -= 1
                
                yield {
                    'array': arr.copy(),
                    'swapping': [j + 1, j + 2],
                    'type': 'swap'
                }
            
            arr[j + 1] = key
        
        yield {
            'array': arr.copy(),
            'sorted': list(range(n)),
            'type': 'complete'
        }
    
    def merge_sort(self, arr: List[int], start: int = 0, end: int = None) -> Dict:
        """
        Merge Sort implementation with visualization.
        Divides array into halves, sorts them, and merges.
        """
        if end is None:
            end = len(arr) - 1
        
        if start < end:
            mid = (start + end) // 2
            
            # Recursively sort first and second halves
            yield from self.merge_sort(arr, start, mid)
            yield from self.merge_sort(arr, mid + 1, end)
            
            # Merge the sorted halves
            yield from self.merge(arr, start, mid, end)
    
    def merge(self, arr: List[int], start: int, mid: int, end: int) -> Dict:
        """
        Merge two sorted subarrays arr[start:mid+1] and arr[mid+1:end+1]
        """
        left = arr[start:mid + 1]
        right = arr[mid + 1:end + 1]
        
        i = j = 0
        k = start
        
        while i < len(left) and j < len(right):
            yield {
                'array': arr.copy(),
                'comparing': [start + i, mid + 1 + j],
                'range': [start, end],
                'type': 'compare'
            }
            
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            
            yield {
                'array': arr.copy(),
                'swapping': [k],
                'range': [start, end],
                'type': 'merge'
            }
            k += 1
        
        # Copy remaining elements
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
            yield {
                'array': arr.copy(),
                'swapping': [k - 1],
                'range': [start, end],
                'type': 'merge'
            }
        
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
            yield {
                'array': arr.copy(),
                'swapping': [k - 1],
                'range': [start, end],
                'type': 'merge'
            }
        
        # Check if entire array is sorted
        if start == 0 and end == len(arr) - 1:
            yield {
                'array': arr.copy(),
                'sorted': list(range(len(arr))),
                'type': 'complete'
            }
    
    def quick_sort(self, arr: List[int], low: int = 0, high: int = None) -> Dict:
        """
        Quick Sort implementation with visualization.
        Uses partition method to place pivot in correct position.
        """
        if high is None:
            high = len(arr) - 1
        
        if low < high:
            # Partition the array and get pivot index
            pivot_states = list(self.partition(arr, low, high))
            for state in pivot_states[:-1]:
                yield state
            
            pi = pivot_states[-1]['pivot_index']
            
            # Recursively sort elements before and after partition
            yield from self.quick_sort(arr, low, pi - 1)
            yield from self.quick_sort(arr, pi + 1, high)
        
        # Check if entire array is sorted
        if low == 0 and high == len(arr) - 1:
            yield {
                'array': arr.copy(),
                'sorted': list(range(len(arr))),
                'type': 'complete'
            }
    
    def partition(self, arr: List[int], low: int, high: int) -> Dict:
        """
        Partition function for Quick Sort.
        Places pivot element at its correct position.
        """
        pivot = arr[high]
        i = low - 1  # Index of smaller element
        
        for j in range(low, high):
            yield {
                'array': arr.copy(),
                'comparing': [j, high],
                'pivot': high,
                'range': [low, high],
                'type': 'compare'
            }
            
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                
                if i != j:
                    yield {
                        'array': arr.copy(),
                        'swapping': [i, j],
                        'pivot': high,
                        'range': [low, high],
                        'type': 'swap'
                    }
        
        # Place pivot in correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        yield {
            'array': arr.copy(),
            'swapping': [i + 1, high],
            'pivot': i + 1,
            'range': [low, high],
            'type': 'swap'
        }
        
        yield {'pivot_index': i + 1}
    
    def heap_sort(self, arr: List[int]) -> Dict:
        """
        Heap Sort implementation.
        Builds max heap and extracts elements one by one.
        """
        n = len(arr)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            yield from self.heapify(arr, n, i)
        
        # Extract elements from heap one by one
        for i in range(n - 1, 0, -1):
            arr[i], arr[0] = arr[0], arr[i]
            
            yield {
                'array': arr.copy(),
                'swapping': [0, i],
                'sorted': list(range(i, n)),
                'type': 'swap'
            }
            
            yield from self.heapify(arr, i, 0)
        
        yield {
            'array': arr.copy(),
            'sorted': list(range(n)),
            'type': 'complete'
        }
    
    def heapify(self, arr: List[int], n: int, i: int) -> Dict:
        """
        Heapify subtree rooted at index i.
        """
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        # Compare with left child
        if left < n:
            yield {
                'array': arr.copy(),
                'comparing': [largest, left],
                'type': 'compare'
            }
            
            if arr[left] > arr[largest]:
                largest = left
        
        # Compare with right child
        if right < n:
            yield {
                'array': arr.copy(),
                'comparing': [largest, right],
                'type': 'compare'
            }
            
            if arr[right] > arr[largest]:
                largest = right
        
        # Swap if needed
        if largest != i:
            arr[i], arr[largest] = arr[i], arr[largest]
            
            yield {
                'array': arr.copy(),
                'swapping': [i, largest],
                'type': 'swap'
            }
            
            # Recursively heapify affected subtree
            yield from self.heapify(arr, n, largest)

# Global visualizer instance
visualizer = SortingVisualizer()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to sorting visualizer'})

@socketio.on('start_sort')
def handle_start_sort(data):
    """
    Handle sorting request from client.
    Starts the selected sorting algorithm with given array.
    """
    algorithm = data.get('algorithm')
    array = data.get('array')
    speed = data.get('speed', 50)
    
    visualizer.array = array.copy()
    visualizer.speed = speed
    visualizer.sorting = True
    visualizer.paused = False
    
    # Select sorting algorithm
    if algorithm == 'bubble':
        generator = visualizer.bubble_sort(visualizer.array)
    elif algorithm == 'selection':
        generator = visualizer.selection_sort(visualizer.array)
    elif algorithm == 'insertion':
        generator = visualizer.insertion_sort(visualizer.array)
    elif algorithm == 'merge':
        generator = visualizer.merge_sort(visualizer.array)
    elif algorithm == 'quick':
        generator = visualizer.quick_sort(visualizer.array)
    elif algorithm == 'heap':
        generator = visualizer.heap_sort(visualizer.array)
    else:
        emit('error', {'message': 'Unknown algorithm'})
        return
    
    # Execute sorting and emit states
    for state in generator:
        if not visualizer.sorting:
            break
        
        while visualizer.paused:
            socketio.sleep(0.1)
        
        emit('update_state', state)
        socketio.sleep(visualizer.speed / 1000.0)
    
    visualizer.sorting = False
    emit('sorting_complete', {'message': 'Sorting completed'})

@socketio.on('pause_sort')
def handle_pause_sort():
    """Pause the current sorting visualization"""
    visualizer.paused = True
    emit('paused', {'message': 'Sorting paused'})

@socketio.on('resume_sort')
def handle_resume_sort():
    """Resume the paused sorting visualization"""
    visualizer.paused = False
    emit('resumed', {'message': 'Sorting resumed'})

@socketio.on('stop_sort')
def handle_stop_sort():
    """Stop the current sorting visualization"""
    visualizer.sorting = False
    visualizer.paused = False
    emit('stopped', {'message': 'Sorting stopped'})

@socketio.on('update_speed')
def handle_update_speed(data):
    """Update the visualization speed"""
    visualizer.speed = data.get('speed', 50)
    emit('speed_updated', {'speed': visualizer.speed})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask-SocketIO server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)