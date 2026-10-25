from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import HeadersReceived, DataReceived
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.asyncio import serve
import hashlib
import asyncio 


configuration = QuicConfiguration(is_client=False, alpn_protocols=["h3"])  # stiamo configurando un server, usa http3 ALPN (Application-Layer Protocol Negotiation)

configuration.load_cert_chain(certfile="server.crt", keyfile="server.key")

async def start_server():
    server = await serve(
        "0.0.0.0",
        4433,
        configuration=configuration,
        create_protocol=HTTP3Protocol   #usa questa classe quando arrvia una connessione QUIC
    )

    await asyncio.Event().wait()

class HTTP3Protocol(QuicConnectionProtocol):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http = H3Connection(self._quic)
        self.bodies = {}

    
    def quic_event_received(self, event):
        for http_event in self.http.handle_event(event):

            if isinstance(http_event, HeadersReceived):
                headers = dict(http_event.headers)
                method = headers[b":method"]
                path = headers[b":path"]
                stream_id = http_event.stream_id

                if method == b"GET" and path == b"/":
                    self.http.send_headers(
                        stream_id=stream_id,
                        headers=[(b":status", b"200")],
                        end_stream=True
                    )
                    self.transmit()

                elif method == b"GET" and path == b"/proto":
                    self.http.send_headers(
                        stream_id=stream_id,
                        headers=[
                            (b":status", b"200"),
                            (b"content-type", b"text/plain")
                        ],
                        end_stream=False
                    )
                    self.http.send_data(
                        stream_id=stream_id,
                        data=b"HTTP/3",
                        end_stream=True
                    )
                    self.transmit()

                elif method == b"POST" and path == b"/hash":
                    # Creo un buffer per questa richiesta
                    self.bodies[stream_id] = bytearray()

                    # Gestisco anche le POST con body vuoto
                    if http_event.stream_ended:
                        self.send_hash(stream_id)

            elif isinstance(http_event, DataReceived):
                stream_id = http_event.stream_id

                if stream_id in self.bodies:
                    # Aggiungo i nuovi dati a quelli precedenti
                    self.bodies[stream_id].extend(http_event.data)

                    # Calcolo l'hash soltanto quando il body è completo
                    if http_event.stream_ended:
                        self.send_hash(stream_id)


    def send_hash(self, stream_id):
        # Recupero il body e libero la memoria
        body = self.bodies.pop(stream_id)

        # Calcolo SHA-256 in formato esadecimale
        digest = hashlib.sha256(body).hexdigest()

        # Invio la risposta HTTP/3
        self.http.send_headers(
            stream_id=stream_id,
            headers=[
                (b":status", b"200"),
                (b"content-type", b"text/plain")
            ],
            end_stream=False
        )

        self.http.send_data(
            stream_id=stream_id,
            data=digest.encode("ascii"),
            end_stream=True
        )
        self.transmit()


if __name__ == "__main__":
    asyncio.run(start_server())

