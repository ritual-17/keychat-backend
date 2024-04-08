import socketio
import uuid

# Setup Socket.IO client
sio = socketio.Client()

# Unique user data
fake_email1 = f"user1_{uuid.uuid4()}@example.com"
fake_name1 = f"User 1 {uuid.uuid4()}"
fake_email2 = f"user2_{uuid.uuid4()}@example.com"
fake_name2 = f"User 2 {uuid.uuid4()}"

# To be set after creating an employee
employee_id1 = None
employee_id2 = None
chat_id = None

@sio.event
def connect():
    print('Connection established')

    # Add the first employee
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
    global employee_id1, employee_id2, chat_id

    if not employee_id1:
        employee_id1 = data['employee_id']
        print(f'First employee added: {data}')

        # Add the second employee
        sio.emit('add_employee', {
            'name': fake_name2,
            'email': fake_email2,
            'position': 'Manager',
            'passwordHash': 'hashed_password2',
            'displayName': fake_name2,
            'profilePicture': 'default2.jpg',
            'status': 'active'
        })
    elif not employee_id2:
        employee_id2 = data['employee_id']
        print(f'Second employee added: {data}')

        # Create a chat between the two users
        sio.emit('create_chat', ([employee_id1, employee_id2], 'Test Chat'))

@sio.event
def chat_created(data):
    global chat_id
    chat_id = data['chat_id']
    print(f'Chat created: {data}')

    # Start sending messages back and forth
    sio.emit('add_chat_message', (chat_id, employee_id1, 'Hello from User 1'))

@sio.event
def message_added(data):
    print(f'Message added to chat: {data}')
    # Fetch the chat after the first message is added
    sio.emit('get_chat', chat_id)

@sio.event
def chat_retrieved(data):
    print(f'Chat retrieved: {data}')
    # Disconnect after retrieving the chat
    sio.disconnect()

def main():
    sio.connect('http://localhost:8080')  # Change to your server URL

if __name__ == '__main__':
    main()
