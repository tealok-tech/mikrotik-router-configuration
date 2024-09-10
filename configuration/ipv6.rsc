/ipv6 settings set accept-router-advertisements=yes
# Add a pool for local network routing
/ipv6 pool add name=ipv6-ula prefix=fd00::/56 prefix-length=64
/ipv6 dhcp-client add add-default-route=yes interface=ether1 pool-name=ipv6-delegated-pool pool-prefix-length=60 prefix-hint=::/56 request=prefix use-peer-dns=no
# The following is used to tell other devices to use a custom DNS server for IPv6
# Useful for Pihole
#/ipv6 dhcp-server option add code=23 name=DNS value="'2001:0DB8::1'"
/ipv6 dhcp-server add address-pool=ipv6-delegated-pool interface=bridge name=ipv6-dhcp
/ipv6 address add address=::1 from-pool=ipv6-delegated-pool interface=bridge
/ipv6 address add address=fd00::1 comment="For routing between static addresses on the LAN" interface=bridge
