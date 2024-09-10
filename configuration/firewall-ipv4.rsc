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
