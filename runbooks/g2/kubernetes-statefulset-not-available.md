# Statefulset Not Available

**Initial runbook version.**

## Problem

Statefulset isn't starting correctly.

## Analysis
 1. Inspect it: `kubectl -n [ns] describe`
 2. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * 

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
