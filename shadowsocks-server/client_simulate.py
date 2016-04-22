from multiprocessing import Process, Queue
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from SocketServer import StreamRequestHandler
import socket
import select
import urllib
import requests
import time

# q = Queue()


def sent_all_in_http_post_format(data):

    payload = {'data': data}
    url = 'http://127.0.0.1:8001/'
    # print 'send data to client-side server', map(ord, data)
    res = requests.post(url, data = payload)


def socks_client(q):

    HOST = '127.0.0.1'
    PORT = 8086
    addr = (HOST, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(addr)
    try:
        while True:
            r, w, e = select.select([client], [client], [])
            if client in w:
                try:
                    data = q.get(False)
                    # print 'sent data to server.py', map(ord, data)
                    if data == 'close':
                        break
                    else:
                        client.send(data)
                except:
                    pass
            if client in r:
                data = client.recv(4096)
                if data:
                    # print 'got data from server.py', map(ord, data)
                    sent_all_in_http_post_format(data)
                else:
                    break
    finally:
        client.close()
        print 'socket closed'
        sent_all_in_http_post_format('close')


def http_server():

    q = Queue()

    class MyRequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            datas = self.rfile.read(int(self.headers['content-length']))
            # print datas
            #datas = urllib.unquote(datas)
            datas = urllib.unquote_plus(datas)   # unquote('%7e/abc+def') -> '~/abc def'
            data = datas[5:]  # datas example: data=payload
            if data == 'newconnection':
                print 'got newconnection'
                p = Process(target=socks_client, args=(q,))
                p.start()
                # sent_all_in_http_post_format('newconnection')
            else:
                q.put(data)
            # print 'got data from local.py', data
            self.send_response(200)

    try:
        server = HTTPServer(('', 8000), MyRequestHandler)
        print 'server-side HTTP serve at 8000'
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':

    #p1 = Process(target=http_server, args=(q,))
    #p1.start()
    # p1.join()

    #p = Process(target=socks_client, args=(q,))
    #p.start()
    # p.join()

    #exit()

    http_server()