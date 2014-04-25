#taken from http://stackoverflow.com/questions/1833563/simple-way-to-simulate-a-slow-network-in-python
import time, socket

class ControllableSocket:
    def __init__(self, latency, bandwidth, type='udp'):
        self._latency = latency
        self._bandwidth = bandwidth
        self._bytesSent = 0
        self._timeCreated = time.time()
        if type is 'udp':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif type is 'tcp':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            print('invalid socket type {}'.format(type))
            exit(1)

    def send(self, conn, bytes):
        now = time.time()
        connectionDuration = now - self._timeCreated
        self._bytesSent += len(bytes)
        # How long should it have taken to send how many bytes we've sent with our
        # given bandwidth limitation?
        requiredDuration = self._bytesSent / self._bandwidth
        time.sleep(max(requiredDuration - connectionDuration, self._latency))
        return conn.send(bytes)

    def sendto(self, packed, a):
        now = time.time()
        connectionDuration = now - self._timeCreated
        self._bytesSent += len(packed)
        # How long should it have taken to send how many bytes we've sent with our
        # given bandwidth limitation?
        requiredDuration = self._bytesSent / self._bandwidth
        time.sleep(max(requiredDuration - connectionDuration, self._latency))
        return self._socket.sendto(packed, a)
