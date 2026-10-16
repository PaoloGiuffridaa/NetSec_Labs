from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json
import secrets
from http.cookies import SimpleCookie


class RequestHandler(BaseHTTPRequestHandler):

    tokens_store = {}

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            return

        if self.path == "/me":
            cookies = SimpleCookie()
            cookies.load(self.headers.get("Cookie", ""))

            if "session" not in cookies:
                self.send_response(401)
                self.end_headers()
                return

            if cookies["session"].value in self.tokens_store:
                self.send_response(200)
                self.end_headers()
                username = self.tokens_store[cookies["session"].value]
                body = json.dumps({"user": username})
                self.wfile.write(body.encode("utf-8"))
                return

            else:
                self.send_response(401)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()
        return

    def do_POST(self):
        if self.path == "/login":
            # estraggo lughezza body
            length = int(self.headers.get("Content-Length", ""))

            # leggo body della post
            if length < 0:
                raise ValueError
            body = self.rfile.read(length)
            body = body.decode("utf-8")
            data = json.loads(body)

            if data["password"] != "netsec":
                self.send_response(401)
                self.end_headers()
                return

            # creo il token
            token = secrets.token_urlsafe(32)
            self.tokens_store[token] = data["user"]

            self.send_response(200)
            self.send_header("Set-Cookie", f"session={token}; Secure; HttpOnly")
            self.end_headers()


def start_server():
    server = HTTPServer(("0.0.0.0", 8443), RequestHandler)

    # posso usare TLS su un server HTTP come quello del task2, prima passo certificato e chiave
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    # associo al socket il contesto TLS
    server.socket = context.wrap_socket(server.socket, server_side=True)

    server.serve_forever()


if __name__ == "__main__":
    start_server()
