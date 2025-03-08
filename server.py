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
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps("Invalid content type").encode('utf-8'))
                return
            
            try:
                
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                float_mode = query_params.get('float', ['false'])[0].lower() in ['true', '1', 'yes']
                
                
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps("Empty request body").encode())
                    return
                body = self.rfile.read(content_length).decode('utf-8')
                expression = json.loads(body)
                
                if not isinstance(expression, str):
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Expression must be a string").encode('utf-8'))
                    return
                
                # ÐŸÐ¾Ð´Ð³Ð¾Ñ‚Ð¾Ð²ÐºÐ° ÐºÐ¾Ð¼Ð°Ð½Ð´Ñ‹
                app_path = os.path.abspath(os.path.join('build', 'app.exe'))
                if not os.path.exists(app_path):
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Calculator not available").encode('utf-8'))
                    return
                
                mode = 'float' if float_mode else 'int'
                cmd = [app_path, mode, expression]
                
                # Ð’Ñ‹Ð¿Ð¾Ð»Ð½ÐµÐ½Ð¸Ðµ Ñ� Ñ‚Ð°Ð¹Ð¼Ð°ÑƒÑ‚Ð¾Ð¼
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                except subprocess.TimeoutExpired:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps("Calculation timeout").encode('utf-8'))
                    return

                # ÐžÐ±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ° Ñ€ÐµÐ·ÑƒÐ»ÑŒÑ‚Ð°Ñ‚Ð¾Ð²
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps(output).encode('utf-8'))
                    else:
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps("No result produced").encode('utf-8'))
                else:
                    error_msg = result.stderr.strip() or "Calculation failed"
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps(error_msg).encode('utf-8'))

            except json.JSONDecodeError:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps("Invalid JSON format").encode('utf-8'))
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
