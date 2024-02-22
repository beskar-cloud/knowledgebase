# MariaDB Galera Not Ready

**Initial runbook version.**

## Problem

MariaDB Galera responsible for data synchronization is not running on a specific node.

## Analysis

 * [MariaDB doesn't start](https://mariadb.com/kb/en/what-to-do-if-mariadb-doesnt-start/)

 1. List Kubernetes MariaDB objects: `kubectl get all -A | grep maria`
 2. Inspect any object in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Galera Known Limitations](https://mariadb.com/kb/en/mariadb-galera-cluster-known-limitations/)
