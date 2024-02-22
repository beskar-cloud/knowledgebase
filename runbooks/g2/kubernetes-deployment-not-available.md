# Kubernetes Deployment Not Available

**Initial runbook version.**

## Problem

There are more or less pods than expected by a specific Deployment.

## Analysis

 * [GenerationMismatch](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubedeploymentgenerationmismatch/), [ReplicasMismatch](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubedeploymentreplicasmismatch/)

 1. List Deployments: `kubectl get deployment -A`
 2. Inspect the object: `kubectl -n [ns] describe`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error responsible for incorrect pod number

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
