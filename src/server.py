import socket
import sys
import json
import traceback
from wil6210fwctrl import *
import version

class wil6210Server():
    def __init__(self):
        print 'Server version: %s, build %s' % (version.version, 
                                                version.build_time)
        self.fw = Wil6210MailBox()
        self.fw.open()
        
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        if len(sys.argv) > 1:
            server_address = ('0.0.0.0', int(sys.argv[1]))
        else:
            server_address = ('0.0.0.0', 10000)
        print 'Starting up on %s port %s' % server_address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(server_address)
        
        # Listen for incoming connections
        self.sock.listen(1)
        self.buf_len = 10240
    
    def run(self):
        try:
            while True:
                connection = None
                
                # Wait for a connection
                print '\nWaiting for a connection'
                connection, client_address = self.sock.accept()
            
                print 'Connection from', client_address
                
                while True:
                    # Receive the data in small chunks and retransmit it
                    d = b''
                    disconnect = False
                    while True:
                        d_tmp = connection.recv(self.buf_len)
                        d += d_tmp
                        if not d_tmp:
                            disconnect = True
                            break
                        if d_tmp[-1] is '}':
                            break
                    
                    if disconnect:
                        break
                    
                    if d:
                        data = json.loads(d.decode('utf-8'))
                        
                        if data['cmd'] in SUPPORTED_WMI.keys():
                            resp = self.fw.caller(SUPPORTED_WMI[data['cmd']], 
                                             SUPPORTED_WMI[data['cmd']].setCmdArgs(data['args']))
                        else:
                            print 'Unsupported command!'
                            resp = ['Unsupported command!']
                        
                        message = json.dumps(resp).encode('utf-8')
                        connection.sendall(message)
        
        except Exception as e:
            print 'Exiting'
            traceback.print_exc()
            print e
        finally:
            print ''
            print 'Stopping running threads'
            for _, instance in SUPPORTED_WMI.iteritems():
                instance.stop()
            print 'Cleaning up firmware communication'
            self.fw.close()
            print 'Destroy sockets'
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            exit()

def parse_help():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        if len(sys.argv) > 2:
            if sys.argv[2] in SUPPORTED_WMI.keys():
                SUPPORTED_WMI[sys.argv[2]].print_help(sys.argv[2])
            else:
                print 'Module %s not found.' % sys.argv[2]
        else:
            for wmi_name in sorted(SUPPORTED_WMI.keys()):
                SUPPORTED_WMI[wmi_name].print_help(wmi_name)
        exit()

def main():
    parse_help()
    app = wil6210Server()
    app.run()
    
if __name__ == '__main__':
    main()
