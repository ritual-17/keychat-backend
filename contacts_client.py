import socketio
import uuid  # To generate unique data

# Setup Socket.IO client
sio = socketio.Client()

# Generate unique test data for two users
fake_email1 = f"user1_{uuid.uuid4()}@example.com"
fake_name1 = f"User 1 {uuid.uuid4()}"
fake_email2 = f"user2_{uuid.uuid4()}@example.com"
fake_name2 = f"User 2 {uuid.uuid4()}"

# To be set after creating an employee
employee_id1 = None
employee_id2 = None

@sio.event
def connect():
    print('Connection established')

    # Test adding first employee
    sio.emit('add_employee', {
        'name': fake_name1,
        'email': fake_email1,
        'position': 'Developer',
        'passwordHash': 'hashed_password1',
        'displayName': fake_name1,
        'profilePicture': 'default1.jpg',
        'status': 'active'
    })

@sio.event
def employee_added(data):
    global employee_id1, employee_id2

    if employee_id1 is None:
        employee_id1 = data['employee_id']
        print('First employee added:', data)

        # Add the second employee after the first one is added
        sio.emit('add_employee', {
            'name': fake_name2,
            'email': fake_email2,
            'position': 'Manager',
            'passwordHash': 'hashed_password2',
            'displayName': fake_name2,
            'profilePicture': 'default2.jpg',
            'status': 'active'
        })
    else:
        employee_id2 = data['employee_id']
        print('Second employee added:', data)

        # Now, add the second employee to the first employee's contact list
        sio.emit('add_contact', (employee_id1, employee_id2))

@sio.event
def contact_added(data):
    print('Contact added:', data)

    # After adding the contact, retrieve the updated contact list
    sio.emit('get_user_contacts', employee_id1)

@sio.event
def user_contacts(data):
    print('User contacts:', data)
    sio.disconnect()

# @sio.event
# def employee_data(data):
#     print('Employee data:', data)

def main():
    sio.connect('http://localhost:8080')  # or your server URL

if __name__ == '__main__':
    main()
