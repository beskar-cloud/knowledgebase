# MariaDB High Table Locks

**Initial runbook version.**

## Problem

MariaDB is waiting too long to lock tables.

## Analysis

 1. List Kubernetes MariaDB objects: `kubectl get all -A | grep maria`
 2. Inspect it: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 3. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

 * [MariaDB Debugging](https://mariadb.com/kb/en/debugging-mariadb/)

## Resolution
 * Fix the error preventing correct functioning

## References
 * [Galera Known Limitations](https://mariadb.com/kb/en/mariadb-galera-cluster-known-limitations/)
