from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/whoami":

            # ricavo il certificato usato del client durante lo handshake
            cert = self.connection.getpeercert()
            subject = cert["subject"]
            name = subject[0][0][1]

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(name.encode("utf-8"))
            return


def start_server():
    server = HTTPServer(("0.0.0.0", 8444), RequestHandler)

    # posso usare TLS su un server HTTP come quello del task2, prima passo certificato e chiave
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    context.load_verify_locations(cafile="ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED
    # associo al socket il contesto TLS
    server.socket = context.wrap_socket(server.socket, server_side=True)

    server.serve_forever()


if __name__ == "__main__":
    start_server()
