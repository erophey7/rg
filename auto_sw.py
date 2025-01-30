import os
import subprocess

#save_get function
def save_get(lst, index):
    try:
        return lst[index]
    except IndexError:
        return None
    
#Update value in file
def update_value(cfg, key, new_value, separator):
    parts = cfg.split('\n')
    updated = False

    for i, part in enumerate(parts):
        if part.startswith(f'{key}{separator}'):
            parts[i] = f'{key}{separator}{new_value}'
            updated = True
            break
    if not updated:
        parts.append(f'{key}{separator}{new_value}')

    return "\n".join(parts)



#Scan network adapters
def scan_adapters():
    adapters = {}
    cmd = subprocess.run(['ip -br a'],
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True)
    for i in cmd.stdout.split("\n"):
        l_formatted = [x for x in i.split(" ") if x]
        adapters[save_get(l_formatted, 0)] = {
            'name': save_get(l_formatted, 0),
            'state': save_get(l_formatted, 1),
            'ipv4': save_get(l_formatted, 2),
            'ipv6': save_get(l_formatted, 3)
            }
    return adapters

#Print interfaces
def print_adapters(adapters):
    for i in adapters.values():
        print(f'> {i["name"]}    {i["state"]}     {i["ipv4"]} {i["ipv6"]}')

#Create interface cfg
def make_adapter_cfg(adapter):
    ifaces_dir = '/etc/net/ifaces/'
    ls_ifaces = os.listdir(ifaces_dir)
    if os.path.isdir(ifaces_dir + adapter):
        pass
    else:
        os.mkdir(ifaces_dir + adapter)
    ls_ifaces = os.listdir(ifaces_dir)
    for i in ls_ifaces:
        if i == adapter:
            ls_iface = os.listdir(ifaces_dir + i)
            os.system(f'touch {ifaces_dir + i}/options')
            with open(f'{ifaces_dir + i}/options', "r") as file:
                cfg = file.read()
                cfg = update_value(cfg, "TYPE", "eth", "=")
                cfg = update_value(cfg, "BOOTPROTO", "static", "=")
            with open(f'{ifaces_dir + i}/options', "w") as file:
                file.write(cfg)
                file.close()

#Setup DNS server
def set_dns(nameserver):
    with open('/etc/resolv.conf', 'r') as file:
        reslov = file.read()
        resolv = update_value(reslov, 'nameserver', nameserver, ' ')
    with open('/etc/resolv.conf', 'w') as file:
        file.write(resolv)
        file.close

#Check and install openvswitch
def install_openvswitch():
    cmd = subprocess.run(['ovs-vsctl -h'],
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True)
    if cmd.stdout == '':
        os.system('apt-get update && apt-get -y install openvswitch')

#Update default interface
def update_default_interface():
    with open('/etc/net/ifaces/default/options', 'r') as file:
        options = file.read()
        options = update_value(options, 'OVS_REMOVE', 'yes', '=')
    with open('/etc/net/ifaces/default/options', 'w') as file:
        file.write(options)

#Create brige interface
def update_manage_interface(sw_ip, r_ip, br_name, br_interface, sw_vlan):
    if os.path.isdir(f'/etc/net/ifaces/{br_interface}/'):
        pass
    else:
        os.mkdir(f'/etc/net/ifaces/{br_interface}/')
    os.system(f'touch /etc/net/ifaces/{br_interface}/' + '{options,ipv4route,ipv4address}')

    with open(f'/etc/net/ifaces/{br_interface}/options', 'r') as file:
        options = file.read()
        options = update_value(options, 'TYPE', 'ovsport', '=')
        options = update_value(options, 'BOOTPROTO', 'static', '=')
        options = update_value(options, 'CONFIG_IPV4', 'yes', '=')
        options = update_value(options, 'BRIDGE', br_name, '=')
        options = update_value(options, 'VID', sw_vlan, '=')
    with open(f'/etc/net/ifaces/{br_interface}/options', 'w') as file:
        file.write(options)

    with open(f'/etc/net/ifaces/{br_interface}/ipv4route', 'r') as file:
        ipv4route = file.read()
        ipv4route = update_value(ipv4route, 'default via', r_ip, ' ')
    with open(f'/etc/net/ifaces/{br_interface}/ipv4route', 'w') as file:
        file.write(ipv4route)

    with open(f'/etc/net/ifaces/{br_interface}/ipv4address', 'w') as file:
        file.write(sw_ip)
            

def run():
    #setup env
    fqdn = input("FQDN> ")
    dns = input('Nameserver (empty for skip)> ')
    adapters = scan_adapters()
    print_adapters(adapters)
    select_bridge_adapters = input('Select adapters for brige(through space)> ').split(' ')
    sw_ip = input('Switch IP (ip\subnet)> ')
    r_ip = input('Router IP (ip)> ')
    br_name = input('Brigde name> ')
    VLANs = input('Network VLANs (through space)> ').split(' ')
    br_interface = input('Brige interface> ')
    sw_vlan = input('Switch VLAN> ')

    #set FQDN
    os.system(f'hostnamectl set-hostname {fqdn}')

    #Create interfaces cfg
    for i in select_bridge_adapters:
        make_adapter_cfg(i)

    #Set DNS server
    if dns != '':
        set_dns(dns)

    #setup OpenVSwitch
    install_openvswitch()
    os.system('systemctl enable --now openvswitch')
    os.system('systemctl start openvswitch')
    os.system('systemctl restart network')
    update_default_interface()
    update_manage_interface(sw_ip, r_ip, br_name, br_interface, sw_vlan)
    os.system(f'ovs-vsctl add-br {br_name}')
    for i in select_bridge_adapters:
        os.system(f'ovs-vsctl add-port {br_name} {i} trunk={",".join(VLANs)}')
    os.system('systemctl restart network')
    os.system('modprobe 8021q')
    os.system('echo "8021q" | tee -a /etc/modules')
    restart = input("Done, restart? (Y,n)> ")
    if restart == 'Y' or restart == '':
        os.system('reboot')

    

if __name__ == "__main__":
    run()
    