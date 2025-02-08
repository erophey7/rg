### NTP+DNS setup in 1 command
```
NTPIP="" && apt-get update && apt-get install -y chrony && \
grep -qxF "server $NTPIP iburst prefer" /etc/chrony.conf || echo "server $NTPIP iburst prefer" | tee -a /etc/chrony.conf && \
systemctl enable --now chronyd && systemctl restart chronyd; echo "search au.team\nnameserver 192.168.11.66\n nameserver 192.168.33.66" > /etc/net/ifaces/enp7s1/resolv.conf

```
### sshuser
```
useradd sshuser -m -U -s /bin/bash
echo "sshuser:P@ssword" | chpasswd
usermod -aG wheel sshuser
echo "sshuser ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
```