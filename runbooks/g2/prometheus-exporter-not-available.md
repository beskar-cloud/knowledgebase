# Prometheus Exporter Not Available

**Initial runbook version.**

## Problem

Prometheus OpenStack Exporter is not running.

## Analysis
 1. Check whether it is supposed to be running in [beskar-flux repo](https://github.com/beskar-cloud/beskar-flux)
 2. List exporter objects: `kubectl get all -A | grep prometheus-openstack-exporter`
 3. Inspect any object in state different from *Running*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 4. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Fix the error preventing exporter from running

## References
 * [Troubleshooting Cheatsheet](https://fluxcd.io/flux/cheatsheets/troubleshooting/)
