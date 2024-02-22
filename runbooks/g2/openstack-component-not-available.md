# OpenStack Component Not Available

**Initial runbook version.**

## Problem

API of some OpenStack component is not reachable.

## Analysis
 1. List Kubernetes objects of given component: `kubectl -n openstack get all | grep`
 2. Inspect any object in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
