# Kubernetes Persistent Volume High Usage

## Problem

Container is saving data to a persistent volume, but this volume will soon be out of space. This can switch accessMode to readOnly and prevent the container from correct functioning.

## Analysis

* Look at the history of the Prometheus metric, triggering the alert. You should be able to see whether the volume usage only goes up or also down, which would mean that a retention policy exists and pv cleanup is in place.
* The helmRelease in CephOpenstackLMA or the helm chart itself might also contain information about retention. Searching for the keyword `retention` is usually enough.

## Resolution

* If there is a retention policy:

1. Make sure its values are sane (= don't store data that no one will ever desire).
2. [Extent the persistentVolume](https://kubernetes.io/blog/2018/07/12/resizing-persistent-volumes-using-kubernetes/): flux might not recreate the pvc with different values, in which case it has to be [forced manually](https://dev.to/bzon/resizing-persistent-volumes-in-kubernetes-like-magic-4f96).

* If there is no retention policy: 

1. Explore the helm chart and turn the retain policy on (if possible).
2. Use [k8s-pvc-cleanup](https://gitlab.ics.muni.cz/cloud/g2/k8s-pvc-cleanup)!

## References
 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubepersistentvolumefillingup/)
