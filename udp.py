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
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.sendto(b'', (ns.host, ns.port))

  recvd = s.recv(BUF_SIZE)
  print('receiving...')
  total = {}
  pieces = []
  size = 1
  while len(total) < size:
    b = s.recv(BUF_SIZE)
    size = b['size']
    if not b or b == b'\x00':
      break
    if b['n'] not in pieces:
      pieces.append(b['n'])
      total[b['n']] = b['data']
    #recvd += b
  print("done")
  with open('udp_'+ns.filename, 'wb') as f:
    f.write(recvd)
  pr.disable()
  s = StringIO.StringIO()
  sortby = 'cumulative'
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()
  with open('udp_stats.txt', 'w') as stats: 
    stats.write(s.getvalue())
  s.close()

def tcp_server(ns):
  s = controlledSocket.ControllableSocket(0.1, 500000)
  s._socket.bind((ns.host, ns.port))
  
  b, a = s._socket.recvfrom(BUF_SIZE)
  
  print("sending...")
  while True:
    f = open(ns.filename, 'rb')
    n = 0
    totalBuf = f.read()
    size = int(BUF_SIZE/2)
    while True:
      buf = totalBuf[n*size:n*size+size]
      if not buf:
        break
      datagram = {'size':len(totalBuf),'n':++n,'data':pack(buf)}
      print ('sending {}'.format(datagram))
      #s._socket.sendto(json.dumps(datagram), a)
      s._socket.sendto(buf, a)
    f.close()
  s._socket.sendto(bytes('\0','UTF-8'), a)

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
