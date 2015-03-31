import sys
import threading
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from netaddr import IPNetwork,IPAddress
from scapy.all import *

network = sys.argv[1]

def icmp_scan(ip_address):
    ans = sr1(IP(dst=ip_address)/ICMP(), verbose=0, retry=2, timeout=1)
    if ans:
        print ans.sprintf('%IP.src% is alive')

def arp_scan(ip_address):
    ans = srp1(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip_address),verbose=False,retry=2, timeout=1)
    if ans:
        print ans.sprintf('%IP.src% is alive')

def udp_scan(ip_address):    
    ans = sr1(IP(dst=network)/UDP(dport=0),verbose=False,retry=2)
    if ans:
        print ans.sprintf('%IP.src% is alive')    
    
def perform_scan(ip_address):
    pass
    
    
print '[*] Performing basic ICMP scan'
for ip in IPNetwork(network):
    while threading.activeCount() > 128:
        time.sleep(5)
        
    threading.Thread(target=icmp_scan,args=(str(ip),)).start()
    
print '[*] Performing ARP scan'
for ip in IPNetwork(network):
    while threading.activeCount() > 128:
        time.sleep(5)    
        
    threading.Thread(target=arp_scan,args=(str(ip),)).start()
    
print '[*] Performing UDP scan'
for ip in IPNetwork(network):
    while threading.activeCount() > 128:
        time.sleep(5)    
    
    threading.Thread(target=udp_scan,args=(str(ip),)).start()
    
