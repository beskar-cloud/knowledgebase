# Alertmanager Reload Failed

**Initial runbook version.**

## Problem

The alert AlertmanagerFailedReload is triggered when the Alertmanager instance for the cluster monitoring stack has consistently failed to reload its configuration for a certain period.

## Analysis
 1. List Kubernetes Alertmanager objects: `kubectl get all -A | grep alertmanager`
 2. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct configuration reload

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
