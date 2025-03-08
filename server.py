from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import json
import os
import time
import argparse
from urllib.parse import urlparse, parse_qs
import structlog
import socket

# ==
def configure_logging(json_logs: bool = False):

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=False),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

# ================================================
# ÐžÐ±Ñ€Ð°Ð±Ð¾Ñ‚Ñ‡Ð¸Ðº HTTP Ð·Ð°Ð¿Ñ€Ð¾Ñ�Ð¾Ð²
# ================================================
class CalculatorHandler(BaseHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        """ÐžÑ‚ÐºÐ»ÑŽÑ‡Ð°ÐµÐ¼ Ñ�Ñ‚Ð°Ð½Ð´Ð°Ñ€Ñ‚Ð½Ð¾Ðµ Ð»Ð¾Ð³Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð¸Ðµ BaseHTTPRequestHandler"""
        pass

    def _init_logger(self):
        """Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ� Ð»Ð¾Ð³Ð³ÐµÑ€Ð° Ñ� ÐºÐ¾Ð½Ñ‚ÐµÐºÑ�Ñ‚Ð¾Ð¼"""
        return structlog.get_logger().bind(
            method=self.command,
            path=self.path,
            client_ip=self.client_address[0],
            request_id=os.urandom(4).hex()
        )

    def _send_response(self, status: int, content: str = None):
        """Ð£Ð½Ð¸Ð²ÐµÑ€Ñ�Ð°Ð»ÑŒÐ½Ñ‹Ð¹ Ð¼ÐµÑ‚Ð¾Ð´ Ð¾Ñ‚Ð¿Ñ€Ð°Ð²ÐºÐ¸ Ð¾Ñ‚Ð²ÐµÑ‚Ð¾Ð²"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        if content:
            self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        """ÐžÐ±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ° GET Ð·Ð°Ð¿Ñ€Ð¾Ñ�Ð¾Ð²"""
        logger = self._init_logger()
        start_time = time.monotonic()
        
        try:
            if self.path == '/':
                logger.info("Handling root request")
                self._send_response(200, "Hello, World!")
                logger.info(
                    "Request completed",
                    duration=time.monotonic() - start_time,
                    status=200
                )
            else:
                logger.warning("Path not found")
                self._send_response(404, "Page not found")
                
        except Exception as e:
            logger.error(
                "Request failed",
                error=str(e),
                exc_info=True
            )
            self._send_response(500, "Internal Server Error")

    def do_POST(self):
        
        logger = self._init_logger()
        start_time = time.monotonic()
        
        try:
            # ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð¿ÑƒÑ‚Ð¸
            if not self.path.startswith('/calc'):
                logger.warning("Invalid endpoint")
                self._send_response(404, "Not Found")
                return

            logger.info("Starting calculation request")
            
            # ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Content-Type
            if self.headers.get('Content-Type') != 'application/json':
                logger.error("Invalid content type", 
                           content_type=self.headers.get('Content-Type'))
                self._send_response(400, "Invalid content type")
                return

            # Ð§Ñ‚ÐµÐ½Ð¸Ðµ Ñ‚ÐµÐ»Ð° Ð·Ð°Ð¿Ñ€Ð¾Ñ�Ð°
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)
            
            # ÐŸÐ°Ñ€Ñ�Ð¸Ð½Ð³ JSON
            try:
                expression = json.loads(raw_body)
                if not isinstance(expression, str):
                    raise ValueError("Expression must be a string")
            except Exception as e:
                logger.error("Invalid request body", error=str(e))
                self._send_response(400, "Invalid request format")
                return

            # ÐŸÐ°Ñ€Ñ�Ð¸Ð½Ð³ Ð¿Ð°Ñ€Ð°Ð¼ÐµÑ‚Ñ€Ð¾Ð²
            query_params = parse_qs(urlparse(self.path).query)
            float_mode = query_params.get('float', ['false'])[0].lower() in ['true', '1', 'yes']
            mode = 'float' if float_mode else 'int'

            # ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð´Ð¾Ñ�Ñ‚ÑƒÐ¿Ð½Ð¾Ñ�Ñ‚Ð¸ ÐºÐ°Ð»ÑŒÐºÑƒÐ»Ñ�Ñ‚Ð¾Ñ€Ð°
            app_path = os.path.abspath(os.path.join('build', 'app.exe'))
            if not os.path.exists(app_path):
                logger.critical("Calculator binary missing")
                self._send_response(500, "Service unavailable")
                return

            # Ð’Ñ‹Ð¿Ð¾Ð»Ð½ÐµÐ½Ð¸Ðµ Ð²Ñ‹Ñ‡Ð¸Ñ�Ð»ÐµÐ½Ð¸Ð¹
            try:
                result = subprocess.run(
                    [app_path, mode, expression],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            except subprocess.TimeoutExpired:
                logger.error("Calculation timeout")
                self._send_response(504, "Gateway Timeout")
                return

            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Calculation failed"
                logger.error(
                    "Calculation error",
                    exit_code=result.returncode,
                    error=error_msg
                )
                self._send_response(500, error_msg)
                return

            if not result.stdout.strip():
                logger.error("Empty result")
                self._send_response(500, "No result produced")
                return

           
            logger.info(
                "Calculation successful",
                duration=time.monotonic() - start_time,
                expression=expression,
                result=result.stdout.strip()
            )
            self._send_response(200, json.dumps(result.stdout.strip()))

        except Exception as e:
            logger.error(
                "Unexpected error",
                error=str(e),
                exc_info=True
            )
            self._send_response(500, "Internal Server Error")


def run_server(host: str = '0.0.0.0', port: int = 8000, json_logs: bool = False):
    
    configure_logging(json_logs)
    server_address = (host, port)
    httpd = HTTPServer(server_address, CalculatorHandler)
    
    logger = structlog.get_logger()
    try:
        logger.info(
            "Starting server",
            host=host,
            port=port,
            log_format="JSON" if json_logs else "CONSOLE"
        )
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.critical("Server crashed", error=str(e))
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculator HTTP Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--json-logs', action='store_true', help='Enable JSON logging')
    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        json_logs=args.json_logs
    )
