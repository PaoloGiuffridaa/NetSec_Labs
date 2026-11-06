import re
import subprocess

PCAP = "/tmp/netsec-pcap7-task2.pcap"

filter = "tls.handshake.type == 1"

result = subprocess.run(
    [
        "tshark",
        "-r", PCAP,
        "-Y", filter,
        "-T", "fields",
        "-e", "frame.number",
        "-e", "tls.handshake.extensions_server_name",
        "-e", "tls.handshake.ja4",
    ],
    capture_output=True,
    text=True,
    check=True,
)
for line in result.stdout.splitlines():
    if "syncbridge.example" in line:
        print(line)
        ja4_sign = line.split()[2]
        print(f"JA4 signature: {ja4_sign}")


filter = f'tls.handshake.ja4 == "{ja4_sign}"'

result = subprocess.run(
    [
        "tshark",
        "-r", PCAP,
        "-Y", filter,
        "-T", "fields",
        "-e", "frame.number",
        "-e", "tls.handshake.extensions_server_name",
    ],
    capture_output=True,
    text=True,
    check=True,
)

flag = "netsec{"
for line in result.stdout.splitlines():
    match = re.search(r"([0-9a-f]{6}\.)", line)
    flag_part = match.group(1).split('.')[0] if match else None
    if flag_part:
        flag += flag_part
flag += "}"
print(flag)
