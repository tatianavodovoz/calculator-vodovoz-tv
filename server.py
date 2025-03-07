from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Hello, World!".encode('utf-8'))
        else:
            self.send_error(404, "Page not found")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
