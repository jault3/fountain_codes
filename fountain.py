# Copyright (c) Alex Chamberlain 2012 https://github.com/alexchamberlain/socket
import socket, controlledSocket
import argparse
from pprint import pprint as pp
from lt import *
from struct import *
import cProfile, pstats, io as StringIO

BUF_SIZE=512

def fountain_client(ns):
  pr = cProfile.Profile()
  pr.enable()
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  bucket = lt_decode(ns.length, 504)
  
  s.sendto(b'', (ns.host, ns.port))
  i = 0
  while bucket.unknown_blocks > 0:
    i += 1
    b, a = s.recvfrom(BUF_SIZE)
    #print("Client received {} bytes from {}:{}".format(len(b), a[0], a[1]))
    degree, seed, data = unpack('!II504s', b)
    bucket.catch({'degree': degree, 'seed': seed, 'data': data})
    print("Caught {:d} droplets. There are {:d} unknown blocks.".format(i, bucket.unknown_blocks), end='\r')
  print("\n")

  with open(ns.filename, 'wb') as f:
    o = memoryview(bucket.original)[:ns.length]
    f.write(o)
  pr.disable()
  s = StringIO.StringIO()
  sortby = 'cumulative'
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()
  with open('fountain_stats.txt', 'w') as stats: 
    stats.write(s.getvalue())

def fountain_server(ns):
  s = controlledSocket.ControllableSocket(0.1, 500000)
  s._socket.bind((ns.host, ns.port))

  with open(ns.filename, 'rb') as f:
    buf = f.read()

  fountain = lt_encode(buf, 504)
  
  while True:
    b, a = s._socket.recvfrom(BUF_SIZE)
    print("Server received {} bytes from {}:{}".format(len(b), a[0], a[1]))
    print("Starting fountain...")

    while 1:
      d = next(fountain)
      s._socket.sendto(pack('!II504s', d['degree'], d['seed'], d['data']), a)
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', action='store_true', default=False, dest='server')
  parser.add_argument('-H', default='', dest='host')
  parser.add_argument('-P', default=50005, dest='port')
  parser.add_argument('-l', '--length', dest='length', type=int)
  parser.add_argument('filename', nargs='?')
  ns = parser.parse_args()

  if(ns.server):
    fountain_server(ns)
  else:
    fountain_client(ns)
