# OpenStack Nova-Scheduler Down

**Initial runbook version.**

## Problem

OpenStack nova-scheduler is not running.

## Analysis

 * It's OK if the node is under maintenance

 1. List Kubernetes nova objects on the node: `kubectl -n openstack get all | grep nova`
 2. Inspect any object in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * 
