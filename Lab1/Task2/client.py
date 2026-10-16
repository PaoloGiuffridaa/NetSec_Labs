import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.8.0.84", 9001))

print("Connected to server!")

while True:
    command = input("Enter command: ")

    if command == "EXIT":
        break

    # Invia il comando al server
    s.sendall((command + "\n").encode("ascii"))

    # Riceve la risposta dal server
    response = s.makefile("rb").readline()

    print("Server:", response.decode("ascii").removesuffix("\n"))

s.close()