# Beskar cloud installation guide

## 0. Preparations

### Get your code downstream

Beskar cloud comes with set of [public git repositories which are ready to be used](repositories.md).
Practically you still want to [mirror these repositories downstream](repositories.md) so you can:
* make your own adjustments
* improve availability of git repositories

We typically mirror Beskar cloud repositories in downstream repository system following way:
* Beskar cloud main branch is 1:1 mirrored to downstream repository of the same name
* Downstream repository has `downstream` branch which keeps custom downstream code
  * As custom downstream code gets tested, patches are pushed to upstream Beskar cloud `main` branch as PR/MR.
* Downstream repository gets a patch in `main` branch
* Downstream repository `downstream` branch gets rebased on `main` branch so they point to same state

### Install needed tools on your controlling node

Following tools are needed on node from where you are going to install the cloud:

* kubectl compatible version, https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
* flux cli, https://fluxcd.io/flux/installation/#install-the-flux-cli
* helm cli, https://helm.sh/docs/intro/install/
* mozilla sops, https://github.com/mozilla/sops/releases
* age, age.rpm / age.deb, https://github.com/FiloSottile/age/
* ansible (take version specified in Kubespray)

## 1. Get your cloud servers

Follow the [Beskar cloud server specification options](architecture.md#recommended-hw-specification) and prepare 3 nodes for controlplane and at least 2 compute nodes.

Ubuntu 22.04 LTS is recommended and the only tested operating system.

## 2. Configure your cloud servers

Prepare infra-config inventory file based on [the example](https://github.com/beskar-cloud/infra-config/blob/main/ansible_hosts_democluster).
Use infra-config repository to configure  your cloud server.

### Operating system upgrade

```sh
cd .../infra-config
# connection test
ansible-playbook --check -i ansible_hosts_democluster play_single_os_patch.yml -t update -l cln-14.priv.cld.democluster.dev -e patch_enabled=true
# 1st upgrade
ansible-playbook -i ansible_hosts_democluster play_single_os_patch.yml -t update -l cln-14.priv.cld.democluster.dev -e patch_enabled=true
# upgrade rest of the cluster
ansible-playbook -i ansible_hosts_democluster play_single_os_patch.yml -t update -l democluster_all -e patch_enabled=true
```

### Reboot cluster nodes (if needed)

```sh
cd .../infra-config
# reboot cluster (if needed)
ansible-playbook -i ansible_hosts_ostrava play_single_os_patch.yml -t reboot -l democluster_all -e patch_enabled=true
```

## 3. Install kubernetes

Once infra-config is executer your cluster nodes are prepared for kubernetes installation. We use [Kubespray](https://github.com/kubernetes-sigs/kubespray) to install kubernetes and [Kubernetes-deployments](https://github.com/beskar-cloud/kubernetes-deployments) repository for persisting kubernetes low-level configuration.

We recommend to use [one of the supported kubernetes releases](https://kubernetes.io/releases/) which has got at least 3 patch releases already.

Kubernetes installation steps are following:
* clone [Kubespray](https://github.com/kubernetes-sigs/kubespray)
* generate and modity your own kubernetes inventory (you can inspire [here](https://github.com/beskar-cloud/kubernetes-deployments/tree/main/deployments/ceph-lab/configuration/kubespray) what is typically changed)
* install kubespray needed tools and initiate kubernetes deployment
* store kubespray revision with inventory in [Kubernetes-deployments](https://github.com/beskar-cloud/kubernetes-deployments) repository for future
* test kubernetes is up and running
* add kubernetes cluster kubectl configuration so you can manage kubernetes remotely


### Kubernetes installation - example command set
```sh
podman run -it docker.io/library/almalinux:8
yum install git-core epel-release vim
yum install python39-pip
cd
git clone https://github.com/kubernetes-sigs/kubespray.git
cd kubespray
python3.9 -m pip install -r requirements.txt
echo $?
cp -r inventory/sample inventory/deployment
# 5 controlplane + 1 compute nodes
declare -a IPS=(10.7.0.{181,3,137,142,250,198})
CONFIG_FILE=inventory/deployment/hosts.yaml python3.9 contrib/inventory_builder/inventory.py ${IPS[@]}
vim inventory/deployment/hosts.yaml
vim inventory/deployment/group_vars/k8s_cluster/addons.yml
vim inventory/deployment/group_vars/k8s_cluster/k8s-cluster.yml
vim inventory/deployment/group_vars/k8s_cluster/kube-vip.yml
ansible-playbook -i inventory/deployment/hosts.yaml --user=ubuntu --become --become-user=root cluster.yml
```

Test of the kubernetes functionality
```sh
control $ ssh ubuntu@10.7.0.181
ubuntu@master1 $ sudo -i
ubuntu@master1 $ kubectl version

# dump kubernetes access configuration and import to your node
sed 's/127.0.0.1:6443/<internal/extrernal-ip>:6443/g' ~/.kube/config
```


## 4. Bootstrap cloud environment with Flux 2 CD and cloud GitOps repository

### Generate Flux CD encryption/decryption key

[Flux CD supports secret data management](https://fluxcd.io/flux/security/secrets-management/) and that's why we recommend to create deficated (per cloud environment) keypair as shown below.

```sh
age-keygen -o ~/.config/sops/age/freznicek-cluster-7-key.txt
[freznicek@lenovo-t14 .kube 0]$ cat ~/.config/sops/age/freznicek-cluster-7-key.txt
# public key: age1wnjcf74ckv0rqhfuzukj5gj67urunv4dylwxfnmz9amwepzycc2sr37mme
AGE-SECRET-KEY-1Q******************************************************4YJ
```

### Initiate cloud environment gitops repository (beskar-flux)

Push initial version of your gitops cloud environment consisting of following files:
* https://github.com/beskar-cloud/beskar-flux/blob/master/infrastructure/kustomization.yaml
* https://github.com/beskar-cloud/beskar-flux/tree/master/infrastructure/00-sources-and-namespaces
* https://github.com/beskar-cloud/beskar-flux/blob/master/clusters/g2-oidc/.sops.yaml (note public key has to match)
* https://github.com/beskar-cloud/beskar-flux/blob/master/clusters/g2-oidc/infrastructure.yaml


### Test remote kubernetes access with kubectl and flux command-line tools
```
[freznicek@lenovo-t14 commandline 0]$ kubectl version
Client Version: version.Info{Major:"1", Minor:"25", GitVersion:"v1.25.10", GitCommit:"e770bdbb87cccdc2daa790ecd69f40cf4df3cc9d", GitTreeState:"clean", BuildDate:"2023-05-17T14:12:20Z", GoVersion:"go1.19.9", Compiler:"gc", Platform:"linux/amd64"}
Kustomize Version: v4.5.7
Server Version: version.Info{Major:"1", Minor:"24", GitVersion:"v1.24.9", GitCommit:"9710807c82740b9799453677c977758becf0acbb", GitTreeState:"clean", BuildDate:"2022-12-08T10:08:06Z", GoVersion:"go1.18.9", Compiler:"gc", Platform:"linux/amd64"}
[freznicek@lenovo-t14 beskar-flux.git 1]$ flux check --pre
► checking prerequisites
✗ flux 0.36.0 <0.37.0 (new version is available, please upgrade)
✔ Kubernetes 1.24.9 >=1.20.6-0
✔ prerequisites checks passed
```


### Bootstrap Flux CD
```sh
# This lab cluster uses downstream gitops repository at gitlab.ics.muni.cz/cloud/g2/beskar-flux
flux bootstrap gitlab --hostname gitlab.ics.muni.cz --owner=cloud/g2 --repository=beskar-flux --branch downstream --path clusters/freznicek-cluster-7
#Please enter your GitLab personal access token (PAT):
flux check
```

### Install private decryption key

```sh
[freznicek@lenovo-t14 ~ 0]$ cat ~/.config/sops/age/freznicek-cluster-7-key.txt | kubectl create secret generic sops-age-key-freznicek-cluster-7 --namespace=flux-system --from-file=age.agekey=/dev/stdin
secret/sops-age-key-freznicek-cluster-7 created
```

### Test Flux CD functionality

```
[freznicek@lenovo-t14 beskar-flux.git 0]$ kubectl -n flux-system get all
NAME                                           READY   STATUS    RESTARTS   AGE
pod/helm-controller-89c567775-qbz9z            1/1     Running   0          3m28s
pod/kustomize-controller-6d9dcc4678-wjjdt      1/1     Running   0          3m25s
pod/notification-controller-5cb4cd7867-9xqjf   1/1     Running   0          3m27s
pod/source-controller-6849d5845f-9vdqh         1/1     Running   0          3m24s

NAME                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/notification-controller   ClusterIP   10.233.31.200   <none>        80/TCP    3m36s
service/source-controller         ClusterIP   10.233.61.119   <none>        80/TCP    3m34s
service/webhook-receiver          ClusterIP   10.233.62.153   <none>        80/TCP    3m32s

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/helm-controller           1/1     1            1           3m32s
deployment.apps/kustomize-controller      1/1     1            1           3m32s
deployment.apps/notification-controller   1/1     1            1           3m31s
deployment.apps/source-controller         1/1     1            1           3m30s

NAME                                                 DESIRED   CURRENT   READY   AGE
replicaset.apps/helm-controller-89c567775            1         1         1       3m32s
replicaset.apps/kustomize-controller-6d9dcc4678      1         1         1       3m31s
replicaset.apps/notification-controller-5cb4cd7867   1         1         1       3m30s
replicaset.apps/source-controller-6849d5845f         1         1         1       3m29s

[freznicek@lenovo-t14 beskar-flux.git 0]$ flux get ks
NAME            REVISION                SUSPENDED       READY   MESSAGE
flux-system     downstream/1f4cba1      False           True    Applied revision: downstream/1f4cba1
infrastructure  downstream/1f4cba1      False           False   Applied revision: downstream/1f4cba1
```

## 5. Install Openstack, monitoring and storage

Once Flux CD is bootstrapped then all the cloud maintenance tasks from kubernetes up is done via cloud gitops repository [beskar-flux](https://github.com/beskar-cloud/beskar-flux) changes (PR/MR). OpenStack cloud isdescribed in [beskar-flux's](https://github.com/beskar-cloud/beskar-flux) [/apps](https://github.com/beskar-cloud/beskar-flux/tree/master/apps) directory.


[beskar-flux](https://github.com/beskar-cloud/beskar-flux) repository shows two different cloud environments:
 * OpenStack with identities from LDAP, named as [shubham-cluster-1](https://github.com/beskar-cloud/beskar-flux/tree/master/clusters/shubham-cluster-1) cluster
 * OpenStack with identities from OIDC, named as [g2-oidc](https://github.com/beskar-cloud/beskar-flux/tree/master/clusters/g2-oidc) cluster


[Openstack-helm](https://github.com/beskar-cloud/openstack-helm) and [Openstack-helm-infra](https://github.com/beskar-cloud/openstack-helm-infra) helm charts expects kubernetes nodes to be properly labelled.

Node labels can be added different ways (sorted by preference):
 * GitOps repository ([patching of existing resources is supported](https://fluxcd.io/flux/faq/#how-to-patch-coredns-and-other-pre-installed-addons))
 * Kubespray cluster configuration
 * manual labelling

### Example of manual labelling (5+1 nodes)
```sh
# label kubernetes nodes
# common kubectl command (add --context=XYZ if needed)
KUBECTL="kubectl"
# control-plane labels
labels="ceph-rgw=enabled horizon=enabled openstack-control-plane-vnc=enabled openstack-control-plane=enabled openstack-mon-node=enabled openstack-mon=enabled openvswitch=enabled rook-ceph-operator=true rook-ceph-role=storage-node topology.kubernetes.io/zone=ostack-vm linuxbridge=enabled"
for i_node in node{1..2}; do
  for i_label in ${labels} topology.rook.io/rack=rack1; do
    $KUBECTL label no ${i_node} "${i_label}"
  done
done
for i_node in node{3..4}; do
  for i_label in ${labels} topology.rook.io/rack=rack2; do
    $KUBECTL label no ${i_node} "${i_label}"
  done
done
for i_node in node5; do
  for i_label in ${labels} topology.rook.io/rack=rack3; do
    $KUBECTL label no ${i_node} "${i_label}"
  done
done

# compute labels
labels="openstack-compute-node=enabled openvswitch=enabled rook-ceph-operator=true topology.kubernetes.io/zone=ostack-vm"
for i_node in node6; do
  for i_label in ${labels} topology.rook.io/rack=rack3; do
    $KUBECTL label no ${i_node} "${i_label}"
  done
done
```

