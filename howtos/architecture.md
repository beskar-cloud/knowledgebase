# Beskar cloud architecture

Beskar cloud stands for OpenStack (IaaS) and Kubernernetes (CaaS) clouds with distributed (ceph) storage in one solution.


## Architecture overview

Each cloud node has installed and cloud configured Ubuntu LTS operating system (via [infra-config](https://github.com/beskar-cloud/infra-config)).
On top of configured operating system vanilla kubernetes is installed (via [Kubespray](https://github.com/kubernetes-sigs/kubespray) and configuration persisted in [kubernetes-deployments repository](https://github.com/beskar-cloud/kubernetes-deployments)).
OpenStack components, monitoring, proxies, log shipping and alternatively ceph distributed storage is deployed into kubernetes via [Flux CD](https://fluxcd.io/).

![](/howtos/pictures/arch-overview-107.png)

Looking more in detail we distinguish three different types of cloud nodes:
 * controlplane nodes
 * compute nodes
 * storage nodes

As shown below all cloud services requiring high availability and resiliency are placed on 3 or 5 controlplane nodes. There are few necessary components on each compute nodes providing OpenStack IaaS services (software defined networking and server virtualization).

![](/howtos/pictures/arch-external-ceph-107.png)

Distributed (ceph) storage is used on one side as distributed storage for Kubernetes and also on other hand as backing storage for OpenStack components (Glance, Cinder, Libvirt, Swift/Rados Gateway). Distributed storage may be consumed from external service or could be part of cloud infrastructure as shows next picture.

![](/howtos/pictures/arch-internal-ceph-107.png)


Learn more about [Beskar cloud repositories](repositories.md).

## Used technologies
 * Kubernetes (Kubespray)
 * kube-vip
 * OpenStack
 * Prometheus monitoring (Prometheus, Pushgateway, various exporters, Alertmanager)
 * Grafana
 * Grafana Loki
 * Traefik / Nginx proxy
 * Oauth2-proxy
 * Rook-ceph
 * Flux CD
 * Weave gitops server

