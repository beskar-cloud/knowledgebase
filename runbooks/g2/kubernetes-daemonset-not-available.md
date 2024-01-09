# Kubernetes Daemonset Not Available

**Initial runbook version.**

## Problem

There are more or less pods than expected by a specific Daemonset.

## Analysis

 * [MisScheduled](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubedaemonsetmisscheduled/), [NotScheduled](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubedaemonsetnotscheduled/)

 1. List Daemonsets: `kubectl get daemonset -A`
 2. Inspect the object: `kubectl -n [ns] describe`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error responsible for incorrect pod number

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
