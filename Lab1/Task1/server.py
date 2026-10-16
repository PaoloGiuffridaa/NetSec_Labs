import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #AF_INET usa iPv4, SOCK_STREAM usa TCP
    server.bind(("127.0.0.1", 9001))

    server.listen()

    print("Server listening on port 9001")

    client, address = server.accept()   #aspetta che un client si connetta
    print("Client connected:", address)
    handle_client(client)

def handle_client(client):
    stream = client.makefile("rb")

    while(True):

        line = stream.readline()

        #CHIUSURA CONNESSIONE
        if not line:
            break

        command = line.decode('ascii')
        command = command.removesuffix("\n")

        #COMANDO PING-PONG
        if command == "PING":
            print(f"Client {client} invia PING")
            response = "PONG\n"
            client.sendall(response.encode('ascii'))


    if __name__ == "__main__":
        start_server()
