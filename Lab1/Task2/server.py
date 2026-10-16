from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json


class RequestHandler(BaseHTTPRequestHandler):

    notes = {}
    next_id = 1

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/":
            self.send_response(200)
            self.end_headers()

        elif parsed_url.path == "/echo":
            params = parse_qs(parsed_url.query, keep_blank_values=True)

            if "msg" not in params:
                self.send_response(400)
                self.end_headers()
                return

            msg = params["msg"][0]
            data = {"msg": msg}
            body = json.dumps(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        elif parsed_url.path.startswith("/notes/"):
            parts = parsed_url.path.split("/")

            if len(parts) != 3 or not parts[2].isascii() or not parts[2].isdigit():
                self.send_response(404)
                self.end_headers()
                return

            note_id = int(parts[2])

            if note_id not in self.notes:
                self.send_response(404)
                self.end_headers()
                return

            msg = self.notes[note_id]
            data = {"id": note_id, "text": msg}
            body = json.dumps(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        elif parsed_url.path == "/notes":
            self.send_response(405)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path.startswith("/notes/"):
            parts = parsed_url.path.split("/")

            if len(parts) != 3 or not parts[2].isascii() or not parts[2].isdigit():
                self.send_response(404)
                self.end_headers()
                return

            note_id = int(parts[2])

            if note_id not in self.notes:
                self.send_response(404)
                self.end_headers()
                return

            del self.notes[note_id]

            self.send_response(204)
            self.end_headers()

        elif parsed_url.path == "/notes":
            self.send_response(405)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/notes":

            # Controlliamo il Content-Type
            content_type = self.headers.get("Content-Type", "")
            content_type = content_type.split(";")[0].strip().lower()

            if content_type != "application/json":
                self.send_response(415)
                self.end_headers()
                return

            # Leggiamo e convertiamo il body
            try:
                length = int(self.headers.get("Content-Length", ""))

                if length < 0:
                    raise ValueError

                body = self.rfile.read(length)
                body = body.decode("utf-8")
                data = json.loads(body)

            except (ValueError, UnicodeDecodeError):
                self.send_response(400)
                self.end_headers()
                return

            # Controlliamo che text esista e sia una stringa
            if not isinstance(data, dict) or not isinstance(data.get("text"), str):
                self.send_response(400)
                self.end_headers()
                return

            # Salviamo la nota
            note_id = RequestHandler.next_id
            self.notes[note_id] = data["text"]
            RequestHandler.next_id += 1

            # Prepariamo la risposta
            data = {"id": note_id}
            body = json.dumps(data)

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        elif parsed_url.path.startswith("/notes/"):
            self.send_response(405)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    # Metodi non supportati
    def do_PUT(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/notes" or parsed_url.path.startswith("/notes/"):
            self.send_response(405)
        else:
            self.send_response(404)

        self.end_headers()

    def do_PATCH(self):
        self.do_PUT()

    def do_OPTIONS(self):
        self.do_PUT()

    def do_HEAD(self):
        self.do_PUT()


def start_server():
    server = HTTPServer(("10.8.0.66", 8080), RequestHandler)
    print("HTTP Server listening on port 8080")
    server.serve_forever()


if __name__ == "__main__":
    start_server()