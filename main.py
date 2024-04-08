import json
import eventlet
import socketio
import threading
import base64
from controllers.employee_controller import Employee
from controllers.contacts_controller import ContactsController  # Adjust the import path as necessary
from controllers.chat_controller import ChatController
from controllers.contacts_controller import ContactsController
from bson import ObjectId
from controllers.announcement_controller import AnnouncementController



import KDC

sio = socketio.Server()
app = socketio.WSGIApp(sio)
contacts_controller = ContactsController()
chat_controller = ChatController()
announcement_controller = AnnouncementController()

usernames = {
  "alice": "password12345678",
  "bob" : "password87654321",
  "cody": "passwordabcdefghi"
}

user_secrets = {
  "alice": usernames['alice'].encode(),
  "bob" : usernames['bob'].encode(),
  "cody": usernames['cody'].encode()
}

shared_keys = {}

kdc = KDC.KDC(user_secrets)

@sio.event
def register(sid, username):
  kdc.add_user(username, sid)
  return kdc.register(username)

@sio.event
def disconnect(sid):
  kdc.remove_user(sid)
  print('disconnect ', sid)

@sio.event
def get_ticket(sid, username, recipient, tgt):
  return kdc.return_ticket(username, recipient, tgt)

def refresh_keys():
  while True:
    threading.Event().wait(300) # refresh every 5 minutes
    for user in kdc.active_users:
      sio.emit('start_key_update', to=user)
      
@sio.event
def use_ticket(sid, username, service, ticket):
  #use service secret key to decrypt ticket
  secret_key = kdc.getServiceKey(service)
  decrypted_ticket = decrypt_shared_key(ticket, secret_key)
  decrypted_ticket_json = json.loads(decrypted_ticket)
  sender = decrypted_ticket_json["sender"]
  
  #make sure sender is the same as the username
  if sender != username:
    return "Invalid ticket"
  shared_key = eval(decrypted_ticket_json["shared_key"])
  shared_key[username] = shared_key

  #return 'ok' reponse encrypted with shared key
  response = encrypt_shared_key("100", shared_key)
  return response


@sio.event
def update_key(sid, tgt):
  return kdc.update_key(tgt)

@sio.event
def get_login(sid, data):
  username, password = data.split(",")
  if username in usernames.keys():
    if usernames[username] == password:
      return 100
    else:
      return 200
  else:
    return 200


@sio.event
def add_employee(sid, employee_data):
    try:
        employee = Employee(employee_data)
        employee_id = employee.add_to_db()
        sio.emit('employee_added', {'employee_id': str(employee_id)}, room=sid)
    except Exception as e:
        sio.emit('employee_add_error', {'error': str(e)}, room=sid)

@sio.event
def get_all_employees(sid):
    try:
        employees = Employee.get_all()  # Use the controller method to get all employees
        for employee in employees:
            employee['_id'] = str(employee['_id'])
        sio.emit('all_employees', employees, room=sid)
    except Exception as e:
        print(f"Error retrieving employees: {e}")
        sio.emit('error', {'error': 'Failed to retrieve employees'}, room=sid)

@sio.event
def get_employee(sid, employee_id):
    try:
        employee = Employee.get(employee_id)  # Use the controller method to get a specific employee
        if employee:
            employee['_id'] = str(employee['_id'])
            sio.emit('employee_data', employee, room=sid)
        else:
            sio.emit('employee_not_found', {'message': 'Employee not found'}, room=sid)
    except Exception as e:
        sio.emit('error', {'error': str(e)}, room=sid)

@sio.event
def update_employee(sid, employee_id, update_data):
    try:
        result = Employee.update(employee_id, update_data)  # Use the controller method to update an employee
        if result.modified_count:
            sio.emit('employee_updated', {'message': 'Employee updated successfully'}, room=sid)
        else:
            sio.emit('employee_not_found', {'message': 'Employee not found'}, room=sid)
    except Exception as e:
        sio.emit('error', {'error': str(e)}, room=sid)

@sio.event
def delete_employee(sid, employee_id):
    try:
        result = Employee.delete(employee_id)  # Use the controller method to delete an employee
        if result.deleted_count:
            sio.emit('employee_deleted', {'message': 'Employee deleted successfully'}, room=sid)
        else:
            sio.emit('employee_not_found', {'message': 'Employee not found'}, room=sid)
    except Exception as e:
        sio.emit('error', {'error': str(e)}, room=sid)


@sio.event
def login(sid, data):
    try:
        email = data['email']
        password_hash = data['password_hash']

        employee = Employee.login(email, password_hash)
        if employee:
            employee['_id'] = str(employee['_id'])  # Convert ObjectId to string for JSON serialization
            sio.emit('login_success', {'employee': employee}, room=sid)
        else:
            sio.emit('login_failed', {'message': 'Invalid email or password'}, room=sid)
    except Exception as e:
        sio.emit('error', {'error': str(e)}, room=sid)



@sio.event
def add_contact(sid, user_id, contact_user_id):
    try:
        contact_id = contacts_controller.add_contact(user_id, contact_user_id)
        sio.emit('contact_added', {'contact_id': str(contact_id)}, room=sid)
    except Exception as e:
        sio.emit('contact_error', {'error': str(e)}, room=sid)


@sio.event
def get_user_contacts(sid, user_id):
    try:
        print("Getting contacts for SID:", sid)
        contacts = contacts_controller.get_contacts(user_id)
        if contacts:
            print("contact not null", contacts)
            # Convert ObjectId to string
            contacts['_id'] = str(contacts['_id'])
            contacts['userId'] = str(contacts['userId'])
            contacts['contacts'] = [{'contactUserId': str(c['contactUserId'])} for c in contacts['contacts']]
            print("Sending contacts to SID:", sid)
            sio.emit('user_contacts', contacts, room=sid)
        else:
            print("No contacts found for SID:", sid)
            sio.emit('no_contacts_found', {'message': 'No contacts found'}, room=sid)
    except Exception as e:
        print("Error for SID:", sid, str(e))
        sio.emit('error', {'error': str(e)}, room=sid)


@sio.event
def create_chat(sid, participants, subject):
    try:
        chat_id = chat_controller.create_chat(participants, subject)
        sio.emit('chat_created', {'chat_id': str(chat_id)}, room=sid)
    except Exception as e:
        sio.emit('chat_error', {'error': str(e)}, room=sid)

@sio.event
def add_chat_message(sid, chat_id, sender_id, content):
    try:
        result = chat_controller.add_message(chat_id, sender_id, content)
        if result.modified_count:
            sio.emit('message_added', {'chat_id': chat_id}, room=sid)
        else:
            sio.emit('message_error', {'error': 'Message not added'}, room=sid)
    except Exception as e:
        sio.emit('error', {'error': str(e)}, room=sid)

@sio.event
def get_chat(sid, chat_id):
    try:
        print(f"GET CHAT IS CALLED for SID: {sid} and chat_id: {chat_id}")
        chat = chat_controller.get_chat(chat_id)
        print(f"Chat data retrieved: {chat}")

        if chat:
            chat['_id'] = str(chat['_id'])
            chat['participants'] = [str(participant) for participant in chat['participants']]
            chat['createdAt'] = chat['createdAt'].isoformat() if 'createdAt' in chat else 'Unknown'
            chat['messages'] = [
                {
                    **message,
                    'messageId': str(message['messageId']),
                    'senderId': str(message['senderId']),
                    'sentAt': message['sentAt'].isoformat() if 'sentAt' in message else 'Unknown',
                    'status': message.get('status', 'Unknown')
                } for message in chat['messages']
            ]

            print(f"Emitting chat_retrieved for chat {chat['_id']}")
            sio.emit('chat_retrieved', chat, room=sid)
        else:
            print("Chat not found.")
            sio.emit('chat_not_found', {'message': 'Chat not found'}, room=sid)
    except Exception as e:
        print(f"Error in get_chat: {str(e)}")
        sio.emit('error', {'error': str(e)}, room=sid)

# @sio.event
# def create_announcement(sid, title, content, created_by):
#     try:
#         announcement_id = announcement_controller.create_announcement(title, content, created_by)
#         sio.emit('announcement_created', {'announcement_id': str(announcement_id)}, room=sid)
#     except Exception as e:
#         sio.emit('announcement_error', {'error': str(e)}, room=sid)

# @sio.event
# def create_announcement(sid, data):
#     print("Announcement creation attempted", data)
#     try:
#         # Extract information from the data dictionary
#         title = data['title']
#         content = data['content']
#         created_by = data['createdBy']

#         # Corrected print statement
#         print(f"Title: {title}, Content: {content}, Created by: {created_by}")

#         announcement_id = announcement_controller.create_announcement(title, content, created_by)
#         sio.emit('announcement_created', {'announcement_id': str(announcement_id)}, room=sid)
#     except Exception as e:
#         print(f"Error creating announcement: {e}")  # Added print for debugging
#         sio.emit('announcement_error', {'error': str(e)}, room=sid)
@sio.event
def create_announcement(sid, data):
    try:
        title = data['title']
        content = data['content']
        created_by = data.get('createdBy')

        # Validate or generate a new ObjectId
        if not ObjectId.is_valid(created_by):
            created_by = ObjectId()  # Generate a new ObjectId if invalid
            print(f"Generated new ObjectId for createdBy: {created_by}")

        print(f"Title: {title}, Content: {content}, Created by: {created_by}")

        announcement_id = announcement_controller.create_announcement(title, content, created_by)
        sio.emit('announcement_created', {'announcement_id': str(announcement_id)}, room=sid)
    except Exception as e:
        print(f"Error creating announcement: {e}")
        sio.emit('announcement_error', {'error': str(e)}, room=sid)



# @sio.event
# def get_announcement(sid, announcement_id):
#     try:
#         announcement = announcement_controller.get_announcement(announcement_id)
#         if announcement:
#             announcement['_id'] = str(announcement['_id'])
#             announcement['createdBy'] = str(announcement['createdBy'])
#             sio.emit('announcement_retrieved', announcement, room=sid)
#         else:
#             sio.emit('announcement_not_found', {'message': 'Announcement not found'}, room=sid)
#     except Exception as e:
#         sio.emit('error', {'error': str(e)}, room=sid)

@sio.event
def get_announcement(sid, announcement_id):
    try:
        announcement = announcement_controller.get_announcement(announcement_id)
        if announcement:
            announcement['_id'] = str(announcement['_id'])
            announcement['createdBy'] = str(announcement['createdBy'])
            # Convert datetime to string in ISO format
            if 'createdAt' in announcement and announcement['createdAt']:
                announcement['createdAt'] = announcement['createdAt'].isoformat()

            sio.emit('announcement_retrieved', announcement, room=sid)
        else:
            sio.emit('announcement_not_found', {'message': 'Announcement not found'}, room=sid)
    except Exception as e:
        print(f"Error retrieving announcement: {e}")
        sio.emit('error', {'error': str(e)}, room=sid)


# @sio.event
# def get_all_announcements(sid):
#     try:
#         announcements = announcement_controller.get_all_announcements()
#         for announcement in announcements:
#             announcement['_id'] = str(announcement['_id'])
#             announcement['createdBy'] = str(announcement['createdBy'])
#         sio.emit('all_announcements', announcements, room=sid)
#     except Exception as e:
#         sio.emit('error', {'error': str(e)}, room=sid)
@sio.event
def get_all_announcements(sid):
    try:
        announcements = announcement_controller.get_all_announcements()
        for announcement in announcements:
            # Convert ObjectId to string
            announcement['_id'] = str(announcement['_id'])
            announcement['createdBy'] = str(announcement['createdBy'])
            
            # Convert datetime to ISO format string
            if 'createdAt' in announcement and announcement['createdAt']:
                announcement['createdAt'] = announcement['createdAt'].isoformat()

        sio.emit('all_announcements', announcements, room=sid)
    except Exception as e:
        print(f"Error retrieving all announcements: {e}")
        sio.emit('error', {'error': str(e)}, room=sid)



if __name__ == '__main__':
  threading.Thread(target=refresh_keys, daemon=True).start()
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
