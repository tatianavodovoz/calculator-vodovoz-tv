from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import os
from urllib.parse import urlparse, parse_qs

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Hello, World!".encode('utf-8'))
        else:
            self.send_error(404, "Page not found")
    
    def do_POST(self):
        if self.path.startswith('/calc'):
            content_type = self.headers.get('Content-Type', '')
            if content_type != 'application/json':
                self.send_response(500)
                self.end_headers()
                return
            
            try:
                # Parse query parameters
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                float_mode = query_params.get('float', ['false'])[0].lower() in ['true', '1', 'yes']
                
                # Parse JSON body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                
                # Validate JSON structure
                try:
                    expression = json.loads(body)
                except json.JSONDecodeError as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Invalid JSON format").encode('utf-8'))
                    return
                
                if not isinstance(expression, str):
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Expression must be a string").encode('utf-8'))
                    return
                
                # Prepare command
                app_path = os.path.abspath(os.path.join('build', 'app.exe'))
                if not os.path.exists(app_path):
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Calculator not available").encode('utf-8'))
                    return
                
                mode = 'float' if float_mode else 'int'
                cmd = [app_path, mode, expression]
                
                # Execute calculator with timeout
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                except subprocess.TimeoutExpired as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Calculation timeout").encode('utf-8'))
                    return
                
                # Handle results
                if result.returncode != 0 or not result.stdout.strip():
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    error_msg = result.stderr.strip() or "Unknown calculation error"
                    self.wfile.write(json.dumps(error_msg).encode('utf-8'))
                    return
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result.stdout.strip()).encode('utf-8'))
            except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps(str(e)).encode('utf-8'))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

