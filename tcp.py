# the base for this file was fountain.py, so partial credit goes to the author of that file, specified at the top of fountain.py
import socket, argparse
from pprint import pprint as pp
from lt import *
from struct import *
import cProfile, pstats, io as StringIO, time

BUF_SIZE=512

def tcp_client(ns):
  pr = cProfile.Profile()
  pr.enable()
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((ns.host, ns.port))

  print ('startTime {}'.format(time.time()))
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
  print ('endTime {}'.format(time.time()))

def tcp_server(ns):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((ns.host, ns.port))
  s.listen(1)
  conn, addr = s.accept()
  
  print("sending...")
  with open(ns.filename, 'rb') as f:
    print ('startTime {}'.format(time.time()))
    while True:
      buf = f.read(BUF_SIZE)
      if not buf:
        break
      conn.send(buf)
  conn.send(bytes('\0','UTF-8'))
  s.close()
  print ('endtime {}'.format(time.time()))

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
