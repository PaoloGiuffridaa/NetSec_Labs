
from scapy.all import rdpcap

packets = rdpcap("capture-7.pcap")

p190 = packets[189]
p385 = packets[384]

c1 = bytes(p190)[88:-8]
c2 = bytes(p385)[88:-8]

with open("expense-form.txt", "rb") as f:
    p1 = f.read()

print("P1:", len(p1))
print("C1:", len(c1))
print("C2:", len(c2))


p2 = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))

print(p2.decode("utf-8", errors="replace"))

