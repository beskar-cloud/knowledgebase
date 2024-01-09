# Calico Felix IPtables Restore Failures

**Initial runbook version.**

## Problem

Kubernetes networking solution Calico has a component called Felix responsible for manipulating IPtables and routing tables. Felix has encountered unexpected issues.

## Analysis
 1. List Kubernetes Calico objects: `kubectl get all -A | grep calico`
 2. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Calico Known Issues](https://github.com/projectcalico/calico/issues)
