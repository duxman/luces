from socket import socket
import struct
import threading
import Queue

class MulticastServer(object):
    MCAST_GRP = "224.0.0.1"
    MCAST_PORT = 10000
    MulticastSockect = None

    def __init__(self,adress,port):
        self.MCAST_GRP = adress
        self.MCAST_PORT= port
        self.MulticastSockect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.MulticastSockect.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

    def send(self,message):
        self.MulticastSockect.sendto(message,(self.MCAST_GRP, self.MCAST_PORT))

    def receive(self):
        print self.MulticastSockect.recv(1024)


class MulticastClient(object):
    MCAST_GRP = "224.0.0.1"
    MCAST_PORT = 10000
    MulticastSockect = None
    ReceiveThreat = None
    ReceiveData = []

    def __init__(self, adress, port):
        self.MCAST_GRP = adress
        self.MCAST_PORT = port
        self.ReceiveData = Queue()
        self.InitializeSockect()


    def CreateReceiveThreat(self):
        self.ReceiveThreat = threading.Thread(target=self.receive(self.ReceiveData), name="MulticastReceiveThreat")
        self.ReceiveThreat.daemon = True
        self.ReceiveThreat.start()


    def InitializeSockect(self):
        self.MulticastSockect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.MulticastSockect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.MulticastSockect.bind((self.MCAST_GRP, self.MCAST_PORT))
        mreq = struct.pack("4s", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
        self.MulticastSockect.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.CreateReceiveThreat()

    def send(self, message):
        self.MulticastSockect.sendto(message, (self.MCAST_GRP, self.MCAST_PORT))

    def receive(self,receivedata):
        while(True):
            data = self.MulticastSockect.recv(1024)
            receivedata.put( data )
