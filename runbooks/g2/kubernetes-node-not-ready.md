# Kubernetes Node Not Ready

**Initial runbook version.**

## Problem

Node has switched itself to NotReady status.

## Analysis

The notification details should list the node that's not ready. For Example:

```txt
 - alertname = KubeNodeNotReady
...
 - node = node1.example.com
...
```

Login to the cluster. Check the status of that node:

```shell
$ kubectl get node $NODE -o yaml
```

## Resolution
 The output should describe why the node isn't ready (e.g.: timeouts reaching the API or kubelet).

## References
 * [Debug on StackOverflow](https://stackoverflow.com/questions/47107117/how-to-debug-when-kubernetes-nodes-are-in-not-ready-state)
 * [Fix Guide](https://komodor.com/learn/how-to-fix-kubernetes-node-not-ready-error/)
