from typing import Union
from fastapi import FastAPI
import eventlet
import socketio

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

sio = socketio.Server()
app = socketio.WSGIApp(sio)
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

if __name__ == '__main__':
  eventlet.wsgi.server(eventlet.listen(('',8080)), app)
