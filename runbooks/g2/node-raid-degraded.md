# Node RAID Degraded

**Initial runbook version.**

## Problem

RAID Array is degraded.
This alert is triggered when a node has a storage configuration with RAID array, and the array is reporting as being in a degraded state due to one or more disk failures.

## Analysis

You can open a shell on the node and use the standard Linux utilities to
diagnose the issue, but you may need to install additional software in the debug
container:

```shell
$ NODE_NAME='<value of instance label from alert>'

$ oc debug "node/$NODE_NAME"
$ cat /proc/mdstat
```

## Resolution

Cordon and drain node if possible, proceed to RAID recovery.
See the Red Hat Enterprise Linux [documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/managing_storage_devices/managing-raid_managing-storage-devices) for potential steps.

## References
 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/node/noderaiddegraded/)
