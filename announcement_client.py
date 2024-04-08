import socketio
import uuid

# Setup Socket.IO client
sio = socketio.Client()

# Unique announcement data
fake_title = f"Announcement {uuid.uuid4()}"
fake_content = "This is a test announcement content."

# To be set after creating an announcement
announcement_id = None

@sio.event
def connect():
    print('Connection established')
    
    # Test creating an announcement
    sio.emit('create_announcement', {
        'title': fake_title,
        'content': fake_content,
        'createdBy': 'SomeUserId'  # Assuming you have a user ID to use here
    })

@sio.event
def announcement_created(data):
    global announcement_id
    announcement_id = data['announcement_id']
    print(f'Announcement created: {data}')

    # Test getting this announcement's data
    sio.emit('get_announcement', announcement_id)

@sio.event
def announcement_retrieved(data):
    print('Announcement data:', data)
    
    # Test getting all announcements
    sio.emit('get_all_announcements')

@sio.event
def all_announcements(data):
    print('All announcements:', data)
    sio.disconnect()

@sio.event
def announcement_not_found(data):
    print('Announcement not found:', data)
    sio.disconnect()

@sio.event
def error(data):
    print('Error:', data)
    sio.disconnect()

@sio.event
def disconnect():
    print('Disconnected from server')

def main():
    sio.connect('http://localhost:8080')  # Change to your server URL

if __name__ == '__main__':
    main()
