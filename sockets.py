#! /usr/bin/python -tt
from tornado import websocket
from tornado import web
from tornado import ioloop
from tornado.options import options
from json import dumps, loads
from time import time
import os

class WebSocket(websocket.WebSocketHandler):
  
  def open(self):
    print 'WebSocket opened'
    self.application.add_socket(self)

  def on_message(self, message):
    incoming = loads(message)
    print incoming
    action = incoming.get("action")
    item = incoming.get("name")
    if action == 'add' :
      self.application.add_item(item, self)
      self.write_message(dumps({'action':'ACK', 'name': item}))
    elif action == 'delete' :
      self.application.delete_message(item, self)
      self.write_message(dumps({'action':'ACK', 'name':item}))
    elif action == 'ping' :
      self.write_message(dumps({'action':'pong'}))

  def on_close(self):
    print 'WebSocket closed'
    self.application.remove_socket(self)

class Main(web.RequestHandler):
  
  @web.addslash
  def get(self):
    self.set_header('text/html', 'charset=UTF-8')
    self.render("frontend.html")

class ListHandler(web.RequestHandler):
  def get(self):
    self.set_header('Content-Type', 'application/json')
    self.write(dumps({"list" : list(self.application.data), 'last_update' : self.application.last_update}))
    self.flush()

  def post(self):
    self.set_header('Connection', 'close')
    self.set_status(200)
    self.application.data.append(self.get_argument('message'))

class Status(web.RequestHandler):
  @web.removeslash
  def get(self):
    self.set_header('text/html', 'charset=UTF-8')
    self.render("status.html", sockets=self.application.sockets)

class Application(web.Application):
  
  def __init__(self):
    handlers = [
      (r'/list/socket', WebSocket),
      (r'/list/api', ListHandler),
      (r'/list[/]?', Main),
      (r'/list/socket/status[/]?', Status)
    ]
    settings = { 
        'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path' : os.path.join(os.path.dirname(__file__), 'static'),
        'debug': True
    }
    self.data = set()
    self.sockets = []
    self.last_update = int(time())
    web.Application.__init__(self, handlers, **settings)

  def add_item(self, message, from_socket):
    self.data.add(message)
    self.last_update = int(time())
    broadcast = dumps({'action':'add', 'name':message, 'update_time':self.last_update})
    map(lambda s: s.write_message(broadcast) if s is not from_socket else s, self.sockets)

  def delete_message(self, message, from_socket):
    if message in self.data: 
      self.data.remove(message);
      self.last_update = int(time())
      broadcast = dumps({'action':'delete', 'name':message, 'update_time': self.last_update})
      map(lambda s: s.write_message(broadcast) if s is not from_socket else s, self.sockets)
    
  def add_socket(self, socket):
    self.sockets.append(socket)
    broadcast = dumps({'action':'connect', 'list':list(self.data), 'update_time':self.last_update})
    socket.write_message(broadcast)

  def remove_socket(self, socket):
    self.sockets.remove(socket)

if __name__ == "__main__":
  application = Application()
  application.listen(8888)
  ioloop.IOLoop.instance().start()
