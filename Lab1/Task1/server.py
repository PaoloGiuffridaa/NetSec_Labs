import socket
import threading

def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("10.8.0.84", 9001))

    store = {}

    server.listen()
    print("Server listening on port 9001")

    try:
        while True:
            client, address = server.accept()
            print("Client connected:", address)

            thread = threading.Thread(
                target=handle_client,
                args=(client, store),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nServer interrupted by user")

    finally:
        server.close()
        print("Server closed")

def handle_client(client, store):
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
            continue

        #COMMAND ECHO
        if command.startswith("ECHO "):
            print(f"Client {client} invia ECHO")
            response = command[5:] + "\n"
            client.sendall(response.encode('ascii'))
            continue

        #COMMAND SET
        if command.startswith("SET "):
            parts = command.split(" ", 2)

            #verifico mancanza value, key, SET
            if len(parts) != 3 or parts[0] != 'SET' or parts[2] == "" or parts[1] == "":
                response = "ERR\n"
                client.sendall(response.encode('ascii'))
                continue

            key = parts[1]
            value = parts[2]
            
            store[key] = value
            response = "OK\n"
            client.sendall(response.encode('ascii'))
            continue

        #COMMAND GET
        if command.startswith("GET "):
            parts = command.split(" ", 1)

            key = parts[1]
            if store.get(key) is not None:
                response = f"{store[key]}\n"
            else:
                response = "NOT_FOUND\n"
            client.sendall(response.encode('ascii'))
            continue

        #UNKNOWN COMMAND
        response = "ERR\n"
        client.sendall(response.encode('ascii'))
            


if __name__ == "__main__":
    start_server()
