# MariaDB Exporter Unavailable

**Initial runbook version.**

## Problem

MariaDB Exporter is not publishing metrics.

## Analysis
 1. List Kubernetes MariaDB objects: `kubectl get all -A | grep maria`
 2. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
