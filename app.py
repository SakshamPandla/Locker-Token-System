from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
from datetime import datetime
from typing import Dict, Set, Optional

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

class LockerSystem:
    def __init__(self):
        self.data_file = "locker_data.json"
        self.total_lockers = 150
        
        # Sample student database
        self.student_database = {
            'CS2021001': {'name': 'Rahul Sharma', 'course': 'Computer Science'},
            'CS2021002': {'name': 'Priya Patel', 'course': 'Computer Science'},
            'EC2021001': {'name': 'Amit Kumar', 'course': 'Electronics'},
            'ME2021001': {'name': 'Sneha Gupta', 'course': 'Mechanical'},
            'CS2021003': {'name': 'Vikram Singh', 'course': 'Computer Science'},
            'EC2021002': {'name': 'Anjali Verma', 'course': 'Electronics'},
            'ME2021002': {'name': 'Ravi Mehta', 'course': 'Mechanical'},
            'CS2021004': {'name': 'Pooja Jain', 'course': 'Computer Science'},
            'EC2021003': {'name': 'Suresh Yadav', 'course': 'Electronics'},
            'ME2021003': {'name': 'Kavita Nair', 'course': 'Mechanical'}
        }
        
        # Initialize data
        self.locker_assignments = {}
        self.occupied_lockers = set()
        self.assignment_history = []
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.locker_assignments = data.get('assignments', {})
                    self.occupied_lockers = set(data.get('occupied', []))
                    self.assignment_history = data.get('history', [])
            except Exception as e:
                print(f"Failed to load data: {e}")
    
    def save_data(self):
        """Save data to file"""
        try:
            data = {
                'assignments': self.locker_assignments,
                'occupied': list(self.occupied_lockers),
                'history': self.assignment_history
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save data: {e}")
    
    def get_status(self):
        """Get current system status"""
        available_count = self.total_lockers - len(self.occupied_lockers)
        occupied_count = len(self.occupied_lockers)
        
        return {
            'available': available_count,
            'occupied': occupied_count,
            'total': self.total_lockers
        }
    
    def find_available_locker(self):
        """Find available locker"""
        for i in range(1, self.total_lockers + 1):
            if i not in self.occupied_lockers:
                return i
        return None
    
    def assign_locker(self, enrollment):
        """Assign locker to student"""
        enrollment = enrollment.strip().upper()
        
        # Verify enrollment
        student = self.student_database.get(enrollment)
        if not student:
            return {
                'success': False,
                'message': 'Enrollment number not found. Please check and try again.',
                'type': 'error'
            }
        
        # Check existing assignment
        if enrollment in self.locker_assignments:
            existing_token = self.locker_assignments[enrollment]
            return {
                'success': False,
                'message': f'You already have locker {existing_token} assigned. Please exit first to get a new locker.',
                'type': 'info',
                'assignment': {
                    'student': student,
                    'locker': existing_token,
                    'enrollment': enrollment
                }
            }
        
        # Find available locker
        available_locker = self.find_available_locker()
        if not available_locker:
            return {
                'success': False,
                'message': 'Sorry, all lockers are currently occupied. Please try again later.',
                'type': 'error'
            }
        
        # Assign locker
        self.locker_assignments[enrollment] = available_locker
        self.occupied_lockers.add(available_locker)
        
        # Update history
        self.assignment_history.append({
            'enrollment': enrollment,
            'name': student['name'],
            'locker': available_locker,
            'action': 'assigned',
            'timestamp': datetime.now().isoformat()
        })
        
        # Save data
        self.save_data()
        
        return {
            'success': True,
            'message': f'Locker {available_locker} assigned successfully!',
            'type': 'success',
            'assignment': {
                'student': student,
                'locker': available_locker,
                'enrollment': enrollment
            }
        }
    
    def exit_locker(self, enrollment):
        """Exit locker"""
        enrollment = enrollment.strip().upper()
        
        # Check assignment
        if enrollment not in self.locker_assignments:
            return {
                'success': False,
                'message': 'No locker found for this enrollment number',
                'type': 'error'
            }
        
        locker_number = self.locker_assignments[enrollment]
        student = self.student_database.get(enrollment)
        
        # Remove assignment
        del self.locker_assignments[enrollment]
        self.occupied_lockers.discard(locker_number)
        
        # Update history
        self.assignment_history.append({
            'enrollment': enrollment,
            'name': student['name'] if student else 'Unknown',
            'locker': locker_number,
            'action': 'exited',
            'timestamp': datetime.now().isoformat()
        })
        
        # Save data
        self.save_data()
        
        return {
            'success': True,
            'message': f'Locker {locker_number} freed successfully. Thank you!',
            'type': 'success'
        }

# Initialize the locker system
locker_system = LockerSystem()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Send initial status and sample data
    emit('status_update', locker_system.get_status())
    emit('sample_data', locker_system.student_database)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('assign_locker')
def handle_assign_locker(data):
    """Handle locker assignment request"""
    enrollment = data.get('enrollment', '')
    
    if not enrollment or enrollment.lower() == 'e.g., cs2021001':
        emit('message', {
            'message': 'Please enter your enrollment number',
            'type': 'error'
        })
        return
    
    result = locker_system.assign_locker(enrollment)
    
    # Send response to requesting client
    emit('assignment_result', result)
    
    # Broadcast status update to all clients
    socketio.emit('status_update', locker_system.get_status())

@socketio.on('exit_locker')
def handle_exit_locker(data):
    """Handle locker exit request"""
    enrollment = data.get('enrollment', '')
    
    if not enrollment or enrollment.lower() == 'e.g., cs2021001':
        emit('message', {
            'message': 'Please enter your enrollment number to exit',
            'type': 'error'
        })
        return
    
    result = locker_system.exit_locker(enrollment)
    
    # Send response to requesting client
    emit('exit_result', result)
    
    # Broadcast status update to all clients
    socketio.emit('status_update', locker_system.get_status())

@socketio.on('get_status')
def handle_get_status():
    """Handle status request"""
    emit('status_update', locker_system.get_status())

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5005)