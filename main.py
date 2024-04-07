import eventlet
import socketio
import threading
import base64
import KDC

sio = socketio.Server()
app = socketio.WSGIApp(sio)

usernames = {
  "alice": "password12345678",
  "bob" : "password87654321",
  "cody": "12345678password"
}

user_secrets = {
  "alice": usernames['alice'].encode(),
  "bob": usernames['bob'].encode(),
  "cody": usernames['cody'].encode()
}

contacts = {
  "alice" : ["bob"],
  "bob" : ["alice"],
  "cody": []
}
online_users = []

kdc = KDC.KDC(user_secrets, user_secrets)

@sio.event
def register(sid, username):
  kdc.add_user(username, sid)
  return base64.b64encode(kdc.register(username)).decode()

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
def get_contacts(sid, data):
  return ",".join(contacts[data])

@sio.event
def add_contact(sid, data):
  contact, user = data.split(',')
  if contact in usernames.keys() and contact not in contacts[user]:
    contacts[user].append(contact)
    return 100
  else:
    return 200

@sio.event
def update_key(sid, tgt):
  return kdc.update_key(tgt)

@sio.event
def get_login(sid, data):
  username, password = data.split(",")
  if username in usernames.keys():
    if usernames[username] == password:
      online_users.append(username)
      return 100
    else:
      return 200
  else:
    return 200

@sio.event
def request_logs(sid, username, recipient, ticket):
  pass

def get_user_from_sid(sid):
  for username in online_users.keys():
    if online_users[username] == sid:
      online_users.pop(username)
      return username
  return "unknown"

if __name__ == '__main__':
  threading.Thread(target=refresh_keys, daemon=True).start()
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
