# WebSocket-Based Library Locker System v0.2

A real-time web application for managing library locker assignments with WebSocket-powered instant updates and comprehensive admin monitoring.

## New in v0.2: Admin Panel
- **Real-time Admin Dashboard**: Monitor all locker activity in real-time
- **Force Exit Capability**: Administrators can free up lockers when needed
- **Detailed Analytics**: View current assignments and historical data
- **System Overview**: See available/occupied locker statistics at a glance

## Features

### User Features
- **Real-time Locker Assignment**: Instant locker assignment with live updates
- **Self-service Exit**: Students can free their lockers when done
- **Assignment History**: View recent locker activity
- **Responsive Design**: Works on all devices

### Admin Features
- **Live System Monitoring**: Track all active assignments
- **Administrative Controls**: Force exit capability for lockers
- **Comprehensive Statistics**: View usage patterns and trends
- **Activity Log**: Detailed history of all locker events

## Project Structure

```
locker-system/
├── app.py                 # Main Flask backend with WebSocket support
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html         # User interface
│   └── admin.html         # Admin dashboard interface
└── locker_data.json       # Auto-generated data file
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

The server will start with:
- User interface: `http://localhost:5001`
- Admin interface: `http://localhost:5001/admin`

### 3. Access the Interfaces

**For Students:**
```
http://localhost:5001
```

**For Administrators:**
```
http://localhost:5001/admin
```

## How to Use

### Student Interface
1. Enter your enrollment number
2. Click "Assign Locker" to get a locker assignment
3. Click "Exit Locker" when finished to free your locker
4. View real-time updates of locker availability

### Admin Interface
1. View current locker assignments
2. Monitor system statistics
3. Review recent activity history
4. Force exit lockers when necessary

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
- `force_exit`: Admin request to force exit a locker
- `get_admin_status`: Request detailed admin status

### Server to Client
- `status_update`: Real-time status updates
- `admin_update`: Detailed admin dashboard updates
- `assignment_result`: Response to assignment request
- `exit_result`: Response to exit request
- `admin_message`: Admin-specific notifications
- `sample_data`: Sample enrollment data

## Configuration

- **Total Lockers**: 150 (configurable in `app.py`)
- **Data File**: `locker_data.json` (auto-created)
- **Server Port**: 5000 (configurable in `app.py`)
- **Admin Secret**: Configure in `app.py` for production

## Key Improvements Over v0.1

1. **Admin Dashboard**:  For real-time monitoring capabilities
2. **Enhanced Controls**: Administrative override capabilities
3. **Split interfaces**: For better security and usability
4. **Detailed Analytics**: More comprehensive statistics
5. **Better Event Handling**: More robust WebSocket communication
6. **Complete History**: Full audit trail of all actions

## Production Deployment

For production deployment:

1. Set proper secret keys in `app.py`
2. Secure admin interface with authentication
3. Use a production WSGI server like Gunicorn
4. Configure reverse proxy (nginx) with WebSocket support
5. Set up proper logging and monitoring
6. Implement regular data backups

## Troubleshooting

- **Connection Issues**: Ensure WebSocket protocol is supported
- **Data Not Updating**: Check browser console for errors
- **Admin Features Not Working**: Verify correct admin URL
- **Port Conflicts**: Change port in `app.py` if needed

## Future Roadmap

- User authentication system
- Usage reporting and analytics
- Mobile app integration
- RFID/NFC support for physical access