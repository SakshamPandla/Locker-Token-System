from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
from datetime import datetime
from typing import Dict, Set, Optional
import threading

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
            'ME2021003': {'name': 'Kavita Nair', 'course': 'Mechanical'},
            'CS2021005': {'name': 'Deepak Tiwari', 'course': 'Computer Science'},
            'EC2021004': {'name': 'Meera Saxena', 'course': 'Electronics'},
            'ME2021004': {'name': 'Arjun Reddy', 'course': 'Mechanical'},
            'CS2021006': {'name': 'Sonia Agarwal', 'course': 'Computer Science'},
            'EC2021005': {'name': 'Karan Malhotra', 'course': 'Electronics'}
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
    
    def get_detailed_status(self):
        """Get detailed status for admin"""
        current_assignments = []
        for enrollment, locker in self.locker_assignments.items():
            student = self.student_database.get(enrollment, {'name': 'Unknown', 'course': 'Unknown'})
            current_assignments.append({
                'enrollment': enrollment,
                'name': student['name'],
                'course': student['course'],
                'locker': locker,
                'assigned_time': self.get_assignment_time(enrollment, locker)
            })
        
        return {
            'current_assignments': current_assignments,
            'total_assignments': len(current_assignments),
            'available_lockers': self.total_lockers - len(self.occupied_lockers),
            'occupied_lockers': len(self.occupied_lockers),
            'total_lockers': self.total_lockers,
            'recent_history': self.assignment_history[-10:][::-1]  # Last 10 entries, reversed
        }
    
    def get_assignment_time(self, enrollment, locker):
        """Get assignment time for a specific enrollment and locker"""
        for entry in reversed(self.assignment_history):
            if entry['enrollment'] == enrollment and entry['locker'] == locker and entry['action'] == 'assigned':
                return entry['timestamp']
        return None
    
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
        
        # Notify all clients
        self.notify_all()
        
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
        
        # Notify all clients
        self.notify_all()
        
        return {
            'success': True,
            'message': f'Locker {locker_number} freed successfully. Thank you!',
            'type': 'success'
        }
    
    def force_exit_locker(self, enrollment):
        """Force exit locker (admin function)"""
        result = self.exit_locker(enrollment)
        if result['success']:
            # Add admin action to history
            self.assignment_history.append({
                'enrollment': enrollment,
                'name': 'Admin Action',
                'locker': 0,
                'action': 'admin_force_exit',
                'timestamp': datetime.now().isoformat()
            })
            self.save_data()
            self.notify_all()
        return result
    
    def notify_all(self):
        """Notify all connected clients of updates"""
        # This will be called from the SocketIO context
        socketio.emit('status_update', self.get_status())
        socketio.emit('admin_update', self.get_detailed_status())

# Initialize the locker system
locker_system = LockerSystem()

# User-facing routes
@app.route('/')
def index():
    return render_template('index.html')

# Admin routes
@app.route('/admin')
def admin_index():
    return render_template('admin.html')

@app.route('/api/status')
def admin_api_status():
    return jsonify(locker_system.get_detailed_status())

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
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

@socketio.on('get_status')
def handle_get_status():
    """Handle status request"""
    emit('status_update', locker_system.get_status())

@socketio.on('force_exit')
def handle_admin_force_exit(data):
    """Handle admin force exit request"""
    enrollment = data.get('enrollment', '')
    
    if not enrollment:
        emit('admin_message', {
            'message': 'Please provide enrollment number',
            'type': 'error'
        })
        return
    
    result = locker_system.force_exit_locker(enrollment)
    
    # Send response to requesting admin client
    emit('admin_message', {
        'message': result['message'],
        'type': result['type']
    })

@socketio.on('get_admin_status')
def handle_get_admin_status():
    """Handle admin status request"""
    emit('admin_update', locker_system.get_detailed_status())

if __name__ == '__main__':
    print("Starting Library Locker System...")
    print("User Interface: http://localhost:5001")
    print("Admin Interface: http://localhost:5001/admin")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)