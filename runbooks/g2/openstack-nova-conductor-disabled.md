# OpenStack Nova-Conductor Disabled

**Initial runbook version.**

## Problem

It is quite normal that some OStack compute nodes are disabled.

## Analysis
 * identify what OStack hypervisors are disabled including the reason: `openstack compute service list --long | grep disabled`

## Resolution
 * if you find some hypervisor should not be disabled enable it with `openstack compute service set --enable <node-fqdn> nova-conductor`
 * if you find some hypervisors disabled without a reason attach the reason in format described in [team/provide-reasons-when-possible.md](/team/provide-reasons-when-possible.md) using command `openstack compute service set --disable --disable-reason "<disable-reason>" <node-fqdn> nova-conductor`

## References
 * 
