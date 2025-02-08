ecorouter>enable
ecorouter#configure
ecorouter(config)#hostname r-hq
r-hq(config)#ip domain-name au.team
r-hq(config)#write
r-hq#configure terminal
r-hq(config)#interface vl110
r-hq(config-if)#description "Clients"
r-hq(config-if)#ip address 192.168.11.1/26
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#interface vl220
r-hq(config-if)#description "Servers"
r-hq(config-if)#ip address 192.168.11.65/28
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#interface vl330
r-hq(config-if)#description "Administrators"
r-hq(config-if)#ip address 192.168.11.81/29
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#write
r-hq(config)#port te1
r-hq(config-port)#service-instance te1/vl110
r-hq(config-service-instance)#encapsulation dot1q 110 exact
r-hq(config-service-instance)#rewrite pop 1
r-hq(config-service-instance)#connect ip interface vl110
r-hq(config-service-instance)#exit
r-hq(config-port)#
r-hq(config-port)#service-instance te1/vl220
r-hq(config-service-instance)#encapsulation dot1q 220 exact
r-hq(config-service-instance)#rewrite pop 1
r-hq(config-service-instance)#connect ip interface vl220
r-hq(config-service-instance)#exit
r-hq(config-port)#
r-hq(config-port)#service-instance te1/vl330
r-hq(config-service-instance)#encapsulation dot1q 330 exact
r-hq(config-service-instance)#rewrite pop 1
r-hq(config-service-instance)#connect ip interface vl330
r-hq(config-service-instance)#exit
r-hq(config-port)#
r-hq(config-port)#write
r-hq#configure terminal
r-hq(config)#interface isp
r-hq(config-if)#ip address 172.16.5.14/28
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#port te0
r-hq(config-port)#service-instance te0/isp
r-hq(config-service-instance)#encapsulation untagged
r-hq(config-service-instance)#connect ip interface isp
r-hq(config-service-instance)#exit
r-hq(config-port)#exit
r-hq(config)#
r-hq(config)#ip route 0.0.0.0/0 172.16.5.1
r-hq(config)#write
r-hq(config)#
r-hq#configure terminal
r-hq(config)#interface isp
r-hq(config-if)#ip nat outside
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#interface vl110
r-hq(config-if)#ip nat inside
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#interface vl220
r-hq(config-if)#ip nat inside
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#interface vl330
r-hq(config-if)#ip nat inside
r-hq(config-if)#exit
r-hq(config)#
r-hq(config)#ip nat pool LOCAL-HQ 192.168.11.1-192.168.11.254
r-hq(config)#ip nat source dynamic inside pool LOCAL-HQ overload 172.16.5.14
r-hq(config)#write
r-hq(config)#
r-hq#configure terminal
r-hq(config)#ip pool CLI-HQ 192.168.11.2-192.168.11.62
r-hq(config)#
r-hq(config)#dhcp-server 1
r-hq(config-dhcp-server)#pool CLI-HQ 1
r-hq(config-dhcp-server-pool)#mask 26
r-hq(config-dhcp-server-pool)#gateway 192.168.11.1
r-hq(config-dhcp-server-pool)#dns 192.168.11.66,192.168.33.66
r-hq(config-dhcp-server-pool)#domain-name au.team
r-hq(config-dhcp-server-pool)#exit
r-hq(config-dhcp-server)#exit
r-hq(config)#
r-hq(config)#interface vl110
r-hq(config-if)#dhcp-server 1
r-hq(config-if)#exit
r-hq(config)#write
r-hq(config)#
r-hq#configure terminal
r-hq(config)#  interface tunnel.0
r-hq(config-if-tunnel)#description "Connect_DT-R"
r-hq(config-if-tunnel)#ip add 10.10.10.2/30
r-hq(config-if-tunnel)#ip mtu 1476
r-hq(config-if-tunnel)#ip tunnel 172.16.5.14 172.16.4.14 mode gre
r-hq(config-if-tunnel)#end
r-hq#write
r-hq#
r-hq#configure terminal
r-hq(config)#router ospf 1
r-hq(config-router)#ospf router-id 10.10.10.2
r-hq(config-router)#passive-interface default
r-hq(config-router)#network 10.10.10.0  0.0.0.3 area 0
r-hq(config-router)#network 192.168.11.0 0.0.0.63 area 0
r-hq(config-router)#network 192.168.11.64 0.0.0.15 area 0
r-hq(config-router)#network 192.168.11.80 0.0.0.7 area 0
r-hq(config-router)#no passive-interface tunnel.0
r-hq(config-router)#exit
r-hq(config)#exit
r-hq#write
r-hq#
r-hq#configure terminal
r-hq(config)#interface tunnel.0
r-hq(config-if-tunnel)#ip ospf authentication message-digest
r-hq(config-if-tunnel)#ip ospf message-digest-key 1 md5 P@ssw0rd
r-hq(config-if-tunnel)#exit
r-hq(config)#write
r-hq(config)#
r-hq#configure terminal
r-hq(config)#username sshuser
r-hq(config-user)#password P@ssw0rd
r-hq(config-user)#role admin 
r-hq(config-user)#exit
r-hq(config)#write
r-hq(config)#
r-hq#configure terminal
r-hq(config)#ip name-server 192.168.11.66 192.168.33.66
r-hq(config)#ip domain-name au.team
r-hq(config)#write
r-hq(config)#
r-hq#configure terminal
r-hq(config)#ntp server 192.168.11.66
r-hq(config)#ntp timezone UTC+3
r-hq(config)#write
r-hq(config)#