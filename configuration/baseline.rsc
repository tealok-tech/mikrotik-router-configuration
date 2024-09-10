{
:local i 0
#Number of interfaces. It is necessary to reconfigure this number for each device (/interface print count-only)
:local x 5
#Max time to wait
:local t 30
while ($i < $t && [:len [/interface find]] < $x) do={
:put $i
:set $i ($i + 1)
:delay 1
}
if ($i = $t) do={
:log warning message="Could not load all physical interfaces"
} else={
/interface bridge add auto-mac=yes name=bridge
/interface list add name=WAN
/interface list add name=LAN
/interface wireless security-profiles set [ find default=yes ] supplicant-identity=MikroTik
/ip hotspot profile set [ find default=yes ] html-directory=hotspot
/ip pool add name=default-dhcp ranges=192.168.88.10-192.168.88.254
/ip dhcp-server add address-pool=default-dhcp disabled=no interface=bridge 
/interface bridge port add bridge=bridge interface=ether2
/interface bridge port add bridge=bridge interface=ether3
/interface bridge port add bridge=bridge interface=ether4
/interface bridge port add bridge=bridge interface=ether5
/ip neighbor discovery-settings set discover-interface-list=LAN
/interface list member add interface=bridge list=LAN
/interface list member add interface=ether1 list=WAN
/ip address add address=192.168.88.1/24 interface=bridge network=192.168.88.0
/ip dhcp-client add disabled=no interface=ether1
/ip dhcp-server network add address=192.168.88.0/24 dns-server=192.168.88.1 gateway=192.168.88.1
/ip dns set allow-remote-requests=yes
/ip dns static add address=192.168.88.1 name=router.lan
/ip firewall filter add action=accept chain=input comment="accept established,related,untracked" connection-state=established,related,untracked
/ip firewall filter add action=drop chain=input comment="drop invalid" connection-state=invalid
/ip firewall filter add action=accept chain=input comment="accept ICMP" protocol=icmp
/ip firewall filter add action=accept chain=input comment="accept to local loopback (for CAPsMAN)" dst-address=127.0.0.1
/ip firewall filter add action=drop chain=input comment="drop all not coming from LAN" in-interface-list=!LAN
/ip firewall filter add action=accept chain=forward comment="accept in ipsec policy" ipsec-policy=in,ipsec
/ip firewall filter add action=accept chain=forward comment="accept out ipsec policy" ipsec-policy=out,ipsec
/ip firewall filter add action=fasttrack-connection chain=forward comment="fasttrack" connection-state=established,related
/ip firewall filter add action=accept chain=forward comment="accept established,related, untracked" connection-state=established,related,untracked
/ip firewall filter add action=drop chain=forward comment="drop invalid" connection-state=invalid
/ip firewall filter add action=drop chain=forward comment="drop all from WAN not DSTNATed" connection-nat-state=!dstnat connection-state=new in-interface-list=WAN
/ip firewall nat add action=masquerade chain=srcnat comment="masquerade" ipsec-policy=out,none out-interface-list=WAN
/tool mac-server set allowed-interface-list=LAN
/tool mac-server mac-winbox set allowed-interface-list=LAN
}
}
