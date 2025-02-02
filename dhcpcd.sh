#!/bin/bash

# Проверка на root-права
if [ "$(id -u)" -ne 0 ]; then
    echo "Пожалуйста, запустите этот скрипт с правами root."
    exit 1
fi

# Установка dhcpcd
echo "Установка dhcpcd..."
apt-get update && apt-get install -y dhcpcd

# Создание systemd шаблонного юнит-файла
echo "Создание systemd юнит-файла..."
cat << 'EOF' > /etc/systemd/system/dhcpcd@.service
[Unit]
Description=DHCP Client Daemon for %i
Documentation=man:dhcpcd(8)
After=network.target
Wants=network.target

[Service]
Type=forking
ExecStart=/sbin/dhcpcd -q -b %i
ExecStop=/sbin/dhcpcd -x %i
Restart=on-failure
PIDFile=/run/dhcpcd-%i.pid

[Install]
WantedBy=multi-user.target
EOF

# Создание универсального юнит-файла для всех интерфейсов
echo "Создание systemd юнита для всех интерфейсов..."
cat << 'EOF' > /etc/systemd/system/dhcpcd-all.service
[Unit]
Description=DHCP Client Daemon for all interfaces
After=network.target
Wants=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'for iface in $(ls /sys/class/net | grep -v lo); do systemctl start dhcpcd@$iface.service; done'
ExecStop=/bin/bash -c 'for iface in $(ls /sys/class/net | grep -v lo); do systemctl stop dhcpcd@$iface.service; done'

[Install]
WantedBy=multi-user.target
EOF

# Создание правила udev для автозапуска при подключении/отключении интерфейсов
echo "Создание правила udev для автозапуска..."
cat << 'EOF' > /etc/udev/rules.d/99-dhcpcd-auto.rules
ACTION=="add", SUBSYSTEM=="net", NAME!="lo", RUN+="/bin/systemctl start dhcpcd@%k"
ACTION=="remove", SUBSYSTEM=="net", NAME!="lo", RUN+="/bin/systemctl stop dhcpcd@%k"
EOF

# Перезагрузка правил systemd и udev
echo "Перезагрузка systemd и правил udev..."
systemctl daemon-reload
udevadm control --reload-rules
udevadm trigger

# Включение dhcpcd-all для автозапуска при загрузке
echo "Активация dhcpcd для всех интерфейсов при загрузке..."
systemctl enable dhcpcd-all.service
systemctl start dhcpcd-all.service

echo "Установка и настройка завершены!"
