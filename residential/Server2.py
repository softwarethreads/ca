#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

from Execute import Execute


class S(BaseHTTPRequestHandler):

    def initialize(self):
        self.exec = Execute()

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            query = self.rfile.read(content_length)
            decoded_query = query.decode('utf-8')
            houses = self.exec.execute(decoded_query)
            if not houses:
                houses = "no houses returned"
            self._set_response()
            houses_encode = str(houses).encode('utf-8')
            self.wfile.write(houses_encode)
        except Exception as ex:
            self._set_response()
            self.wfile.write("error in getting houses 1".encode('utf-8'), str(ex))


def run(server_class=HTTPServer, handler_class=S, port=9000):
    logging.basicConfig(level=logging.ERROR)
    S.initialize(S)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("Initialization complete")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    run(port=9000)
