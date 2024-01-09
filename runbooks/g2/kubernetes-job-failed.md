# Kubernetes Job Failed

**Initial runbook version.**

## Problem

One time job connected to a specific object (like Deployment) failed. This might be preventing connected objects from running correctly.

## Analysis

 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubejobfailed/)

 1. Inspect the job: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 2. Find the job context (object that initiated the job + what else it initiates)
 3. Inspect any object from contex in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 4. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing the job from finishing

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
