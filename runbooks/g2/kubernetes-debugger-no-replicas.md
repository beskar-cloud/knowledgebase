# Kubernetes Debugger No Replicas

**Initial runbook version.**

## Problem

Debugger has no replicas.

## Analysis
 1. Check whether the debugger is supposed to have replicas in [beskar-flux repo](https://github.com/beskar-cloud/beskar-flux)
 2. List debugger objects: `kubectl get all -A | grep debugger`
 3. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 4. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * If desired, scale debugger to more replicas
 * Fix the error preventing debugger from running

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
