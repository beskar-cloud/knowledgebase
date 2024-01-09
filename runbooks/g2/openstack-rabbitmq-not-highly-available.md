# Rabbitmq Not Highly Available

**Initial runbook version.**

## Problem

There is less instances of Rabbitmq running than desired.

## Analysis

 1. Check how many instances are expected in the [manifest](https://github.com/beskar-cloud/beskar-flux). This was originally 3 - on every control-plane node.
 2. Check currently running Rabbitmq instances with the `rabbitmq_running` metric
 3. Inspect Kubernetes Rabbitmq objects on the node, where it isn't running but is expected to: `kubectl get all -A | grep rabbit`
 4. Inspect any objects in state different from *Running* or *Completed*: `kubectl -n [ns] describe` or `kubectl -n [ns] logs`
 5. Inspect Kubernetes events: `kubectl get events -n flux-system --field-selector type=Warning` and `kubectl get events -n [ns] --field-selector type=Warning` or `kubectl get helmreleases.helm.toolkit.fluxcd.io -A`

## Resolution
 * Might be temporary with a node in `down` state
 * Fix the error preventing correct functioning

## References
 * 
