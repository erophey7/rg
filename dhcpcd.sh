#!/bin/bash

# Проверка наличия прав суперпользователя
if [ "$EUID" -ne 0 ]; then
  echo "Пожалуйста, запустите скрипт с правами суперпользователя (sudo)." >&2
  exit 1
fi

# Установка dhcpcd, если он не установлен
if ! command -v dhcpcd &> /dev/null; then
  echo "Установка dhcpcd..."
  apt-get update
  apt-get install -y dhcpcd
else
  echo "dhcpcd уже установлен."
fi

# Создание systemd unit-файла
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

# Создание правила udev
cat << 'EOF' > /etc/udev/rules.d/99-dhcpcd-auto.rules
ACTION=="add", SUBSYSTEM=="net", KERNEL=="eth*", RUN+="/bin/systemctl start dhcpcd@%k"
ACTION=="add", SUBSYSTEM=="net", KERNEL=="en*", RUN+="/bin/systemctl start dhcpcd@%k"
ACTION=="add", SUBSYSTEM=="net", KERNEL=="ens*", RUN+="/bin/systemctl start dhcpcd@%k"
ACTION=="add", SUBSYSTEM=="net", KERNEL=="wlan*", RUN+="/bin/systemctl start dhcpcd@%k"

ACTION=="remove", SUBSYSTEM=="net", KERNEL=="eth*", RUN+="/bin/systemctl stop dhcpcd@%k"
ACTION=="remove", SUBSYSTEM=="net", KERNEL=="en*", RUN+="/bin/systemctl stop dhcpcd@%k"
ACTION=="remove", SUBSYSTEM=="net", KERNEL=="ens*", RUN+="/bin/systemctl stop dhcpcd@%k"
ACTION=="remove", SUBSYSTEM=="net", KERNEL=="wlan*", RUN+="/bin/systemctl stop dhcpcd@%k"
EOF

# Перезагрузка служб udev и systemd
udevadm control --reload-rules
udevadm trigger
systemctl daemon-reload

echo "Конфигурация завершена. DHCP будет автоматически запускаться при подключении сетевых интерфейсов."
