#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Использование: $0 <пользователь> <пароль>"
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Этот скрипт нужно запускать от имени root."
  exit 1
fi

USER="$1"
PASSWORD="$2"

useradd $USER -m -U -s /bin/bash
echo "$USER:$PASSWORD" | chpasswd
usermod -aG wheel $USER
echo "$USER ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers