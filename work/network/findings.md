# Thor network investigation — 2026-09-26

CTGP endpoint: 88.19.187.219:7777 (certificate CN imaginye.ddns.net).
Direct Thor TCP repeatedly times out. Thor TLS through temporary Mac SSH reverse forward succeeded in 0.151 s; tunnel removed afterward.
Mac and Thor report the same public IPv4 address through api.ipify.org.

Negative local tests: TX checksum offload disabled, TCP timestamps disabled (separately; restored and verified), MSS 1200 and 536, IP TOS 0/16/32/184, explicit source ports 20001/30001/40001. All timed out.
Thor TCP ECN/timestamps/window-scaling/SACK defaults match Linux builder. Wi-Fi power save disabled, PCI runtime power control on, -35 dBm signal, gateway ping 8/8 success around 3 ms. No unexpected IPv4 routing tables/rules, no tc filters shown. User-provided root capture shows outgoing SYN retries, no server replies; control 1.1.1.1:443 succeeds. iptables base policies ACCEPT and no rules; no nft output in supplied test.

TCP TTL error-queue probes prove requests reach home gateway (TTL1), 10.29.26.2 (TTL3), 149.6.187.9 (TTL4), and 130.117.1.106 (TTL6), with ICMP replies returned to the Thor. Other sampled TTLs silent. This is not evidence those later hops drop traffic; ICMP may be suppressed.
Docker trace not directly comparable: VM networking returns apparent successful TCP connection at TTL2, likely due virtualization/proxy transport. Do not infer identical routes from these tests.

SSH contributor confirmed separately: old Mac ssh-connect.py raced 8 connections and abandoned 7, provoking OpenSSH unauthenticated-source penalties. Prior boot logs show penalties at 18:10, current diagnostic probes at 22:42. Helper replaced with single TCP relay, backup retained. Direct authenticated SSH and corrected helper work. This does not prove all historical SSH failures were explained.

CTGP logs show successful MK7/plugin launch followed by four roughly 134-second failed HTTP connections. Root cause of destination-specific TCP failure remains UNCONFIRMED. No emulator upgrade or persistent kernel/network changes applied for this investigation.
