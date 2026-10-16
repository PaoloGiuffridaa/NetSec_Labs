from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
from http.cookies import SimpleCookie
import hashlib

class RequestHandler(BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"
    tokens_store = {}

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Alt-Svc", 'h3=":4433"')
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path == "/proto":
            self.send_response(200)
            self.send_header("Content-Type", 'text/plain')
            self.send_header("Content-Length", "8")
            self.end_headers()
            body = "HTTP/1.1"
            self.wfile.write(body.encode("utf-8"))
            return
    def do_POST(self):
        if self.path == "/hash":
            # estraggo lughezza body
            length = int(self.headers.get("Content-Length", ""))
            
            # leggo body della post
            if length < 0:
                raise ValueError
            body = self.rfile.read(length)
            digest = hashlib.sha256(body).hexdigest()
            self.send_response(200)
            self.send_header("Content-Type", 'text/plain')
            self.send_header("Content-Length", "64")
            self.end_headers()
            self.wfile.write(digest.encode(ascii))
            return

            


        

def start_server():
    server = HTTPServer(("0.0.0.0", 4433), RequestHandler)

    # posso usare TLS su un server HTTP come quello del task2, prima passo certificato e chiave
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    # associo al socket il contesto TLS
    server.socket = context.wrap_socket(server.socket, server_side=True)

    server.serve_forever()


if __name__ == "__main__":
    start_server()
