# WebSocket-Based Library Locker System

This is a real-time web application for managing library locker assignments using WebSockets for instant updates across all connected clients.

## Features

- **Real-time Updates**: All clients receive instant updates when lockers are assigned or freed
- **Modern Web Interface**: Responsive design that works on desktop and mobile
- **Persistent Data**: All assignments and history are saved to JSON file
- **Multi-client Support**: Multiple users can use the system simultaneously
- **Live Connection Status**: Shows connection status to the server

## Project Structure

```
locker-system/
├── app.py                 # Flask backend with WebSocket support
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML with embedded CSS and JavaScript
└── locker_data.json      # Auto-generated data file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5005`

### 3. Access the Application

Open your web browser and navigate to:
```
http://localhost:5005
```

## How to Use

1. **Enter Enrollment Number**: Type a valid enrollment number (see sample data)
2. **Assign Locker**: Click "Assign Locker" to get a locker assignment
3. **Exit Locker**: Click "Exit Locker" to free up your assigned locker
4. **Real-time Updates**: Watch the status update in real-time as other users assign/exit lockers

## Sample Enrollment Numbers

- CS2021001 - Rahul Sharma
- CS2021002 - Priya Patel  
- EC2021001 - Amit Kumar
- ME2021001 - Sneha Gupta
- CS2021003 - Vikram Singh
- EC2021002 - Anjali Verma
- ME2021002 - Ravi Mehta
- CS2021004 - Pooja Jain
- EC2021003 - Suresh Yadav
- ME2021003 - Kavita Nair

## WebSocket Events

### Client to Server
- `assign_locker`: Request locker assignment
- `exit_locker`: Request locker exit
- `get_status`: Request current status

### Server to Client
- `status_update`: Real-time status updates
- `assignment_result`: Response to assignment request
- `exit_result`: Response to exit request
- `sample_data`: Sample enrollment data

## Configuration

- **Total Lockers**: 150 (configurable in `app.py`)
- **Data File**: `locker_data.json` (auto-created)
- **Server Port**: 5000 (configurable in `app.py`)

## Production Deployment

For production deployment:

1. Set proper secret key in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure reverse proxy (nginx)
4. Use environment variables for configuration
5. Set up proper logging and monitoring

## Key Improvements Over Original

1. **Real-time Synchronization**: Multiple clients stay in sync
2. **Web-based**: No need to install desktop application
3. **Cross-platform**: Works on any device with a web browser
4. **Scalable**: Can handle multiple concurrent users
5. **Modern UI**: Responsive design with better UX
6. **Live Updates**: Instant feedback for all operations