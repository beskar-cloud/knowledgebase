# Kubernetes API Server Not Available

**Initial runbook version.**

## Problem

Kubernetes API Server is not running.

## Analysis

 * [KubeAPIDown](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubeapidown/)

 1. List Kubernetes kube-api objects: `kubectl get all -A | grep kube-api`
 2. Inspect the object: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * 

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
