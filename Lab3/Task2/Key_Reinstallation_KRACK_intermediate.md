# Task 2 — Key Reinstallation (KRACK)

**Files:** `capture-7.pcap` (Task 2), `expense-form.txt`  
**Flag:** `netsec{70eca2ca80d5ef3d005ee0412f0bb273}`

## 1. Identify the key reinstallation

We analyzed the new capture in Wireshark with the `eapol` filter. Two **Message 3 of 4** frames targeted the same client (`f0:18:98:b3:ea:c5`):

| Frame | Replay Counter | ANonce |
| ---: | ---: | --- |
| 53 | 2 | Same value |
| 294 | 3 | Same value |

The different Replay Counters do not rule out a reinstallation; the repeated ANonce is consistent with the same key-establishment context. To check the practical effect, we filtered encrypted frames transmitted by that client:

```wireshark
wlan.fc.protected == 1 && wlan.ta == f0:18:98:b3:ea:c5
```

We added `wlan.ccmp.extiv` as a Wireshark column. After frame **294**, the client reused earlier CCMP Packet Numbers (PNs), including PN 1 and PN 12. This provided evidence of PN reset; a repeated PN alone would not necessarily guarantee usable keystream reuse.

## 2. Select the ciphertext pair

We chose two frames with the same transmitter and **PN = 12**:

```wireshark
frame.number == 190 || frame.number == 385
```

| Frame | Position | Size | PN |
| ---: | --- | ---: | ---: |
| 190 | Before key reinstallation | 1463 bytes | 12 |
| 385 | After key reinstallation | 279 bytes | 12 |

The supplied `expense-form.txt` is **1367 bytes** (`wc -c expense-form.txt`). Its size matched the expected TCP payload length of frame 190, allowing us to use the file as known plaintext. The successful XOR recovery later confirmed the pair and alignment were useful.

For these frames, the payload starts at offset **88**: 8 Radiotap + 24 IEEE 802.11 + 8 CCMP + 8 LLC/SNAP + 20 IPv4 + 20 TCP bytes. The final **8 bytes** are the CCMP MIC and were excluded. These offsets are specific to the observed frames.

## 3. Recover the second payload with Python

We wrote `krack.py` using Scapy to read the capture, extract the two encrypted TCP payloads, and apply the known-plaintext XOR:

```python
from scapy.all import rdpcap

packets = rdpcap("capture-7.pcap")

# Wireshark numbers frames from 1; Python indexes from 0.
c1 = bytes(packets[189])[88:-8]  # frame 190
c2 = bytes(packets[384])[88:-8]  # frame 385

with open("expense-form.txt", "rb") as f:
    p1 = f.read()

p2 = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
print(p2.decode("utf-8", errors="replace"))
```

The calculation **`P2 = C1 XOR C2 XOR P1`** works because these two frames reused the same CCMP keystream. The script recovered **183 bytes** of the second TCP payload and revealed the flag, without needing the Wi-Fi passphrase.

**Result:** `netsec{70eca2ca80d5ef3d005ee0412f0bb273}`
