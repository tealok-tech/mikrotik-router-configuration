# Basic configurations

**These have only been tested with a hEX lite RouterBOARD**

These are configurations that provide a basic template that makes the router 'declarative' for certain values of declarative. In essence we want a way to set the entire configuration of the router in a single file without having to know the previous state of the router. Each of these comes with a preamble that is was taken from [the Mikrotik wiki](https://wiki.mikrotik.com/wiki/Manual:Configuration_Management#Importing_Configuration). The preamble waits until a number of interfaces is online before applying the configuration.

Without this delay the configuration will not correctly apply.

Some people use a delay for this function. Waiting for the interfaces is more reliable.

If you apply these configurations to a device you should ensure it has the correct number of interfaces. You can check the number of interfaces with `/interface print count-only`.

Start by applying the `baseline.rsc` script on reset:

```
scp baseline.rsc admin@192.168.88.1:/flash/baseline.rsc
ssh admin@192.168.88.1
/system reset-configuration run-after-reset=flash/baseline.rsc keep-users=yes no-defaults=yes skip-backup=yes
```

The router should then reset, wait for the interfaces to come online, then apply the baseline configuration. This will maintain the same `admin` user and the password printed on the bottom of the device/in the documentation that came with the device. From there you can apply additional configuration scripts:

```
scp [script] admin@192.168.88.1:/[script]
ssh admin@192.168.88.1
/import [script] verbose=yes
```

So, to add IPv6 support you'd do:

```
scp ipv6.rsc admin@192.168.88.1:/ipv6.rsc
ssh admin@192.168.88.1
/import ipv6.rsc verbose=yes
```

## baseline.rsc

This sets up DHCP from an upstream rounter (like an ISP) and a DHCPv4 server for the LAN managed by the router. You can communicate with the router at 192.168.88.1

## IPv6

There is no way that I know of to use a script to enable the IPv6 module declaratively. This is because the module must be enabled, then the router restarted. Eventually we'll manage the router entirely via a go program and be able to overcome all of this.

### ipv6.rsc

This script assumes that the router has the ipv6 module enabled and the router has been restarted so that the ipv6 module is loaded. It then configures the router with DHCPv6-PD (prefix delegation) which will request a subnet from the upstream router via prefix delegation, then provide addresses within that subnet to downstream devices.

## Firewalls

IPv4 doesn't work correctly without some firewall rules since we need to do network address translation (NAT). The baseline includes more rules than that, preferring to include most of the same rules that come in the Mikrotik default set. The specific IPv4 rules are separated out into `firewall-ipv4.rsc` for convenience. You can drop all of the existing firewall rules and recreate them without resetting the entire device and re-establishing connectivity.

For IPv6 we take the opposite approach. IPv6 does not need NAT, so we include no firewall rules in the default set. You can apply firewall rules with `firewall-ipv6.rsc`
