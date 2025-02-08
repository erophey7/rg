ecorouter>enable
ecorouter#configure
ecorouter(config)#hostname r-dt
r-hq(config)#ip domain-name au.team
r-hq(config)#write
r-dt#configure terminal
r-dt(config)#interface int1
r-dt(config-if)#description "Connect_FW-DT"
r-dt(config-if)#ip address 192.168.33.89/30
r-dt(config-if)#exit
r-dt(config)#
r-dt(config)#port te1
r-dt(config-port)#service-instance te1/int1
r-dt(config-service-instance)#encapsulation untagged
r-dt(config-service-instance)#connect ip interface int1
r-dt(config-service-instance)#exit
r-dt(config-port)#write
r-dt(config-port)#
r-dt#configure terminal
r-dt(config)#interface isp
r-dt(config-if)#ip address 172.16.4.14/28
r-dt(config-if)#exit
r-dt(config)#
r-dt(config)#port te0
r-dt(config-port)#service-instance te0/isp
r-dt(config-service-instance)#encapsulation untagged
r-dt(config-service-instance)#connect ip interface isp
r-dt(config-service-instance)#exit
r-dt(config-port)#exit
r-dt(config)#
r-dt(config)#ip route 0.0.0.0/0 172.16.4.1
r-dt(config)#write
r-dt(config)#
r-dt#configure terminal
r-dt(config)#interface isp
r-dt(config-if)#ip nat outside
r-dt(config-if)#exit
r-dt(config)#
r-dt(config)#interface int1
r-dt(config-if)#ip nat inside
r-dt(config-if)#exit
r-dt(config)#
r-dt(config)#ip nat pool LOCAL-DT 192.168.33.1-192.168.33.254
r-dt(config)#ip nat source dynamic inside pool LOCAL-DT overload 172.16.4.14
r-dt(config)#write
r-dt(config)#
r-dt#configure terminal
r-dt(config)#ip pool CLI-DT 192.168.33.2-192.168.33.62
r-dt(config)#dhcp-server 1
r-dt(config-dhcp-server)#pool CLI-DT 1
r-dt(config-dhcp-server-pool)#mask 26
r-dt(config-dhcp-server-pool)#gateway 192.168.33.1
r-dt(config-dhcp-server-pool)#dns 192.168.33.66,192.168.11.66
r-dt(config-dhcp-server-pool)#domain-name au.team
r-dt(config-dhcp-server-pool)#exit
r-dt(config-dhcp-server)#exit
r-dt(config)#interface int1
r-dt(config-if)#dhcp-server 1
r-dt(config-if)#exit
r-dt(config)#write
r-dt(config)#
r-dt#configure terminal
r-dt(config)#  interface tunnel.0
r-dt(config-if-tunnel)#description "Connect_HQ-R"
r-dt(config-if-tunnel)#ip add 10.10.10.1/30
r-dt(config-if-tunnel)#ip mtu 1476
r-dt(config-if-tunnel)#ip tunnel 172.16.4.14 172.16.5.14 mode gre
r-dt(config-if-tunnel)#end
r-dt#write
r-dt#
r-dt#configure terminal
r-dt(config)#router ospf 1
r-dt(config-router)#ospf router-id 10.10.10.1
r-dt(config-router)#passive-interface default
r-dt(config-router)#network 10.10.10.0  0.0.0.3 area 0
r-dt(config-router)#network 192.168.33.88 0.0.0.3 area 0
r-dt(config-router)#no passive-interface tunnel.0
r-dt(config-router)#no passive-interface int1
r-dt(config-router)#exit
r-dt(config)#exit
r-dt#write
r-dt#
r-dt#configure terminal
r-dt(config)#interface tunnel.0
r-dt(config-if-tunnel)#ip ospf authentication message-digest
r-dt(config-if-tunnel)#ip ospf message-digest-key 1 md5 P@ssw0rd
r-dt(config-if-tunnel)#exit
r-dt(config)#write
r-dt(config)#
r-dt#configure terminal
r-dt(config)#router ospf 1
r-dt(config-router)#default-information originate 
r-dt(config-router)#exit
r-dt(config)#  write
r-dt(config)#
r-hq#configure terminal
r-hq(config)#username sshuser
r-hq(config-user)#password P@ssw0rd
r-hq(config-user)#role admin 
r-hq(config-user)#exit
r-hq(config)#write
r-hq(config)#
r-dt#configure terminal
r-dt(config)#ip name-server 192.168.33.66 192.168.11.66
r-dt(config)#ip domain-name au.team
r-dt(config)#write
r-dt(config)#
r-hq#configure terminal
r-hq(config)#ntp server 192.168.11.66
r-hq(config)#ntp timezone UTC+3
r-hq(config)#write
r-hq(config)#