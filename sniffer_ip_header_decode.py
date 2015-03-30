import socket
import os
import struct
import sys

from ctypes import *


#host to listen on
host = sys.argv[1]

class IP(Structure):
    _fields_ = [
        ("ihl",           c_ubyte, 4),
    ("version",       c_ubyte, 4),
    ("tos",           c_ubyte),
    ("len",           c_ushort),
    ("id",            c_ushort),
    ("offset",        c_ushort),
    ("ttl",           c_ubyte),
    ("protocol_num",  c_ubyte),
    ("sum",           c_ushort),
    ("src",           c_ulong),
    ("dst",           c_ulong)
    ]
    
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):
        
        #map protocol constants to their names
        self.protocol_map = {1: 'ICMP', 6:'TCP',17:'UDP'}
        
        #human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst_address = socket.inet.ntoa(struct.pack("<L",self.dst))
        
        #human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)
            
        
#This should look familiar from the previous example


if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP
    
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
#sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW)

sniffer.bind((host,0))

sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)

if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RVCALL,socket.RCVALL_ON)
    
try:
    while True:
        #read in a packet
        raw_buffer = sniffer.recvfrom(65535)[0]
        
        #create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[0:20])
        
        #print out the protocol that was detected and the hosts
        print 'Protocol: %s %s -> %s '% (ip_header.protocol,ip_header.src_address,ip_header.dst_address)
        
except KeyboardInterrupt:
    #if using windows turn off promisc mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)
                
