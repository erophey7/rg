### NTP setup in 1 command
```
NTPIP="" && apt-get update && apt-get install -y chrony && \
grep -qxF "server $NTPIP iburst prefer" /etc/chrony.conf || echo "server $NTPIP iburst prefer" | tee -a /etc/chrony.conf && \
systemctl enable --now chronyd && systemctl restart chronyd

```
### Users srv1-hq
```
samba-tool group add group1
samba-tool group add group2
samba-tool group add group3
for i in {1..10}; do
  samba-tool user add user$i P@ssw0rd;
  samba-tool user setexpiry user$i --noexpiry;
  samba-tool group addmembers "group1" user$i;
done
for i in {11..20}; do
  samba-tool user add user$i P@ssw0rd;
  samba-tool user setexpiry user$i --noexpiry;
  samba-tool group addmembers "group2" user$i;
done
for i in {21..30}; do
  samba-tool user add user$i P@ssw0rd;
  samba-tool user setexpiry user$i --noexpiry;
  samba-tool group addmembers "group3" user$i;
done
samba-tool ou add 'OU=CLI'
samba-tool ou add 'OU=ADMIN'

```