
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread


class RequestHandler(BaseHTTPRequestHandler):

    tokens_store = {}

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            return

        if self.path == "/claim":
            body = RequestHandler.tokens_store.get("last", b"")

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/claim":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)

            RequestHandler.tokens_store["last"] = body

            self.send_response(200)
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()


def start_server():
    server_onion = HTTPServer(("127.0.0.1", 5000), RequestHandler)
    server_vpn = HTTPServer(("10.8.0.5", 8090), RequestHandler)

    thread = Thread(target=server_onion.serve_forever)
    thread.start()

    server_vpn.serve_forever()


if __name__ == "__main__":
    start_server()
