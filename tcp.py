# the base for this file was fountain.py, so partial credit goes to the author of that file, specified at the top of fountain.py
import socket, controlledSocket
import argparse
from pprint import pprint as pp
from lt import *
from struct import *
import cProfile, pstats, io as StringIO
import json

BUF_SIZE=512

def tcp_client(ns):
  pr = cProfile.Profile()
  pr.enable()
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((ns.host, ns.port))

  recvd = s.recv(BUF_SIZE)
  print('receiving...')
  
  while True:
    b = s.recv(BUF_SIZE)
    if not b or b == b'\x00':
      break
    recvd += b
  s.close()
  print("done")
  with open('tcp_'+ns.filename, 'wb') as f:
    f.write(recvd)
  pr.disable()
  s = StringIO.StringIO()
  sortby = 'cumulative'
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()
  with open('tcp_stats.txt', 'w') as stats: 
    stats.write(s.getvalue())

def tcp_server(ns):
  s = controlledSocket.ControllableSocket(0.1, 500000, 'tcp')
  s._socket.bind((ns.host, ns.port))
  s._socket.listen(1)
  conn, addr = s._socket.accept()
  
  print("sending...")
  with open(ns.filename, 'rb') as f:
    while True:
      buf = f.read(BUF_SIZE)
      if not buf:
        break
      conn.send(buf)
  conn.send(bytes('\0','UTF-8'))
  s._socket.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', action='store_true', default=False, dest='server')
  parser.add_argument('-H', default='', dest='host')
  parser.add_argument('-P', default=50006, dest='port')
  parser.add_argument('-l', '--length', dest='length', type=int)
  parser.add_argument('filename', nargs='?')
  ns = parser.parse_args()

  if(ns.server):
    tcp_server(ns)
  else:
    tcp_client(ns)
