from typing import Union
from fastapi import FastAPI
import eventlet
import socketio
import KDC

sio = socketio.Server()
app = socketio.WSGIApp(sio)
kdc = KDC.KDC(user_secrets, service_secrets)
clients = []

@sio.event
def register(sid, username):
  sio.emit('tgt_get', kdc.register(username))
  kdc.add_user(username, sid)

@sio.event
def disconnect(sid):
  kdc.remove_user(sid)
  print('disconnect ', sid)

@sio.event
def get_ticket(sid, username, recipient, tgt):
  sio.emit('ticket_get', kdc.return_ticket(username, recipient, tgt))

def refresh_keys(sid):
  for user in kdc.active_users:
    sio.emit('start_key_update')

@sio.event
def update_tgt(sid, tgt):


@sio.event
def update(sid, data):
  print("Received", data, "from", sid)
  for client in clients:
    if client != sid:
      print("Sent to", sid)
      sio.emit('message', data)
  return 'OK', 123

if __name__ == '__main__':
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
