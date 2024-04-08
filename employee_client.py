import socketio
import uuid  # To generate unique data

# Setup Socket.IO client
sio = socketio.Client()

# Generate unique test data
fake_email = f"test_{uuid.uuid4()}@example.com"
fake_name = f"Test User {uuid.uuid4()}"
updated_position = f"Updated Position {uuid.uuid4()}"
employee_id = None  # To be set after creating an employee

@sio.event
def connect():
    print('Connection established')
    
    # Test adding an employee
    sio.emit('add_employee', {
        'name': fake_name,
        'email': fake_email,
        'position': 'Developer',
        'passwordHash': 'hashed_password_example',
        'displayName': fake_name,
        'profilePicture': 'default.jpg',
        'status': 'active'
    })

# @sio.event
# def employee_added(data):
#     global employee_id
#     employee_id = data['employee_id']
#     print('Employee added:', data)

#     # After adding, test getting this employee's data
#     sio.emit('get_employee', employee_id)


@sio.event
def employee_added(data):
    global employee_id
    employee_id = data['employee_id']
    print('Employee added:', data)

    # After adding, attempt to login with the added employee's credentials
    # Ensure that the 'login' event is called with the correct parameters
    sio.emit('login', {'email': fake_email, 'password_hash': 'hashed_password_example'})


@sio.event
def login_success(data):
    print('Login successful:', data)
    # Proceed with other tests or actions after successful login

    # After adding, test getting this employee's data
    sio.emit('get_employee', employee_id)

@sio.event
def employee_data(data):
    print('Employee data:', data)
    
    # Test updating the employee
    sio.emit('update_employee', (employee_id, {'position': "random"}))

@sio.event
def employee_updated(data):
    print('Employee updated:', data)
    
    sio.emit('get_employee', employee_id)

@sio.event
def get_updated_employee(data):
    print('Updated Employee data:', data)
    
    # Test deleting the employee
    sio.emit('delete_employee', employee_id)

@sio.event
def login_failed(data):
    print('Login failed:', data)
    sio.disconnect()

@sio.event
def employee_deleted(data):
    print('Employee deleted:', data)
    sio.disconnect()

@sio.event
def employee_not_found(data):
    print('Employee not found:', data)
    sio.disconnect()

@sio.event
def error(data):
    print('Error:', data)
    sio.disconnect()

@sio.event
def disconnect():
    print('Disconnected from server')

if __name__ == '__main__':
    sio.connect('http://localhost:8080')
