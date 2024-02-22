# Rabbitmq Not Available

**Initial runbook version.**

## Problem

Rabbitmq is seen as down.

## Analysis
 1. List Kubernetes Rabbitmq objects: `kubectl get all -A | grep rabbit`
 2. Inspect any objects in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
