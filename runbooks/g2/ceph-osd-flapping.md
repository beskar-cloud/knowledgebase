# Ceph OSD Flapping

**Initial runbook version.**

## Problem

Ceph object storage daemon is crashing repeatedly.

## Analysis
 1. List Kubernetes ceph objects: `kubectl get all -A | grep ceph`
 2. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Ceph OSD Troubleshooting](https://docs.ceph.com/en/latest/rados/troubleshooting/troubleshooting-osd/)
