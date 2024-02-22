# Node RAID Inactive

**Initial runbook version.**

## Problem

RAID is in inactive state.

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
 * 

## References
 * [Community RAIDdegraded Runbook](https://runbooks.prometheus-operator.dev/runbooks/node/noderaiddegraded/)
