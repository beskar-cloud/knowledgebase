# Linux Network Bonding

Read more information about bonding [in the bonding howto](https://www.kernel.org/doc/Documentation/networking/bonding.txt).

You may also look into [IEEE 802.3ad brief](https://en.wikipedia.org/wiki/Link_aggregation) or [full specification](https://www.ieee802.org/3/ad/public/mar99/seaman_1_0399.pdf).

## Troubleshooting

Checklist
* Check service availability (for instance node-exporter on TCP port 9100) from different nodes (`ncat -z <ip> 9100;echo $?` or `curl -L -v http://<ip>:9100/metrics`)
* Compare following checks on node with problem with node with NO problem ([A/B testing](https://en.wikipedia.org/wiki/A/B_testing))
  * Get bonding configuration and status (`ls /proc/net/bonding;cat /proc/net/bonding/bond0`)
    * decode bonding port status (`Slave Interface: X / details actor lacp pdu / port status`) [according table](https://movingpackets.net/2017/10/17/decoding-lacp-port-state/)
    * get bond configuration (cat /etc/sysconfig/network-scripts/ifcfg-bond0)
  * Linux NICs under bond are functional and has link (`ethtool em2`)
  * Step by step bring down and up all real bonded NICs (`ip link set dev em2 down;sleep 10; ip link set dev em2 up`)
    * Alternatively bring down all the bonded NICs including the bond NIC itself (`ip link set dev em1 down;ip link set dev em2 down;ip link set dev bond0 down;sleep 10; ip link set dev bond0 up;ip link set dev em2 up;ip link set dev em1 up`)
  * Check whether bonding and/or ethtool statuses have changed
  * Check that node is fully updated ([there were LACP issues later in RHEL7.9 cycle](https://access.redhat.com/discussions/3357541#comment-2329941))
* doublecheck state of the bond on the router if you can to doublecheck whether we are [hitting possible router issue](https://supportportal.juniper.net/s/article/QFX-Mismatched-LACP-bundle-state-when-core-isolation-and-minimum-links-config-are-enabled?language=en_US)
* if nothing helps you reboot and redo above checks (with complete updated system)

```sh
# get routes
ip r l
# test ping on non functional bond
ping -I bond0.677 10.16.61.5
# test TCP access to hypervisor node-exporter
for i in 10.16.108.{31,32,35}; do ncat -w 1 -z $i 9100;echo "$i:9100 $?"; done

# see bonding status, especially:
# * MII Status
# * Active Aggregator Info / Number of ports
# * Slave Interface: X / details actor lacp pdu / port status
# you should see port status as 63, if not see table https://movingpackets.net/2017/10/17/decoding-lacp-port-state/
cat /sys/class/net/bond0/bonding/mode
cat /proc/net/bonding/bond0

# check whether interfaces in the bond are functional
ethtool em1;ethtool em2

# bring step by step interfaces in bond down & up again
## em2
ip a sh dev em2
ip link set dev em2 down;sleep 10; ip link set dev em2 up
ip a sh dev em2
cat /proc/net/bonding/bond0

## em1
...

# if nothing helps bring down and up all interfaces including the bond
ip link set dev em1 down;ip link set dev em2 down;ip link set dev bond0 down;sleep 10; ip link set dev bond0 up;ip link set dev em2 up;ip link set dev em1 up

# if you still see NICs functional from ethtool and bonding but bonding port state is wrong (> 70), then perform package upgrade to latest and restart hypervisor
```
Complete terminal transcripts can be seen here:
 * [bonding problem present](/howtos/artefacts/linux-network-bonding/bonding-issue-before-fix.log)
 * [bonding problem fixed](/howtos/artefacts/linux-network-bonding/bonding-issue-after-fix.log)

# References:
 * https://www.kernel.org/doc/Documentation/networking/bonding.txt
 * https://wiki.linuxfoundation.org/networking/bonding
 * https://en.wikipedia.org/wiki/Link_aggregation
 * https://www.ieee802.org/3/ad/public/mar99/seaman_1_0399.pdf
 * https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/networking_guide/sec-verifying_network_configuration_bonding_for_redundancy
 * https://supportportal.juniper.net/s/article/Linux-Troubleshooting-bond-interfaces-on-RHEL-CentOS-7-5?language=en_US
 * https://movingpackets.net/2017/10/17/decoding-lacp-port-state/
 * https://access.redhat.com/discussions/3357541
 * https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/10/html/ovs-dpdk_end_to_end_troubleshooting_guide/configure_and_test_lacp_bonding_with_open_vswitch_dpdk
 * https://www.thegeekdiary.com/basics-of-ethernet-bonding-in-linux/
