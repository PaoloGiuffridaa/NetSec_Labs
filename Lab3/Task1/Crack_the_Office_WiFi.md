# Task 1 — Crack the Office Wi-Fi

## Objective

Recover the WPA2-Personal passphrase of the `Acme-WiFi` network from `capture-7.pcap`, decrypt the captured wireless traffic, and find the `netsec{...}` flag sent to the intranet.

The challenge states that the passphrase consists of the fixed prefix `Acme` followed by **exactly six decimal digits**. This reduces the search space to `10^6 = 1,000,000` candidates.

## 1. Identify WPA2 handshakes with Wireshark

Open `capture-7.pcap` in Wireshark and apply the display filter:

```wireshark
eapol
```

This selects EAPOL-Key packets involved in WPA2's 4-way handshake. A complete exchange contains messages 1–4. We initially inspected packets **978–981**, including the MIC in message 2 (packet **979**):

```text
WPA Key MIC: 2309df2a75096a42aa66b76e36ae6101
BSSID: 74:83:c2:c1:88:7f
```

However, this handshake belonged to a **different SSID**, `Acme_WiFi`, not the requested `Acme-WiFi`. A similar-looking network name is not sufficient: the precise SSID matters because it is used as the salt in WPA2's PMK derivation.

## 2. Export handshake records for Hashcat

Install the required utility if necessary:

```bash
sudo apt install hcxtools
```

From the directory containing the correct capture file, run:

```bash
hcxpcapngtool -o acme.22000 capture-7.pcap
```

Observed output included:

```text
ESSID (total unique).....................: 2
EAPOL messages (total)...................: 18
EAPOL pairs (total)......................: 9
EAPOL pairs (best).......................: 4
EAPOL pairs written to 22000 hash file...: 4
```

Inspect the four records in the resulting `acme.22000` file. The SSID is encoded as hexadecimal:

| SSID hex | Decoded SSID | Action |
| --- | --- | --- |
| `41636d652d57694669` | `Acme-WiFi` | Keep (first three records) |
| `41636d655f57694669` | `Acme_WiFi` | Exclude (fourth record) |

For this **specific file and its verified record order**, retain the first three lines:

```bash
head -n 3 acme.22000 > acme-wifi.22000
wc -l acme-wifi.22000
```

Expected count: `3 acme-wifi.22000`.

> The `head -n 3` selection depends on this capture's observed record order; it is not a general-purpose way to filter by SSID.

## 3. Recover candidate passphrases with Hashcat

Install Hashcat if necessary:

```bash
sudo apt install hashcat
```

Use the WPA-PBKDF2-PMKID/EAPOL hash mode (`-m 22000`) and the mask attack mode (`-a 3`):

```bash
hashcat -m 22000 -a 3 acme-wifi.22000 'Acme?d?d?d?d?d?d'
```

Mask construction:

- `Acme`: fixed prefix specified by the challenge.
- `?d`: one decimal digit (`0`–`9`).
- Six `?d` tokens: all numbers from `000000` through `999999`.
- Total candidates: `10^6`.

The recorded run ended with:

```text
Status...........: Cracked
Recovered........: 3/3 (100.00%)
```

The recovered credentials (shown by Hashcat in its output) were:

| Client MAC | Recovered passphrase |
| --- | --- |
| `8c:85:90:52:4d:ce` | `Acme619650` |
| `8c:85:90:9c:e0:0c` | `Acme676196` |
| `f0:18:98:1c:88:92` | `Acme676196` |

The already recovered results can also be displayed using:

```bash
hashcat -m 22000 acme-wifi.22000 --show
```

**Interpretation:** Hashcat verified the passphrases against the corresponding recorded EAPOL data. Finding two values for records with the same SSID does not by itself mean that both were used by successfully associated clients; a captured handshake may not lead to a successful connection.

## 4. Select the relevant passphrase from encrypted traffic

In Wireshark, filter the protected wireless frames associated with the target access point:

```wireshark
wlan.fc.protected == 1 && wlan.bssid == 00:1a:1e:c1:76:50
```

We observed encrypted frames involving clients ending in `9c:e0:0c` and `1c:88:92`, which matched the two Hashcat records with passphrase **`Acme676196`**. The client ending in `52:4d:ce`, associated with `Acme619650`, was not present in the inspected encrypted traffic. We therefore tested `Acme676196` first.

This is an evidence-based choice about which traffic to decrypt, not proof that another recovered password is mathematically invalid.

## 5. Enable WPA2 decryption in Wireshark

1. Open **Edit → Preferences → Protocols → IEEE 802.11**.
2. Enable **Enable decryption**.
3. Open **Decryption keys → Edit** and add a key of type **`wpa-pwd`**.
4. Enter the exact value:

```text
Acme676196:Acme-WiFi
```

Both the passphrase and exact SSID are required to derive the WPA2 key material. Wireshark uses the captured handshakes to obtain the session keys needed for CCMP decryption.

## 6. Find the intranet message and flag

After decryption, filter HTTP requests:

```wireshark
http.request
```

Locate **frame 1201**:

```http
POST /api/notes HTTP/1.1
```

Right-click the packet and choose **Follow → TCP Stream** to inspect the request content. The captured message included:

```text
Wi-Fi audit, remember: netsec{81633e18c549f8cab9462eedef7edd0f}
```

## Result

```text
netsec{81633e18c549f8cab9462eedef7edd0f}
```
