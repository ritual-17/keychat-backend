import eventlet
import socketio
import threading
import base64
from controllers.employee_controller import Employee
from controllers.contacts_controller import ContactsController  # Adjust the import path as necessary
from controllers.chat_controller import ChatController
from controllers.contacts_controller import ContactsController
from bson import ObjectId

import KDC

sio = socketio.Server()
app = socketio.WSGIApp(sio)
contacts_controller = ContactsController()
chat_controller = ChatController()

usernames = {
  "alice": "password123",
  "bob" : "password456",
  "cody": "password789"
}

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
def update_key(sid, tgt):
  return kdc.update_key(tgt)

@sio.event
def get_login(sid, data):
  username, password = data.split(",")
  if username in usernames.keys():
    if usernames[username] == password:
      sio.emit("login_success")
    else:
      sio.emit("login_failure")
  else:
    sio.emit("login_failure")


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




if __name__ == '__main__':
  threading.Thread(target=refresh_keys, daemon=True).start()
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
