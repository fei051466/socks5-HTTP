from multiprocessing import Process, Queue
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from SocketServer import StreamRequestHandler
import urllib


import time

q = Queue()


def socks_server(q):

    class MySocksHandler(StreamRequestHandler):

        def handle(self):
            #print 'got connect from %s ', self.client_address
            sock = self.connection
            while True:
                data = q.get()
                #print 'send data to local.py', map(ord, data)
                if data == 'close':
                    sock.close()
                    '''
                    while not q.empty():
                        q.get()
                    '''
                    break
                else:
                    sock.send(data)

    try:
        server = SocketServer.ThreadingTCPServer(('', 8087), MySocksHandler)
        print 'server-simulate serve at 8087'
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


def http_server(q):

    class MyRequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            datas = self.rfile.read(int(self.headers['content-length']))
            #datas = urllib.unquote(datas)
            datas = urllib.unquote_plus(datas)
            data = datas[5:]  # datas example: data=zo
            #print 'got data from server-side HTTP', map(ord, data)
            '''
            if data == 'newconnection':
                # q = Queue()
                p = Process(target=socks_server, args=(q,))
                p.start()
            else:
            '''
            q.put(data)
            self.send_response(200)

    try:
        server = HTTPServer(('', 8001), MyRequestHandler)
        print 'local-side HTTP serve at 8081'
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    p1 = Process(target=http_server, args=(q,))
    p1.start()
    #p1.join()

    p = Process(target=socks_server, args=(q,))
    p.start()
    #p.join()

    exit()
    #http_server()
