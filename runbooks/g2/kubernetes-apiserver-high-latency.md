# Kubernetes API Server High Latency

**Initial runbook version.**

## Problem

Kubernetes API Server is slower than expected.

## Analysis
 1. List Kubernetes kube-api objects: `kubectl get all -A | grep kube-api`
 2. Inspect the object: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Slow responses could be caused by inadequate pod resources
 * Fix the error slowing down the pod

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
