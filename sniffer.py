import socket
import os
import sys


#host to listen on
host = sys.argv[1]

if os.name == 'nt':
    print 'Detected a windows operating system'
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP
print 'setting up the sniffer'
sniffer = socket.socket(socket.AF_INET,socket.SOCK_RAW, socket_protocol)

sniffer.bind((host,0))

#We want the IP headers included in the capture
sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)

#If we're using windows, we need to send an ICTL to setup promiscious mode
if os.name == 'nt':
    print 'Setting promisc mode for windows'
    sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

print 'Starting sniffer'
print sniffer.recvfrom(64)

#If we're on windows turn off promisc mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_ECVALL,socket.RCVALL_OFF)

