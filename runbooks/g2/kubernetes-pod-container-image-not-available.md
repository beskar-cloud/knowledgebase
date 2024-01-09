# Pod Image Not Available

**Initial runbook version.**

## Problem

Pod can't fetch specified container image.

## Analysis
 1. Inspect the pod to get the image: `kubectl -n [ns] describe`
 2. Check image availability from outside the node.
 3. Consider node connection issues

## Resolution
 * Fix the image reference or connection issue

## References
 * 
