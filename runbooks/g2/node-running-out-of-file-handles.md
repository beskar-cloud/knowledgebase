# Node File Handles Limit

**Initial runbook version.**

## Problem

This alert is triggered when a node's kernel is found to be running out of available file descriptors.

## Analysis

You can open a shell on the node and use the standard Linux utilities to
diagnose the issue:

```shell
$ NODE_NAME='<value of instance label from alert>'

$ oc debug "node/$NODE_NAME"
# sysctl -a | grep 'fs.file-'
fs.file-max = 1597016
fs.file-nr = 7104       0       1597016
# lsof -n
```

## Resolution
 * Reduce the number of files opened simultaneously by either adjusting application configuration or by moving some applications to other nodes.

## References
 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/node/nodefiledescriptorlimit/)
