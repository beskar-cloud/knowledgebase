# beskar-cloud repositories

This document describes beskar cloud repositories.

## Knowledgebase

[Knowledgebase](https://github.com/beskar-cloud/knowledgebase) repository comes with operation recipes (runbooks), how-to guides and team/community agreements.

## Hardware provisioning and/or Operating System installation/configuration

[Infra-config](https://github.com/beskar-cloud/infra-config) repository deals with following topics:
 * networking (bonding LACP, iptables, DNS, ipv6, /etc/hosts)
 * proxy apt packages from local repo
 * install needed tools
 * install ssh keys
 * miscellaneous (bash PS1, time syncing, PCI passthrough, ...)

## Kubernetes installation

Kubernetes cloud installation is done via [Kubespray](https://github.com/kubernetes-sigs/kubespray) repository and configuration is then kept declaratively in [kubernetes-deployments repository](https://github.com/beskar-cloud/kubernetes-deployments).

## OpenStack cloud deployment via Flux CD

Multiple repositories are used to deploy whole OpenStack cloud deployed on top of Kubernetes:
 * [openstack-helm](https://github.com/beskar-cloud/openstack-helm) is stabilized clone of [openstack/openstack-helm](https://github.com/openstack/openstack-helm).
 * [openstack-helm-infra](https://github.com/beskar-cloud/openstack-helm-infra) is stabilized clone of [openstack/openstack-helm-infra](https://github.com/openstack/openstack-helm-infra).
 * [custom-helm-charts](https://github.com/beskar-cloud/custom-helm-charts) comes with extra helm charts created to integrate various openstack-components.
 * [beskar-flux](https://github.com/beskar-cloud/beskar-flux) shows actual declarative OpenStack cloud deployment.
