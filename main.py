import eventlet
import socketio
import threading

import KDC

sio = socketio.Server()
app = socketio.WSGIApp(sio)
user_secrets = {}
service_secrets = {}
kdc = KDC.KDC(user_secrets, service_secrets)

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

if __name__ == '__main__':
  threading.Thread(target=refresh_keys, daemon=True).start()
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
