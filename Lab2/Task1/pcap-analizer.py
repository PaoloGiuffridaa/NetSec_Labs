import re
import subprocess

PCAP = "/tmp/netsec-capture-7.pcap"

syn_filter = (
    "ip.src == 198.51.100.7 && "
    "tcp.flags.syn == 1 && "
    "tcp.flags.ack == 0 && "
    "ip.ttl == 63 && "
    "tcp.window_size_value == 65535 && "
    "tcp.options.mss_val == 1400 && "
    "tcp.options.wscale.shift == 9 && "
    "tcp.hdr_len == 40"
)

result = subprocess.run(
    [
        "tshark",
        "-r", PCAP,
        "-Y", syn_filter,
        "-T", "fields",
        "-e", "tcp.stream",
    ],
    capture_output=True,
    text=True,
    check=True,
)

print("Return code:", result.returncode)
print("STDOUT:", repr(result.stdout))
print("STDERR:", result.stderr)

streams = sorted(set(result.stdout.split()), key=int)

print(f"Connessioni candidate: {len(streams)}")
print("TCP streams:", ", ".join(streams))

fragments = {}
for stream in streams:
    filter = f"tcp.stream == {stream} && http.request"

    result = subprocess.run(
        [
            "tshark",
            "-r", PCAP,
            "-Y", filter,
            "-T", "fields",
            "-e", "http.request.line",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    print(f"Stream {stream}: {result.stdout.strip()}")

    matches = re.findall(
        r"X-Trace:\s*([1-8])-([0-9a-fA-F]{6})",
        result.stdout)

    for position, fragment in matches:
        fragments[int(position)] = fragment

if set(fragments.keys()) != set(range(1, 9)):
    raise ValueError("Mancano alcuni frammenti della flag")

flag = ""
for frag in sorted(fragments.keys()):
    flag += fragments[frag]

flag = f"netsec{{{flag}}}"
print(flag)

#netsec{7f2e83ac2cc5da1d16cc576dae4f662882244adba8d2fc38}