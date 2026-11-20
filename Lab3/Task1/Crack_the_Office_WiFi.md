# Task 1 — Crack the Office Wi-Fi

**Files:** `capture-7.pcap`  
**Flag:** `netsec{81633e18c549f8cab9462eedef7edd0f}`

## 1. Handshake selection

We inspected the capture in Wireshark using `eapol` to locate the WPA2 4-way handshakes. The capture included two similar SSIDs, `Acme-WiFi` and `Acme_WiFi`; only the former was the target. In particular, the handshake at frames 978–981 belonged to the *other* SSID and was excluded.

We converted the capture to Hashcat's 22000 format:

```bash
hcxpcapngtool -o acme.22000 capture-7.pcap
```

The tool wrote four EAPOL records. We checked the encoded SSIDs in `acme.22000`:

| SSID bytes (hex) | Decoded SSID | Records |
| --- | --- | ---: |
| `41636d652d57694669` | `Acme-WiFi` | 3 |
| `41636d655f57694669` | `Acme_WiFi` | 1 |

The three target records happened to be the first three lines **in this output**, so we isolated them with:

```bash
head -n 3 acme.22000 > acme-wifi.22000
wc -l acme-wifi.22000  # 3
```

## 2. Offline password recovery

The task specified the format `Acme` + six decimal digits. We therefore used the mask `Acme?d?d?d?d?d?d`: `Acme` is fixed, and each `?d` stands for one digit (`0`–`9`), giving **1,000,000 possible candidates**.

```bash
hashcat -m 22000 -a 3 acme-wifi.22000 'Acme?d?d?d?d?d?d'
```

Here `-m 22000` selects WPA-PBKDF2-PMKID/EAPOL and `-a 3` selects a mask attack. Hashcat reported **`Status: Cracked`** and **`Recovered: 3/3`** (the attack stopped once all three records had been recovered):

| Client MAC | Recovered passphrase |
| --- | --- |
| `8c:85:90:52:4d:ce` | `Acme619650` |
| `8c:85:90:9c:e0:0c` | `Acme676196` |
| `f0:18:98:1c:88:92` | `Acme676196` |

## 3. Decryption and flag extraction

To choose which passphrase to try, we inspected protected frames associated with the target access point:

```wireshark
wlan.fc.protected == 1 && wlan.bssid == 00:1a:1e:c1:76:50
```

The visible traffic involved the two clients associated with **`Acme676196`**. We enabled **Preferences → Protocols → IEEE 802.11 → Enable decryption**, then added a key of type `wpa-pwd` with the value:

```text
Acme676196:Acme-WiFi
```

After decryption, the Wireshark filter `http.request` exposed an HTTP **`POST /api/notes`** request in **frame 1201**. Using **Follow TCP Stream**, we read the message containing the flag.

**Result:** `netsec{81633e18c549f8cab9462eedef7edd0f}`
