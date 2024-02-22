# Node Network Bonds Down

## Problem

In case a bonded network interface is aggregating N interfaces but not all them are active, the alert `node_network_bond_slaves_down` kicks in. The Prometheus metric `node_bonding_slaves` (type gauge) ~ number of configured slaves (slaves == underlying interfaces) per bonding interface) is then equal to N and the Prometheus metric `node_bonding_active` (type gauge) ~ number of active slaves per bonding interface is expected to match N in case of all slaves are up.

### Possible causes
* Slave is disabled administratively: Slave is disabled by purpose by administrator (`ip link set enp225s0f1 down`). Note that having a slave disabled may be a temporary fix for bonding issues when a failing interface may not be recognized by the bond and the bond keeps routing portion of the traffic through the interface.

* Load Imbalance: If the network traffic isn't distributed evenly across the bonded interfaces, it can lead to one or more interfaces being overwhelmed and going down.

* Switch or Network Infrastructure Problems: Problems with the network switch or other networking equipment that the bonded interfaces are connected to can cause this alert. This might include switch failures, misconfigurations, or network congestion.

* The link connection between a bonded interface and other network nodes can be affected by a malfunctioning of one of the aggregated interfaces. In the result, the link connection does fails and related business tasks (reading data from remote host, sending data to remote host) fail. As the bond implementation is not able to determine whether the link failure comes from the connected network or from possibly malfunctioning aggregated interfaces 


## Analysis
 * Check whether the interfaces aggregated in the bond are up. In case an interface is down, check with owner of the host. 
```
$> grep 'Slave Interface' /proc/net/bonding/bond0
$> ip link show <...>
```

* Check rate of `node_bonding_active`. The frequent rate is indicating malfunctioning of the interface (not necessarily HW issue). 

* Check utilization of the aggregated interfaces to confirm or exclude possible network congestion.
  * `node_network_transmit_bytes_total` 
  * `node_network_receive_bytes_total`


* Other options
  * Restart host
  * Check the configuration of the network switch to ensure nobody else touch the configuration.
  * Check Physical Connections
  * Check version of network drivers of the aggregated interfaces
  * Consult with supplier or vendor

## Resolution
 *  As the cause of the problem may vary, there is no clear answer for it 

## References
 * https://www.kernel.org/doc/Documentation/networking/bonding.txt
 * https://www.oracle.com/a/otn/docs/oraclepcax9-2_monitoring_and_alerting.pdf
