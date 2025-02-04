import os
import sys
import fileinput
import re
import pexpect
import time

def parse_config(config_str):
    config = {
        "admpass": "",
        "dns": {
            "A": [],
            "ZONE": [],
            "PTR": [],
            "CNAME": []
        }
    }

    lines = config_str.split("\n")
    
    for line in lines:
        line = line.strip()
        
        # Пропускаем пустые строки или комментарии
        if not line or line.startswith("#"):
            continue
        
        # Обрабатываем пароль администратора
        if line.startswith("ADMPASS:"):
            config["admpass"] = line.split(":", 1)[1].strip()
        
        # Обрабатываем DNS записи
        if line.startswith("A:"):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                ip, hostname = parts[1].split(" ", 1)
                config["dns"]["A"].append({"ip": ip.strip(), "hostname": hostname.strip()})
        elif line.startswith("ZONE:"):
            config["dns"]["ZONE"].append(line.split(":", 1)[1].strip())
        elif line.startswith("PTR:"):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                ip, hostname = parts[1].split(" ", 1)
                config["dns"]["PTR"].append({"ip": ip.strip(), "hostname": hostname.strip()})
        elif line.startswith("CNAME:"):
            parts = line.split(" ", 1)
            if len(parts) == 2:
                alias, target = parts[1].split(" ", 1)
                config["dns"]["CNAME"].append({"alias": alias.strip(), "target": target.strip()})
    
    return config

def read_config():
    try:
        with open('smb_bind.conf', 'r', encoding='utf-8') as file:
            return parse_config(file.read())
    except FileNotFoundError:
        with open('smb_bind.conf', 'a', encoding='utf-8') as file:
            example = ("# ADMPASS: Пароль администратора для доступа\n"
                       "# Пример: ADMPASS: P@ssw0rd\n\n"
                       "# DNS записи - соответствие IP-адресов и имен хостов\n"
                       "# Пример записи: \n"
                       "# A: 192.168.11.2 cli-hq.au.team   IP адрес 192.168.11.2 соответствует хосту cli-hq.au.team\n"
                       "# A: 192.168.11.66 srv1-hq.au.team   IP адрес 192.168.11.66 соответствует хосту srv1-hq.au.team\n\n\n"
                       "# Записи зоны - для определения зон обратного поиска (reverse lookup)\n"
                       "# ZONE: 11.168.192.in-addr.arpa  # Обратный поиск для подсети 192.168.11.x\n"
                       "# ZONE: 33.168.192.in-addr.arpa  # Обратный поиск для подсети 192.168.33.x\n\n\n"
                       "# Записи для обратного разрешения (PTR) - связывание IP-адресов с именами хостов\n"
                       "# Пример записи:\n"
                       "# PTR: 192.168.11.2 cli-hq.au.team   IP адрес 192.168.11.2 разрешается в имя cli-hq.au.team\n"
                       "# PTR: 192.168.11.66 srv1-hq.au.team   IP адрес 192.168.11.66 разрешается в имя srv1-hq.au.team\n\n\n"
                       "# CNAME записи - псевдонимы для доменных имен\n"
                       "# Пример записи:\n"
                       "# CNAME: www srv1-dt.au.team  # www.ua.team будет перенаправляться на srv1-dt.au.team\n"
                       "# CNAME: zabbix srv1-dt.au.team  # zabbix.ua.team будет перенаправляться на srv1-dt.au.team\n")
            file.write(example)

def verity_config(config):
    cfg_info = {'state': True, 'message': "не заполнено: "}

    if config['admpass'] == "":
        cfg_info['message'] += "ADMPASS, "
        cfg_info['state'] = False
    if config['dns']['A'] == []:
        cfg_info['message'] += "A, "
        cfg_info['state'] = False
    if config['dns']['ZONE'] == []:
        cfg_info['message'] += "ZONE, "
        cfg_info['state'] = False
    if config['dns']['PTR'] == []:
        cfg_info['message'] += "PTR, "
        cfg_info['state'] = False
    if config['dns']['CNAME'] == []:
        cfg_info['message'] += "CNAME"
        cfg_info['state'] = False

    return cfg_info


def insert_into_file(file_path, insert_lines, marker, before=True):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if marker in line:
                if before:
                    file.writelines(insert_lines)
                file.write(line)
                if not before:
                    file.writelines(insert_lines)
            else:
                file.write(line)

def replace_in_file(file_path, replacements):
    """Заменяет строки в файле по заданным шаблонам"""
    with fileinput.FileInput(file_path, inplace=True) as file:
        for line in file:
            for pattern, replacement in replacements.items():
                if re.search(pattern, line):
                    line = replacement + "\n"
            print(line, end='')

def domain_provision(password):
    try:
        child = pexpect.spawn('samba-tool domain provision', encoding='utf-8', timeout=300)

        # Выводим stdout в реальном времени
        child.logfile_read = sys.stdout  

        # Ожидание и ввод данных
        child.expect_exact("Realm [AU.TEAM]:")  
        child.sendline('')
        child.flush()  # Принудительно отправляем буфер

        child.expect_exact("Domain [AU]:")  
        child.sendline('')
        child.flush()

        child.expect_exact("Server Role (dc, member, standalone) [dc]:")  
        child.sendline('')
        child.flush()

        child.expect_exact("DNS backend (SAMBA_INTERNAL, BIND9_FLATFILE, BIND9_DLZ, NONE) [SAMBA_INTERNAL]:")  
        child.sendline('BIND9_DLZ')
        child.flush()

        child.expect_exact("Administrator password:")  
        child.sendline(password)
        child.flush()

        child.expect_exact("Retype password:")  
        child.sendline(password)
        child.flush()

        # Ждём завершения
        child.expect(pexpect.EOF)

    except Exception as e:
        print("Ошибка:", str(e))

def setup_samba_master(config):
    print('Installing Samba')
    os.system('apt-get install task-samba-dc -y')
    print('Configure BIND')
    os.system('control bind-chroot disabled')
    print('Disable KRB5RCACHETYPE')
    os.system('''grep -q KRB5RCACHETYPE /etc/sysconfig/bind || echo 'KRB5RCACHETYPE="none"' >> /etc/sysconfig/bind''')
    print('Enable BIND_DLZ')
    os.system('control bind-chroot disabled')
    os.system("""grep -q 'bind-dns' /etc/bind/named.conf || echo 'include "/var/lib/samba/bind-dns/named.conf";' >> /etc/bind/named.conf""")

    print('add settings to BIND')
    insert_into_file('/etc/bind/options.conf', ['        tkey-gssapi-keytab "/var/lib/samba/bind-dns/dns.keytab";\n', '        minimal-responses yes;\n'], "options {", before=False)
    insert_into_file('/etc/bind/options.conf', ['        category lame-servers { null; };\n'], "logging {", before=False)

    print('Stop BIND')
    os.system('systemctl stop bind')
    print('Clear Samba conf')
    os.system('rm -f /etc/samba/smb.conf')
    os.system('rm -rf /var/lib/samba')
    os.system('rm -rf /var/cache/samba')
    os.system('mkdir -p /var/lib/samba/sysvol')
    time.sleep(5)

    print('Start domain setup')
    domain_provision(config['admpass'])

    print('Start BIND and Samba')
    os.system('systemctl enable --now samba')
    os.system('systemctl start bind')

    print('Setup Kerberos')
    os.system('cp -f /var/lib/samba/private/krb5.conf /etc/krb5.conf')

    print('Setup shared folder')
    os.system('mkdir /opt/data')
    os.system('chmod 777 /opt/data')

    samba_conf = """
[SAMBA]
    path = /opt/data
    comment = SAMBA
    public = yes
    writable = yes
    browseable = yes
    guest ok = yes
    """
    with open('/etc/samba/smb.conf', "a+") as file:
        file.write(samba_conf)

    print('Restart Samba')
    os.system('systemctl restart samba')

    print('Setup Users and Groups')
    for i in range(1, 4):
        os.system(f'samba-tool group add group{i}')
    for i in range(1, 11):
        os.system(f'samba-tool user add user{i} P@ssw0rd;')
        os.system(f'samba-tool user setexpiry user{i} --noexpiry;')
        os.system(f'samba-tool group addmembers "group1" user{i};')
    for i in range(11, 21):
        os.system(f'samba-tool user add user{i} P@ssw0rd;')
        os.system(f'samba-tool user setexpiry user{i} --noexpiry;')
        os.system(f'samba-tool group addmembers "group2" user{i};')
    for i in range(21, 31):
        os.system(f'samba-tool user add user{i} P@ssw0rd;')
        os.system(f'samba-tool user setexpiry user{i} --noexpiry;')
        os.system(f'samba-tool group addmembers "group3" user{i};')
    os.system("samba-tool ou add 'OU=CLI'")
    os.system("samba-tool ou add 'OU=ADMIN'")


def dns_necessary(config):
    maincmd = 'echo "P@ssw0rd" | {} -U Administrator'
    necessary_A = config['dns']['A']
    necessary_ZONE = config['dns']['ZONE']
    necessary_PTR = config['dns']['PTR']
    necessary_CNAME = config['dns']['CNAME']

    for i in necessary_A:
        name = i['hostname'].split('.')[0]
        domain = f"{i['hostname'].split('.')[1]}.{i['hostname'].split('.')[2]}"
        os.system(maincmd.format(f'samba-tool dns add 127.0.0.1 {domain} {name} A {i["ip"]}'))

    for i in necessary_ZONE:
        os.system(maincmd.format(f'samba-tool dns zonecreate 127.0.0.1 {i}'))

    for i in necessary_PTR:
        reversed_ip = '.'.join(list(reversed(i['ip'].split('.')[:-1])))
        subnet8 = i['ip'].split('.')[3]
        os.system(maincmd.format(f'samba-tool dns add 127.0.0.1 {reversed_ip}.in-addr.arpa {subnet8} PTR {i["hostname"]}'))

    for i in necessary_CNAME:
        domain = f"{i['target'].split('.')[1]}.{i['target'].split('.')[2]}"
        os.system(maincmd.format(f"samba-tool dns add 127.0.0.1 {domain} {i['alias']} CNAME {i['target']}"))


def setup_server_master():
    config = read_config()
    if verity_config(config)['state'] == True:
        setup_samba_master(config)
        dns_necessary(config)
    else:
        print(verity_config(config)['message'])
        exit(0)
    

def setup_samba_slave(admpass, slave_server_fqdn, master_server_fqdn):
    print('Installing Samba')
    os.system('apt-get install task-samba-dc -y')

    print('Stop Conflict services')
    for i in ['smb', 'nmb', 'krb5kdc', 'slapd', 'bind']:
        os.system(f'systemctl disable {i}; systemctl disable {i}')

    print('Disable KRB5RCACHETYPE')
    os.system('''grep -q KRB5RCACHETYPE /etc/sysconfig/bind || echo 'KRB5RCACHETYPE="none"' >> /etc/sysconfig/bind''')
    print('Enable BIND_DLZ')
    os.system('control bind-chroot disabled')

    print('add settings to BIND')
    insert_into_file('/etc/bind/options.conf', ['        tkey-gssapi-keytab "/var/lib/samba/bind-dns/dns.keytab";\n', '        minimal-responses yes;\n'], "options {", before=False)
    insert_into_file('/etc/bind/options.conf', ['        category lame-servers { null; };\n'], "logging {", before=False)

    print('Add settings to krb5')
    krb5conf = "/etc/krb5.conf"
    replace_in_file(krb5conf, {
    r"^\s*dns_lookup_realm\s*=\s*true": " dns_lookup_realm = false",
    r"^\s*dns_lookup_kdc\s*=\s*false": " dns_lookup_kdc = true"
    })
    default_realm_line = " default_realm = AU.TEAM\n"
    with open(krb5conf, 'r') as file:
        if not any("default_realm = AU.TEAM" in line for line in file):
            insert_into_file(krb5conf, [default_realm_line], "[libdefaults]", before=False)
    print('kerberos request')
    os.system(f'echo "{admpass}" | kinit administrator@AU.TEAM')
    print('Clear Samba config')
    os.system(f'rm -f /etc/samba/smb.conf')
    os.system(f'rm -rf /var/lib/samba')
    os.system(f'rm -rf /var/cache/samba')
    os.system(f'mkdir -p /var/lib/samba/sysvol')
    print('Enter to domain')

    # Исправленный код: получаем домен из FQDN
    parts = slave_server_fqdn.split('.')
    if len(parts) >= 3:
        domain = '.'.join(parts[1:])  # Берём второй и третий элемент, и соединяем их
    else:
        raise ValueError(f"FQDN '{slave_server_fqdn}' некорректен, должно быть минимум три части")

    os.system(f'echo "{admpass}" | samba-tool domain join {domain} DC -U administrator --realm={domain} --dns-backend=BIND9_DLZ')
    print('Enable samba, bind')
    os.system('systemctl enable --now samba')
    os.system('systemctl enable --now bind')
    print('Replicate domain controlers')
    os.system(f'echo "{admpass}" | samba-tool drs replicate {slave_server_fqdn} {master_server_fqdn} dc=au,dc=team -U administrator')
    os.system(f'echo "{admpass}" | samba-tool drs replicate {master_server_fqdn} {slave_server_fqdn} dc=au,dc=team -U administrator')


if __name__ == "__main__":
    try:
        mode = sys.argv[1]
    except IndexError:
        print(f'Usage: python3 {sys.argv[0]} <mode (master/slave)> <admin pass (if slave)> <slave server fqdn> <master server fqdn>')
        exit(0)

    if mode == 'master':
        setup_server_master()

    if mode == 'slave':
        try:
            admpass = sys.argv[2]
            slave_server_fqdn = sys.argv[3]
            master_server_fqdn = sys.argv[4]
        except IndexError:
            print(f'Usage: python3 {sys.argv[0]} <mode (master/slave)> <admin pass (if slave)> <slave server fqdn> <master server fqdn>')
            exit(0)
        setup_samba_slave(admpass, slave_server_fqdn, master_server_fqdn)

    else:
        print(f'Usage: python3 {sys.argv[0]} <mode (master/slave)> <admin pass (if slave)> <slave server fqdn> <master server fqdn>')
        exit(0)