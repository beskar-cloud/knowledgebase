# OpenStack Exporter Not Available

**Initial runbook version.**

## Problem

OpenStack Exporter is not publishing metrics or being scraped.

## Analysis
 1. Inspect Exporter as a target in Prometheus for error messages.
 2. List Kubernetes objects: `kubectl -n openstack get all | grep openstack-exporter`
 3. Inspect any object in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 4. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing correct functioning

## References
 * 
