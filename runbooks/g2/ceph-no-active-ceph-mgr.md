# No Active Ceph Mgr

**Initial runbook version.**

## Problem

Ceph Manager isn't running.

## Analysis
 1. Check whether the manager is supposed to be deployed in [beskar-flux repo](https://github.com/beskar-cloud/beskar-flux)
 2. List Kubernetes ceph objects: `kubectl get all -A | grep ceph`
 3. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 4. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix errors preventing ceph-manager deployment, if any.

## References
 * 
