# The Flux Runbook

**Initial runbook version.**

## Problem

Flux isn't working correctly, either its components are experiencing issues or it isn't synchronizing the GitOps repository.

## Analysis
 1. Alerts should be descriptive enough to pinpoint the problem or unfunctional component
 2. List flux objects: `kubectl get all -n flux-system`
 3. Inspect any object in state different from *Running*: `kubectl -n flux-system describe` or `kubectl -n flux-system logs`
 4. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * To fix reconciliation failures suspend and resume: `flux -n [ns] suspend hr [name]` and `flux -n [ns] resume hr [name]`
 * To resume suspended resources: `flux -n [ns] resume hr [name]`
 * Fix the error preventing Flux components from running

## References
 * [Flux Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
