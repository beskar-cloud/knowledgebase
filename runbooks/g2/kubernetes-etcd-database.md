# Kubernetes etcd Database Issues

**Initial runbook version.**

## Problem

Etcd database has little space left or is heavily fragmented.

## Analysis

 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/etcd/etcdbackendquotalowspace/)

 * [Etcd Monitoring](https://etcd.io/docs/v3.5/op-guide/monitoring/)
 * [Etcd Troubleshooting](https://ranchermanager.docs.rancher.com/troubleshooting/kubernetes-components/troubleshooting-etcd-nodes)

## Resolution
 * Defrag or increase the quota as the writes to etcd will be disabled when it is full.
 * Run defragmentation (e.g. etcdctl defrag) to retrieve the unused fragmented disk space.

## References
 * 
