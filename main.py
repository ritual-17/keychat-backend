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
def connect(sid, env):
  clients.append(sid)
  print('connect ', sid)

@sio.event
def disconnect(sid):
  clients.remove(sid)
  print('disconnect ', sid)

@sio.event
def connected(sid, data):
  print(data)

@sio.event
def register(sid, username):
  pass

def get_ticket(sid, recipient, tgt):
  pass

@sio.event
def send_message(sid, data):
  print("Received", data, "from", sid)
  for client in clients:
    if client != sid:
      print("Sent to", sid)
      sio.emit('message', data)
  return 'OK', 123

if __name__ == '__main__':
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
