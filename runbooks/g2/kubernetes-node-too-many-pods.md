# KubeletTooManyPods

**Initial runbook version.**

## Problem

Running many pods (more than 110) on a single node places a strain on the Container Runtime Interface (CRI), Container Network Interface (CNI), and the operating system itself. Approaching that limit may affect performance and availability of that node.

## Analysis

Check the number of pods on a given node by running:

```shell
kubectl get pods --all-namespaces --field-selector spec.nodeName=<node>
```

## Resolution

Since Kubernetes only officially supports [110 pods per node](https://kubernetes.io/docs/setup/best-practices/cluster-large/),
you should preferably move pods onto other nodes or expand your cluster with more worker nodes.

If you're certain the node can handle more pods, you can raise the max pods
per node limit by changing `maxPods` in your [KubeletConfiguration](https://kubernetes.io/docs/reference/config-api/kubelet-config.v1beta1/)
(for kubeadm-based clusters) or changing the setting in your cloud provider's
dashboard (if supported).

## References
 * [Community Runbook](https://runbooks.prometheus-operator.dev/runbooks/kubernetes/kubelettoomanypods/)
