# OpenStack Designate Configuration with Bind9 and PowerDNS Integration to Neutron
OpenStack Designate is a multi-tenant DNS-as-a-Service (DNSaaS) solution designed for OpenStack. It provides a scalable and reliable way to manage DNS records and zones across different tenants. Designate integrates seamlessly with OpenStack projects like Neutron to enable dynamic DNS updates when new instances or networks are created. With support for various DNS backends such as Bind9 and PowerDNS, Designate offers flexibility in choosing the underlying DNS server technology.

This guide details the setup and configuration of OpenStack Designate with Bind9 and PowerDNS as backend DNS servers, along with their integration with Neutron. Follow the steps below to configure and test the setup in your OpenStack environment.

## Using Bind9 DNS Backend Server
Set up a server with BIND9 installed, either as part of a Kubernetes cluster or as an external server with access to all Kubernetes nodes.

1. **Install Bind9 package:**

    `apt-get install bind9 bind9utils bind9-doc`

2. **Generate rndc key and create rndc.conf:**

    `rndc-confgen -a -k rndc-key -c /etc/rndc.key`

    e.g `/etc/rndc.key`
    ```
    key "rndc-key" {
        algorithm hmac-sha256;
        secret "XUTO6iQhAZj8gUFL1OB63EyezIvT6bfjU7Z4o24J+nM=";
    };;
    ```

    e.g `/etc/rndc.conf`

    ```
    #include "/etc/rndc.key";
    options {
        default-key "rndc-key";
        default-server 192.168.101.63;
        default-port 953;
    };
    ```
3.	**Configure Bind9:**

    ```
    include "/etc/rndc.key";
    options {
        listen-on port 53 { 192.168.101.63; };
        directory "/var/lib/bind";
        allow-new-zones yes;
        dnssec-validation yes;
        auth-nxdomain no;
        request-ixfr no;
        recursion no;
        minimal-responses yes;
        allow-notify { 192.168.101.63; };
    };
    controls {
        inet 192.168.101.63 port 953 allow { 192.168.101.63; } keys { "rndc-key"; };
    };
    ```

4. **Fix file permissions:**
    ```
    chown root:bind /etc/rndc.key
    chmod 640 /etc/rndc.key
    chown root:bind /etc/rndc.conf
    chmod 640 /etc/rndc.conf
    ```

5. **Restart Bind9 service:**

    `systemctl restart bind9`


- ##  Integrate Bind9 with Designate

    - Modify `pools.yaml` and mount `rndc.key` and `rndc.conf` in `designate-worker` pod. [Here](https://github.com/beskar-cloud/openstack-helm/commit/3d38a56152120a99fcdf8bb3258a5151c94bc60f) is the commit with changes for mounting `rndc.key` and `rndc.conf` in the `deployment` and `configmap`.
    - Ensure the `designate-worker` pod runs on the same server as Bind9.
    - If you are using Flux for Kubernetes deployment management, use the [beskar-flux](https://github.com/beskar-cloud/beskar-flux) repo for the [Designate](https://github.com/beskar-cloud/beskar-flux/blob/master/apps/shubham-cluster-1/03-openstack/20-openstack-designate.yaml) flux template.

  **pools.yaml**
    ```
    conf:
      rndc_conf: |
        #include "/etc/rndc.key";
        options {
            default-key "rndc-key";
            default-server 192.168.101.63;
            default-port 953;
        };
      rndc_key: |
        key "rndc-key" {
            algorithm hmac-sha256;
            secret "XUTO6iQhAZj8gUFL1OB63EyezIvT6bfjU33ffsado24J+nM=";
        };
      pools: |
        - name: default
          description: Default Pool
          attributes: {}
          ns_records:
            - hostname: hemant-openstack-lab-1-26074-ctl-1.
              priority: 1
          nameservers:
            - host: 192.168.101.63
              port: 53
          targets:
            - type: bind9
              description: BIND9 Server 1
              masters:
                - host: 192.168.101.63 
                  port: 32572
              options:
                host: 192.168.101.63
                port: 53
                rndc_host: 192.168.101.63
                rndc_port: 953
                rndc_key_file: /etc/designate/rndc.key
    ```

- ## Testing Designate with Bind9 Integration

    - Once you have configured OpenStack Designate and deployed the necessary services, it's important to verify that all the Designate components are running correctly. OpenStack Designate includes several key services that need to be up and operational for proper DNS-as-a-Service functionality. You can use the `openstack dns service list` command to check the status of these services.
    
    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack dns service list
    +--------------------------------------+-------------------------------------+--------------+--------+-------+--------------+
    | id                                   | hostname                            | service_name | status | stats | capabilities |
    +--------------------------------------+-------------------------------------+--------------+--------+-------+--------------+
    | 85668d7c-dbc9-4762-a397-0c4dce9dbe11 | designate-api-55668b6cff-8cx4j      | api          | UP     | -     | -            |
    | 8d792416-db13-4445-87f1-2b6a216bbab4 | designate-producer-7bbd957f8-bwr24  | producer     | UP     | -     | -            |
    | bac599e6-816d-469c-b613-f454e440366a | designate-mdns-79f69c548-bhbh2      | mdns         | UP     | -     | -            |
    | f6e0d5b2-807a-499f-a12f-b9f6998a8286 | designate-central-75798b84bc-vtm2w  | central      | UP     | -     | -            |
    +--------------------------------------+-------------------------------------+--------------+--------+-------+--------------+
    ```
    - Use OpenStack CLI commands to create zones and recordsets, and verify DNS resolution.
    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack zone create --email dnsmaster@example.com example3.com.
    +----------------+--------------------------------------+
    | Field          | Value                                |
    +----------------+--------------------------------------+
    | action         | CREATE                               |
    | attributes     |                                      |
    | created_at     | 2024-05-28T10:18:24.000000           |
    | description    | None                                 |
    | email          | dnsmaster@example.com                |
    | id             | 95c7456f-648a-40a9-b55a-071c6a652c06 |
    | masters        |                                      |
    | name           | example3.com.                        |
    | pool_id        | 794ccc2c-d751-44fe-b57f-8894c9f5c842 |
    | project_id     | 7e27be1e438749fa94177c078ecd4bef     |
    | serial         | 1716891504                           |
    | status         | PENDING                              |
    | transferred_at | None                                 |
    | ttl            | 3600                                 |
    | type           | PRIMARY                              |
    | updated_at     | None                                 |
    | version        | 1                                    |
    +----------------+--------------------------------------+
    ```
    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack zone list
    +--------------------------------------+----------------+---------+------------+--------+--------+
    | id                                   | name           | type    |     serial | status | action |
    +--------------------------------------+----------------+---------+------------+--------+--------+
    | 95c7456f-648a-40a9-b55a-071c6a652c06 | example3.com. | PRIMARY | 1716891504 | ACTIVE  | NONE   |
    +--------------------------------------+----------------+---------+------------+--------+--------+
    ```
    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack recordset create --records '10.0.0.1' --type A example3.com. www
    +-------------+--------------------------------------+
    | Field       | Value                                |
    +-------------+--------------------------------------+
    | action      | CREATE                               |
    | created_at  | 2024-05-28T10:20:54.000000           |
    | description | None                                 |
    | id          | c43ef607-54a7-4564-b4e6-03f9bfbf209a |
    | name        | www.example3.com.                    |
    | project_id  | 7e27be1e438749fa94177c078ecd4bef     |
    | records     | 10.0.0.1                             |
    | status      | PENDING                              |
    | ttl         | None                                 |
    | type        | A                                    |
    | updated_at  | None                                 |
    | version     | 1                                    |
    | zone_id     | 95c7456f-648a-40a9-b55a-071c6a652c06 |
    | zone_name   | example3.com.                        |
    +-------------+--------------------------------------+
    ```
    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack recordset list 95c7456f-648a-40a9-b55a-071c6a652c06
    +--------------------------------------+-------------------+------+-------------------------------------------------------------------------------------------+--------+--------+
    | id                                   | name              | type | records                                                                                   | status | action |
    +--------------------------------------+-------------------+------+-------------------------------------------------------------------------------------------+--------+--------+
    | 051a6ac9-3197-4982-a81a-be515b729e00 | example3.com.     | NS   | hemant-openstack-lab-1-26074-ctl-1.                                                       | ACTIVE | NONE   |
    | edb4a64d-157b-465b-a317-ab793b789bfd | example3.com.     | SOA  | hemant-openstack-lab-1-26074-ctl-1. dnsmaster.example.com. 1716891654 3567 600 86400 3600 | ACTIVE | NONE   |
    | c43ef607-54a7-4564-b4e6-03f9bfbf209a | www.example3.com. | A    | 10.0.0.1                                                                                  | ACTIVE | NONE   |
    +--------------------------------------+-------------------+------+-------------------------------------------------------------------------------------------+--------+--------+
    ```
    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# dig @192.168.101.63 www.example3.com. +short
    10.0.0.1
    ```

Additionally, it is possible to create a Helm chart for Bind9 and deploy it using a Persistent Volume Claim (PVC) to store DNS data created using Designate. This approach allows for better persistence and scalability, especially when managing DNS records dynamically within a Kubernetes environment.

## Using PowerDNS Backend Server
Setting up Designate with PowerDNS as the backend DNS server is the most suitable approach. This method is outlined in detail, with detailed configuration steps and example logs, to provide a clear understanding of how it works.

PowerDNS, being a part of openstack-helm-infra, simplifies our setup by eliminating the need for separate storage solutions like PVCs. Instead, it uses a MariaDB database, which is more efficient and well-suited use case.

To get started, we will first deploy PowerDNS. The following sections will guide you through each step of the setup, ensuring a seamless integration with OpenStack Designate.

- ## **Deploy PowerDNS using [openstack-helm-infra/powerdns](https://github.com/beskar-cloud/openstack-helm-infra/tree/main/powerdns) chart:**
    - PowerDNS Configuration

    ```
    conf:
      powerdns:
        slave: true
        dnsupdate: true
        api: true
        api_key: CjNUbmaLHTnWwgtPxpJRhY
        cache_ttl: 0
        query_cache_ttl: 0
        negquery_cache_ttl: 0
        webserver: true
        webserver_address: 0.0.0.0
        webserver_allow_from: 0.0.0.0/0
        gmysql_dbname: powerdns
        gmysql_dnssec: yes
      mysql:
        client:
          database: powerdns
    ```
    - If you are using Flux for Kubernetes deployment management, use the [beskar-flux](https://github.com/beskar-cloud/beskar-flux) repo for the [PowerDNS](https://github.com/beskar-cloud/beskar-flux/blob/master/apps/shubham-cluster-1/03-openstack/19-openstack-powerdns.yaml) flux template.

    ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# kubectl get pods -n openstack | grep powerdn
    powerdns-c8dd96f8c-vnmpv                                1/1     Running     0             82d
    powerdns-db-init-6f24f                                  0/1     Completed   0             82d
    powerdns-db-sync-cspjl                                  0/1     Completed   0             82d
    ```

- ## **Integrate PowerDNS with Designate:**
    - Update `pools.yaml` in Designate to integrate PowerDNS as the backend DNS server.  

      ```
      pools: |
        - name: default
          description: Default Pool
          attributes: {}

          ns_records:
            - hostname: hemant-openstack-lab-1-26074-cmp-1.
              priority: 1

          nameservers:
            - host: 192.168.101.245      # IP of node where powerdns running
              port: 32392                # powerdns service nodePort

          targets:
            - type: pdns4
              description: PowerDNS 4

              masters:
                - host: 192.168.101.245  # IP of node where designate worker running
                  port: 32621            # designate minidns service nodePort

              options:
                host: 192.168.101.245    # IP of node where powerdns running
                port: 32392              # powerdns service nodePort
                api_endpoint: http://powerdns.openstack.svc.cluster.local:8081
                api_token: CjNUbmaLHTnWwgtPxpJRhY   # make sure you use same token as setup in powerdns config
      ```

- ## Testing Designate with Bind9 Integration
    - Once you have configured OpenStack Designate and deployed the necessary services, it's important to verify that all the Designate components are running correctly. OpenStack Designate includes several key services that need to be up and operational for proper DNS-as-a-Service functionality. You can use the `openstack dns service list` command to check the status of these services.

      ```
        root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack dns service list
        +--------------------------------------+-------------------------------------+--------------+--------+-------+--------------+
        | id                                   | hostname                            | service_name | status | stats | capabilities |
        +--------------------------------------+-------------------------------------+--------------+--------+-------+--------------+
        | c543d8c0-81ed-43aa-8f70-a6ffab9f7f0d | designate-api-6bcd876649-hvg2v      | api          | UP     | -     | -            |
        | 7da76f8e-bc72-49ac-9fa5-76e8727dff1d | designate-central-5b5c659bff-tqhtl  | central      | UP     | -     | -            |
        | 60df317b-934d-49af-84bc-78cdd5259a4c | designate-mdns-649459978d-lgzfv     | mdns         | UP     | -     | -            |
        | c1d1af40-0c4f-4468-889b-37ce04c6430b | designate-producer-64cfc6cc98-mxx5c | producer     | UP     | -     | -            |
        +--------------------------------------+-------------------------------------+--------------+--------+-------+--------------+
    - Use OpenStack CLI commands to create zones and recordsets, and verify DNS resolution.

      ```
        root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack zone create example.org. --email mail@example.org

        +----------------+--------------------------------------+
        | Field          | Value                                |
        +----------------+--------------------------------------+
        | action         | NONE                                 |
        | attributes     |                                      |
        | created_at     | 2024-06-17T13:04:05.000000           |
        | description    | None                                 |
        | email          | mail@example.org                     |
        | id             | 3e10776b-ec96-479a-92dc-d4c8e0b4892a |
        | masters        |                                      |
        | name           | example.org.                         |
        | pool_id        | 794ccc2c-d751-44fe-b57f-8894c9f5c842 |
        | project_id     | 7e27be1e438749fa94177c078ecd4bef     |
        | serial         | 1718630156                           |
        | status         | ACTIVE                               |
        | transferred_at | None                                 |
        | ttl            | 3600                                 |
        | type           | PRIMARY                              |
        | updated_at     | 2024-06-17T13:16:01.000000           |
        | version        | 22                                   |
        +----------------+--------------------------------------+
      ```
      ```
        root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack zone list
        +--------------------------------------+----------------+---------+------------+--------+--------+
        | id                                   | name           | type    |     serial | status | action |
        +--------------------------------------+----------------+---------+------------+--------+--------+
        | 3e10776b-ec96-479a-92dc-d4c8e0b4892a | example.org.   | PRIMARY | 1718630156 | ACTIVE | NONE   |
        +--------------------------------------+----------------+---------+------------+--------+--------+
      ```
    - Once zone is created it should be in ACTIVE status and you will be able to see following logs in powerdns pods

      ```
      Jun 17 13:15:15 Initiating transfer of 'example.org' from remote '192.168.101.245:32621'
      Jun 17 13:15:15 AXFR started for 'example.org'
      Jun 17 13:15:15 Backend transaction started for 'example.org' storage
      Jun 17 13:15:15 AXFR done for 'example.org', zone committed with serial number 1718630115
      Jun 17 13:15:56 Initiating transfer of 'example.org' from remote '192.168.101.245:32621'
      Jun 17 13:15:56 AXFR started for 'example.org'
      Jun 17 13:15:56 Backend transaction started for 'example.org' storage
      Jun 17 13:15:56 AXFR done for 'example.org', zone committed with serial number 1718630156
      ```
    - Additionally, you should see the following logs in the Designate pods:
      ```
      2024-06-17 13:04:05.396 7 INFO designate.worker.tasks.zone [None req-647da0cb-9f7a-4201-9f2e-b99bbf1669c9 - - - all - -] Attempting to CREATE zone_name=example.org. zone_id=3e10776b-ec96-479a-92dc-d4c8e0b4892a
      ```
    - We have our zone ACTIVE and ready lets create recordset in example.org. zone
      ```
      root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack recordset create --type A --record 192.168.0.125  example.org. www.taikun
      +-------------+--------------------------------------+
      | Field       | Value                                |
      +-------------+--------------------------------------+
      | action      | CREATE                               |
      | created_at  | 2024-06-20T08:41:57.000000           |
      | description | None                                 |
      | id          | 4ddcb176-96ca-433b-8fbb-779bab03173d |
      | name        | www.taikun.example.org.              |
      | project_id  | 7e27be1e438749fa94177c078ecd4bef     |
      | records     | 192.168.0.125                        |
      | status      | PENDING                              |
      | ttl         | None                                 |
      | type        | A                                    |
      | updated_at  | None                                 |
      | version     | 1                                    |
      | zone_id     | 3e10776b-ec96-479a-92dc-d4c8e0b4892a |
      | zone_name   | example.org.                         |
      +-------------+--------------------------------------+
      ```
      ```
      root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack recordset list  3e10776b-ec96-479a-92dc-d4c8e0b4892a
      +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
      | id                                   | name                    | type | records                                                                              | status | action |
      +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
      | 0685cf80-151b-443d-b44c-e125e9ab2907 | example.org.            | SOA  | hemant-openstack-lab-1-26074-cmp-1. mail.example.org. 1718872917 3562 600 86400 3600 | ACTIVE | NONE   |
      | b9d3b2cf-d448-4d8a-a3fe-635bcc3e2c23 | example.org.            | NS   | hemant-openstack-lab-1-26074-cmp-1.                                                  | ACTIVE | NONE   |
      | 4ddcb176-96ca-433b-8fbb-779bab03173d | www.taikun.example.org. | A    | 192.168.0.125                                                                        | ACTIVE | NONE   |
      +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
      ```
    - After creation Designate and PowerDNS logs are as follows

        - Designate Logs:
      ```
      2024-06-20 08:41:57.579 7 INFO designate.worker.tasks.zone [None req-3cbeff83-34e7-48c5-90b5-68dc89c3218d 8d7ebbc875b147c6a743a2761354afc0 7e27be1e438749fa94177c078ecd4bef - - - -] Attempting to UPDATE zone_name=example.org. zone_id=3e10776b-ec96-479a-92dc-d4c8e0b4892a
      ```
        - PowerDNS Logs:
      ```
      powerdns-c8dd96f8c-vnmpv powerdns Jun 20 08:41:58 Initiating transfer of 'example.org' from remote '192.168.101.245:32621'
      powerdns-c8dd96f8c-vnmpv powerdns Jun 20 08:41:58 AXFR started for 'example.org'
      powerdns-c8dd96f8c-vnmpv powerdns Jun 20 08:41:58 Backend transaction started for 'example.org' storage
      powerdns-c8dd96f8c-vnmpv powerdns Jun 20 08:41:58 AXFR done for 'example.org', zone committed with serial number 17188729
      ```
    
    - Verify DNS resolution with PowerDNS

      ```
      root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack recordset list  3e10776b-ec96-479a-92dc-d4c8e0b4892a
      +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
      | id                                   | name                    | type | records                                                                              | status | action |
      +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
      | 0685cf80-151b-443d-b44c-e125e9ab2907 | example.org.            | SOA  | hemant-openstack-lab-1-26074-cmp-1. mail.example.org. 1718872917 3562 600 86400 3600 | ACTIVE | NONE   |
      | b9d3b2cf-d448-4d8a-a3fe-635bcc3e2c23 | example.org.            | NS   | hemant-openstack-lab-1-26074-cmp-1.                                                  | ACTIVE | NONE   |
      | 4ddcb176-96ca-433b-8fbb-779bab03173d | www.taikun.example.org. | A    | 192.168.0.125                                                                        | ACTIVE | NONE   |
      +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
      ```
      ```
      root@hemant-openstack-lab-1-26074-master:/home/hemant# kubectl get svc -n openstack | grep power
      powerdns                      LoadBalancer   10.233.55.82    77.78.90.15   53:32392/UDP,53:32392/TCP,8081:30981/TCP   25d
      ```
      ```
      root@hemant-openstack-lab-1-26074-master:/home/hemant# dig @10.233.55.82 www.taikun.example.org.
      ; <<>> DiG 9.18.12-0ubuntu0.22.04.1-Ubuntu <<>> @10.233.55.82 www.taikun.example.org.
      ; (1 server found)
      ;; global options: +cmd
      ;; Got answer:
      ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 43833
      ;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
      ;; WARNING: recursion requested but not available
      
      ;; OPT PSEUDOSECTION:
      ; EDNS: version: 0, flags:; udp: 1232
      ;; QUESTION SECTION:
      ;www.taikun.example.org. IN A
      
      ;; ANSWER SECTION:
      www.taikun.example.org. 3600 IN A 192.168.0.125
      
      ;; Query time: 24 msec
      ;; SERVER: 10.233.55.82#53(10.233.55.82) (UDP)
      ;; WHEN: Tue Jul 02 06:42:54 UTC 2024
      ;; MSG SIZE rcvd: 67
      ```
    - Tested by exposing powerdns service as loadbalancer and using loadbalancer public IP it is successfully allowed DNS recordsets to be resolved from any location.
      ```
      dig @77.78.90.15 www.taikun.example.org. 
      ; <<>> DiG 9.10.6 <<>> @77.78.90.15 www.taikun.example.org.
      ; (1 server found)
      ;; global options: +cmd
      ;; Got answer:
      ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 13643
      ;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
      ;; WARNING: recursion requested but not available
      
      ;; OPT PSEUDOSECTION:
      ; EDNS: version: 0, flags:; udp: 1232
      ;; QUESTION SECTION:
      ;www.taikun.example.org. IN A
      
      ;; ANSWER SECTION:
      www.taikun.example.org. 3600 IN A 192.168.0.125
      
      ;; Query time: 40 msec
      ;; SERVER: 77.78.90.15#53(77.78.90.15)
      ;; WHEN: Tue Jul 02 08:44:53 CEST 2024
      ;; MSG SIZE rcvd: 67
      ```
We've observed that PowerDNS and Designate works well together. Now, let's explore integrating them with Neutron to use their capabilities with networks, ports, and virtual machines (VMs).


## Neutron Integration
Neutron can be integrated with Designate to provide automatic recordset creation for ports and, by proxy, Nova server instances. The following configurations and tests describes DNS management by generating and updating DNS recordsets whenever new instances or ports are created, ensuring accurate and up-to-date DNS information across your cloud environment.

- Create and Configure DNS Domain in Neutron
  - create zone in designate:
  ```
    openstack zone create --email dnsmaster@example.com example.org.

    +----------------+--------------------------------------+
    | Field          | Value                                |
    +----------------+--------------------------------------+
    | action         | CREATE                               |
    | attributes     |                                      |
    | created_at     | 2024-06-17T13:04:05.000000           |
    | description    | None                                 |
    | email          | dnsmaster@example.org                |
    | id             | 3e10776b-ec96-479a-92dc-d4c8e0b4892a |
    | masters        |                                      |
    | name           | example.org.                         |
    | pool_id        | 794ccc2c-d751-44fe-b57f-8894c9f5c842 |
    | project_id     | 7e27be1e438749fa94177c078ecd4bef     |
    | serial         | 1718872917                           |
    | status         | PENDING                              |
    | transferred_at | None                                 |
    | ttl            | 3600                                 |
    | type           | PRIMARY                              |
    | updated_at     | None                                 |
    | version        | 1                                    |
    +----------------+--------------------------------------+
  ```

  ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack zone list
    +--------------------------------------+----------------+---------+------------+--------+--------+
    | id                                   | name           | type    |     serial | status | action |
    +--------------------------------------+----------------+---------+------------+--------+--------+
    | 3e10776b-ec96-479a-92dc-d4c8e0b4892a | example.org.   | PRIMARY | 1718872917 | ACTIVE | NONE   |
    +--------------------------------------+----------------+---------+------------+--------+--------+
  ```
- Use created zone in following neutron configuration 

  ```
    conf:
      neutron:
        designate:
          url: http://designate-api.openstack.svc.cluster.local:9001/v2
          auth_type: password
          auth_url: http://keystone-api.openstack.svc.cluster.local:5000
          username: designate
          password: <designate_password>
          project_name: service
          project_domain_name: service
          user_domain_name: service
          allow_reverse_dns_lookup: True
          ipv4_ptr_zone_prefix_size: 24
          ipv6_ptr_zone_prefix_size: 116
          ptr_zone_email: admin@example.org
        DEFAULT:
          #l3_ha: True
          # Use domain name of zone created 
          dns_domain: example.org. 
          external_dns_driver: designate
      plugins:
        ml2_conf:
          ml2:
            extension_drivers: port_security,dns_domain_ports
  ```
- Create and Manage Ports with DNS
  ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack network list
    +--------------------------------------+----------------------------------------------------+--------------------------------------+
    | ID                                   | Name                                               | Subnets                              |
    +--------------------------------------+----------------------------------------------------+--------------------------------------+
    | 83c07ac7-32e0-41f0-9a7d-20411aec6c83 | HA network tenant 7e27be1e438749fa94177c078ecd4bef | 24933352-e943-40cc-b9f0-df09eaa1d7ee |
    | b1b5be89-12b4-4c5d-b626-7b56584648b4 | fip                                                | 982ca829-097b-44df-b3b1-c27bbe2d3ccf |
    | edcfcacc-ef93-4f13-ae42-f9d76b576da6 | itera-net                                          | 102c0faa-81aa-4987-8ff7-7989d59fe538 |
    | f3aef839-5008-4103-ba23-7d0966f5a335 | taikun-net                                         | 73f43b77-d4da-4059-b32c-08483dcafff9 |
    +--------------------------------------+----------------------------------------------------+--------------------------------------+
  ```
  ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack  port create --network f3aef839-5008-4103-ba23-7d0966f5a335  --dns-domain example.org. --dns-name my-dns-port dns-port
    +-------------------------+-------------------------------------------------------------------------------------+
    | Field                   | Value                                                                               |
    +-------------------------+-------------------------------------------------------------------------------------+
    | admin_state_up          | UP                                                                                  |
    | allowed_address_pairs   |                                                                                     |
    | binding_host_id         |                                                                                     |
    | binding_profile         |                                                                                     |
    | binding_vif_details     |                                                                                     |
    | binding_vif_type        | unbound                                                                             |
    | binding_vnic_type       | normal                                                                              |
    | created_at              | 2024-07-02T09:23:59Z                                                                |
    | data_plane_status       | None                                                                                |
    | description             |                                                                                     |
    | device_id               |                                                                                     |
    | device_owner            |                                                                                     |
    | device_profile          | None                                                                                |
    | dns_assignment          | fqdn='my-dns-port.example.org.', hostname='my-dns-port', ip_address='100.0.100.166' |
    | dns_domain              | example.org.                                                                        |
    | dns_name                | my-dns-port                                                                         |
    | extra_dhcp_opts         |                                                                                     |
    | fixed_ips               | ip_address='100.0.100.166', subnet_id='73f43b77-d4da-4059-b32c-08483dcafff9'        |
    | id                      | 56e17cad-03bb-4595-affa-0d8bde8b6044                                                |
    | ip_allocation           | None                                                                                |
    | mac_address             | fa:16:3e:3a:cf:98                                                                   |
    | name                    | dns-port                                                                            |
    | network_id              | f3aef839-5008-4103-ba23-7d0966f5a335                                                |
    | numa_affinity_policy    | None                                                                                |
    | port_security_enabled   | True                                                                                |
    | project_id              | 7e27be1e438749fa94177c078ecd4bef                                                    |
    | propagate_uplink_status | None                                                                                |
    | qos_network_policy_id   | None                                                                                |
    | qos_policy_id           | None                                                                                |
    | resource_request        | None                                                                                |
    | revision_number         | 1                                                                                   |
    | security_group_ids      | 5a911fef-f86a-4f11-86b1-8d16f5f6a217                                                |
    | status                  | DOWN                                                                                |
    | tags                    |                                                                                     |
    | trunk_details           | None                                                                                |
    | updated_at              | 2024-07-02T09:24:00Z                                                                |
    +-------------------------+-------------------------------------------------------------------------------------+
  ```
- Create and Manage Instances with DNS

  ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack  server create --flavor m1.small --image fd4df95d-e1d8-4ac9-8e9a-4c9a45f8e35b --nic net-id=f3aef839-5008-4103-ba23-7d0966f5a335 dns-test
    +-------------------------------------+------------------------------------------------------------+
    | Field                               | Value                                                      |
    +-------------------------------------+------------------------------------------------------------+
    | OS-DCF:diskConfig                   | MANUAL                                                     |
    | OS-EXT-AZ:availability_zone         |                                                            |
    | OS-EXT-SRV-ATTR:host                | None                                                       |
    | OS-EXT-SRV-ATTR:hypervisor_hostname | None                                                       |
    | OS-EXT-SRV-ATTR:instance_name       |                                                            |
    | OS-EXT-STS:power_state              | NOSTATE                                                    |
    | OS-EXT-STS:task_state               | scheduling                                                 |
    | OS-EXT-STS:vm_state                 | building                                                   |
    | OS-SRV-USG:launched_at              | None                                                       |
    | OS-SRV-USG:terminated_at            | None                                                       |
    | accessIPv4                          |                                                            |
    | accessIPv6                          |                                                            |
    | addresses                           |                                                            |
    | adminPass                           | AR3UnWwJ6hSP                                               |
    | config_drive                        |                                                            |
    | created                             | 2024-07-02T11:12:42Z                                       |
    | flavor                              | m1.small (7c276679-1c36-4781-988a-4a7e81bc71fa)            |
    | hostId                              |                                                            |
    | id                                  | 1cc91b35-2529-45ca-8a86-e0ee596345a8                       |
    | image                               | Cirros 0.3.5 64-bit (fd4df95d-e1d8-4ac9-8e9a-4c9a45f8e35b) |
    | key_name                            | None                                                       |
    | name                                | dns-test                                                   |
    | progress                            | 0                                                          |
    | project_id                          | 7e27be1e438749fa94177c078ecd4bef                           |
    | properties                          |                                                            |
    | security_groups                     | name='default'                                             |
    | status                              | BUILD                                                      |
    | updated                             | 2024-07-02T11:12:42Z                                       |
    | user_id                             | 8d7ebbc875b147c6a743a2761354afc0                           |
    | volumes_attached                    |                                                            |
    +-------------------------------------+------------------------------------------------------------+
  ```
  ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack port list --server dns-test
    +--------------------------------------+------+-------------------+-----------------------------------------------------------------------------+--------+
    | ID                                   | Name | MAC Address       | Fixed IP Addresses                                                          | Status |
    +--------------------------------------+------+-------------------+-----------------------------------------------------------------------------+--------+
    | f0542c90-4874-4d20-899b-39f384be12c5 |      | fa:16:3e:72:2e:25 | ip_address='100.0.100.27', subnet_id='73f43b77-d4da-4059-b32c-08483dcafff9' | ACTIVE |
    +--------------------------------------+------+-------------------+-----------------------------------------------------------------------------+--------+
  ```
  ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack port show f0542c90-4874-4d20-899b-39f384be12c5
    +-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
    | Field                   | Value                                                                                                                                      |
    +-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
    | admin_state_up          | UP                                                                                                                                         |
    | allowed_address_pairs   |                                                                                                                                            |
    | binding_host_id         | hemant-openstack-lab-1-26074-cmp-2.cluster.local                                                                                           |
    | binding_profile         |                                                                                                                                            |
    | binding_vif_details     | bound_drivers.0='openvswitch', bridge_name='br-int', connectivity='l2', datapath_type='system', ovs_hybrid_plug='True', port_filter='True' |
    | binding_vif_type        | ovs                                                                                                                                        |
    | binding_vnic_type       | normal                                                                                                                                     |
    | created_at              | 2024-07-02T11:12:43Z                                                                                                                       |
    | data_plane_status       | None                                                                                                                                       |
    | description             |                                                                                                                                            |
    | device_id               | 1cc91b35-2529-45ca-8a86-e0ee596345a8                                                                                                       |
    | device_owner            | compute:nova                                                                                                                               |
    | device_profile          | None                                                                                                                                       |
    | dns_assignment          | fqdn='dns-test.example.org.', hostname='dns-test', ip_address='100.0.100.27'                                                               |
    | dns_domain              |                                                                                                                                            |
    | dns_name                | dns-test                                                                                                                                   |
    | extra_dhcp_opts         |                                                                                                                                            |
    | fixed_ips               | ip_address='100.0.100.27', subnet_id='73f43b77-d4da-4059-b32c-08483dcafff9'                                                                |
    | id                      | f0542c90-4874-4d20-899b-39f384be12c5                                                                                                       |
    | ip_allocation           | None                                                                                                                                       |
    | mac_address             | fa:16:3e:72:2e:25                                                                                                                          |
    | name                    |                                                                                                                                            |
    | network_id              | f3aef839-5008-4103-ba23-7d0966f5a335                                                                                                       |
    | numa_affinity_policy    | None                                                                                                                                       |
    | port_security_enabled   | True                                                                                                                                       |
    | project_id              | 7e27be1e438749fa94177c078ecd4bef                                                                                                           |
    | propagate_uplink_status | None                                                                                                                                       |
    | qos_network_policy_id   | None                                                                                                                                       |
    | qos_policy_id           | None                                                                                                                                       |
    | resource_request        | None                                                                                                                                       |
    | revision_number         | 4                                                                                                                                          |
    | security_group_ids      | 5a911fef-f86a-4f11-86b1-8d16f5f6a217                                                                                                       |
    | status                  | ACTIVE                                                                                                                                     |
    | tags                    |                                                                                                                                            |
    | trunk_details           | None                                                                                                                                       |
    | updated_at              | 2024-07-02T11:12:46Z                                                                                                                       |
    +-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
  ```
- Verify that the newly created VM automatically uses the specified `dns_domain` from the Neutron configuration
  ```
    root@hemant-openstack-lab-1-26074-cmp-2:/home/hemant# virsh console instance-00000072
    Connected to domain 'instance-00000072'
    Escape character is ^] (Ctrl + ])

    dns-test login: cirros
    Password:
    $ cat /etc/resolv.conf
    search example.org
  ```
  ### Designate As External DNS Service (DNSaaS)
   To use Designate as an external DNS service, both internal and external DNS configurations need to be set up in the Neutron configuration. Use similar configuration as mentioned in Neutron Integration as we have alredy setup `external_dns_driver: designate` paramerter in the configuration. For more info follow official OpenStack documentation [DNS Integration with an External Service](https://docs.openstack.org/neutron/latest/admin/config-dns-int-ext-serv.html)

   When configuring Neutron, ensure that the `dns_domain` attribute in the configuration file (e.g., `dns_domain: example.org.`) and the `--dns-domain` property when setting an OpenStack network (e.g., `--dns-domain example.org`.) are both assigned a valid domain name that ends with a dot (.).”

  - Lets test the DNSaaS:

   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack network list
   +--------------------------------------+----------------------------------------------------+--------------------------------------+
   | ID                                   | Name                                               | Subnets                              |
   +--------------------------------------+----------------------------------------------------+--------------------------------------+
   | 83c07ac7-32e0-41f0-9a7d-20411aec6c83 | HA network tenant 7e27be1e438749fa94177c078ecd4bef | 24933352-e943-40cc-b9f0-df09eaa1d7ee |
   | b1b5be89-12b4-4c5d-b626-7b56584648b4 | fip                                                | 982ca829-097b-44df-b3b1-c27bbe2d3ccf |
   | edcfcacc-ef93-4f13-ae42-f9d76b576da6 | itera-net                                          | 102c0faa-81aa-4987-8ff7-7989d59fe538 |
   | f3aef839-5008-4103-ba23-7d0966f5a335 | taikun-net                                         | 73f43b77-d4da-4059-b32c-08483dcafff9 |
   +--------------------------------------+----------------------------------------------------+--------------------------------------+
   ```
   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack network set --dns-domain example.org. edcfcacc-ef93-4f13-ae42-f9d76b576da6
   ```
   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack network show edcfcacc-ef93-4f13-ae42-f9d76b576da6
   +---------------------------+--------------------------------------+
   | Field                     | Value                                |
   +---------------------------+--------------------------------------+
   | admin_state_up            | UP                                   |
   | availability_zone_hints   | nova                                 |
   | availability_zones        | nova                                 |
   | created_at                | 2024-05-22T08:41:34Z                 |
   | description               |                                      |
   | dns_domain                | example.org.                         |
   | id                        | edcfcacc-ef93-4f13-ae42-f9d76b576da6 |
   | ipv4_address_scope        | None                                 |
   | ipv6_address_scope        | None                                 |
   | is_default                | None                                 |
   | is_vlan_transparent       | None                                 |
   | mtu                       | 8950                                 |
   | name                      | itera-net                            |
   | port_security_enabled     | True                                 |
   | project_id                | 7e27be1e438749fa94177c078ecd4bef     |
   | provider:network_type     | vxlan                                |
   | provider:physical_network | None                                 |
   | provider:segmentation_id  | 717                                  |
   | qos_policy_id             | None                                 |
   | revision_number           | 15                                   |
   | router:external           | Internal                             |
   | segments                  | None                                 |
   | shared                    | False                                |
   | status                    | ACTIVE                               |
   | subnets                   | 102c0faa-81aa-4987-8ff7-7989d59fe538 |
   | tags                      |                                      |
   | updated_at                | 2024-06-13T13:06:20Z                 |
   +---------------------------+--------------------------------------+
   ```
    - Create Instance and attached floatingIP to it

   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack server create --flavor m1.small --image fd4df95d-e1d8-4ac9-8e9a-4c9a45f8e35b --nic net-id=edcfcacc-ef93-4f13-ae42-f9d76b576da6 taikun
   +-------------------------------------+------------------------------------------------------------+
   | Field                               | Value                                                      |
   +-------------------------------------+------------------------------------------------------------+
   | OS-DCF:diskConfig                   | MANUAL                                                     |
   | OS-EXT-AZ:availability_zone         |                                                            |
   | OS-EXT-SRV-ATTR:host                | None                                                       |
   | OS-EXT-SRV-ATTR:hypervisor_hostname | None                                                       |
   | OS-EXT-SRV-ATTR:instance_name       |                                                            |
   | OS-EXT-STS:power_state              | NOSTATE                                                    |
   | OS-EXT-STS:task_state               | scheduling                                                 |
   | OS-EXT-STS:vm_state                 | building                                                   |
   | OS-SRV-USG:launched_at              | None                                                       |
   | OS-SRV-USG:terminated_at            | None                                                       |
   | accessIPv4                          |                                                            |
   | accessIPv6                          |                                                            |
   | addresses                           |                                                            |
   | adminPass                           | 7DbKbF9QTRbq                                               |
   | config_drive                        |                                                            |
   | created                             | 2024-07-02T12:28:50Z                                       |
   | flavor                              | m1.small (7c276679-1c36-4781-988a-4a7e81bc71fa)            |
   | hostId                              |                                                            |
   | id                                  | 67388836-587f-4ff2-96b7-a931ab58e66e                       |
   | image                               | Cirros 0.3.5 64-bit (fd4df95d-e1d8-4ac9-8e9a-4c9a45f8e35b) |
   | key_name                            | None                                                       |
   | name                                | taikun                                                     |
   | progress                            | 0                                                          |
   | project_id                          | 7e27be1e438749fa94177c078ecd4bef                           |
   | properties                          |                                                            |
   | security_groups                     | name='default'                                             |
   | status                              | BUILD                                                      |
   | updated                             | 2024-07-02T12:28:50Z                                       |
   | user_id                             | 8d7ebbc875b147c6a743a2761354afc0                           |
   | volumes_attached                    |                                                            |
   +-------------------------------------+------------------------------------------------------------+
   ``` 
   ```    
   root@hemant-openstack-lab-1-26074-master:/home/hemant#  openstack  port list --server taikun
   +--------------------------------------+------+-------------------+------------------------------------------------------------------------------+--------+
   | ID                                   | Name | MAC Address       | Fixed IP Addresses                                                           | Status |
   +--------------------------------------+------+-------------------+------------------------------------------------------------------------------+--------+
   | e9835023-bf15-4868-8b63-8ca3b66fd493 |      | fa:16:3e:6b:d8:3b | ip_address='200.0.200.167', subnet_id='102c0faa-81aa-4987-8ff7-7989d59fe538' | ACTIVE |
   +--------------------------------------+------+-------------------+------------------------------------------------------------------------------+--------+    
   ```
   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack port show e9835023-bf15-4868-8b63-8ca3b66fd493
   +-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
   | Field                   | Value                                                                                                                                      |
   +-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
   | admin_state_up          | UP                                                                                                                                         |
   | allowed_address_pairs   |                                                                                                                                            |
   | binding_host_id         | hemant-openstack-lab-1-26074-cmp-1.cluster.local                                                                                           |
   | binding_profile         |                                                                                                                                            |
   | binding_vif_details     | bound_drivers.0='openvswitch', bridge_name='br-int', connectivity='l2', datapath_type='system', ovs_hybrid_plug='True', port_filter='True' |
   | binding_vif_type        | ovs                                                                                                                                        |
   | binding_vnic_type       | normal                                                                                                                                     |
   | created_at              | 2024-07-02T12:28:51Z                                                                                                                       |
   | data_plane_status       | None                                                                                                                                       |
   | description             |                                                                                                                                            |
   | device_id               | 67388836-587f-4ff2-96b7-a931ab58e66e                                                                                                       |
   | device_owner            | compute:nova                                                                                                                               |
   | device_profile          | None                                                                                                                                       |
   | dns_assignment          | fqdn='taikun.example.org.', hostname='taikun', ip_address='200.0.200.167'                                                                  |
   | dns_domain              |                                                                                                                                            |
   | dns_name                | taikun                                                                                                                                     |
   | extra_dhcp_opts         |                                                                                                                                            |
   | fixed_ips               | ip_address='200.0.200.167', subnet_id='102c0faa-81aa-4987-8ff7-7989d59fe538'                                                               |
   | id                      | e9835023-bf15-4868-8b63-8ca3b66fd493                                                                                                       |
   | ip_allocation           | None                                                                                                                                       |
   | mac_address             | fa:16:3e:6b:d8:3b                                                                                                                          |
   | name                    |                                                                                                                                            |
   | network_id              | edcfcacc-ef93-4f13-ae42-f9d76b576da6                                                                                                       |
   | numa_affinity_policy    | None                                                                                                                                       |
   | port_security_enabled   | True                                                                                                                                       |
   | project_id              | 7e27be1e438749fa94177c078ecd4bef                                                                                                           |
   | propagate_uplink_status | None                                                                                                                                       |
   | qos_network_policy_id   | None                                                                                                                                       |
   | qos_policy_id           | None                                                                                                                                       |
   | resource_request        | None                                                                                                                                       |
   | revision_number         | 5                                                                                                                                          |
   | security_group_ids      | 5a911fef-f86a-4f11-86b1-8d16f5f6a217                                                                                                       |
   | status                  | ACTIVE                                                                                                                                     |
   | tags                    |                                                                                                                                            |
   | trunk_details           | None                                                                                                                                       |
   | updated_at              | 2024-07-02T12:28:53Z                                                                                                                       |
   +-------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
   ```
   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack floating ip create b1b5be89-12b4-4c5d-b626-7b56584648b4 --port e9835023-bf15-4868-8b63-8ca3b66fd493
   +---------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | Field               | values                                                                                                                                                  |
   +---------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   | created_at          | 2024-07-02T12:31:12Z                                                                                                                                    |
   | description         |                                                                                                                                                         |
   | dns_domain          |                                                                                                                                                         |
   | dns_name            |                                                                                                                                                         |
   | fixed_ip_address    | 200.0.200.167                                                                                                                                           |
   | floating_ip_address | 192.168.0.36                                                                                                                                            |
   | floating_network_id | b1b5be89-12b4-4c5d-b626-7b56584648b4                                                                                                                    |
   | id                  | 0abcf913-d712-4815-adf6-fad0c677bc37                                                                                                                    |
   | name                | 192.168.0.36                                                                                                                                            |
   | port_details        | {'name': '', 'network_id': 'edcfcacc-ef93-4f13-ae42-f9d76b576da6', 'mac_address': 'fa:16:3e:6b:d8:3b', 'admin_state_up': True, 'status': 'ACTIVE', 
                           'device_id':'67388836-587f-4ff2-96b7-a931ab58e66e', 'device_owner': 'compute:nova'}                                                                     |
   | port_id             | e9835023-bf15-4868-8b63-8ca3b66fd493                                                                                                                    |
   | project_id          | 7e27be1e438749fa94177c078ecd4bef                                                                                                                        |
   | qos_policy_id       | None                                                                                                                                                    |
   | revision_number     | 1                                                                                                                                                       |
   | router_id           | 40cf12dc-5439-4d1a-bc35-a716396bcaac                                                                                                                    |
   | status              | DOWN                                                                                                                                                    |
   | subnet_id           | None                                                                                                                                                    |
   | tags                | []                                                                                                                                                      |
   | updated_at          | 2024-07-02T12:31:12Z                                                                                                                                    |
   +---------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
   ```
   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack server show 67388836-587f-4ff2-96b7-a931ab58e66e
   +-------------------------------------+------------------------------------------------------------+
   | Field                               | Value                                                      |
   +-------------------------------------+------------------------------------------------------------+
   | OS-DCF:diskConfig                   | MANUAL                                                     |
   | OS-EXT-AZ:availability_zone         | nova                                                       |
   | OS-EXT-SRV-ATTR:host                | hemant-openstack-lab-1-26074-cmp-1.cluster.local           |
   | OS-EXT-SRV-ATTR:hypervisor_hostname | hemant-openstack-lab-1-26074-cmp-1.cluster.local           |
   | OS-EXT-SRV-ATTR:instance_name       | instance-00000075                                          |
   | OS-EXT-STS:power_state              | Running                                                    |
   | OS-EXT-STS:task_state               | None                                                       |
   | OS-EXT-STS:vm_state                 | active                                                     |
   | OS-SRV-USG:launched_at              | 2024-07-02T12:28:56.000000                                 |
   | OS-SRV-USG:terminated_at            | None                                                       |
   | accessIPv4                          |                                                            |
   | accessIPv6                          |                                                            |
   | addresses                           | itera-net=192.168.0.36, 200.0.200.167                      |
   | config_drive                        | True                                                       |
   | created                             | 2024-07-02T12:28:50Z                                       |
   | flavor                              | m1.small (7c276679-1c36-4781-988a-4a7e81bc71fa)            |
   | hostId                              | 6087c71fccb497069d05404dc1d4a6cebabb524ef76344f501c871f9   |
   | id                                  | 67388836-587f-4ff2-96b7-a931ab58e66e                       |
   | image                               | Cirros 0.3.5 64-bit (fd4df95d-e1d8-4ac9-8e9a-4c9a45f8e35b) |
   | key_name                            | None                                                       |
   | name                                | taikun                                                     |
   | progress                            | 0                                                          |
   | project_id                          | 7e27be1e438749fa94177c078ecd4bef                           |
   | properties                          |                                                            |
   | security_groups                     | name='default'                                             |
   | status                              | ACTIVE                                                     |
   | updated                             | 2024-07-02T12:28:56Z                                       |
   | user_id                             | 8d7ebbc875b147c6a743a2761354afc0                           |
   | volumes_attached                    |                                                            |
   +-------------------------------------+------------------------------------------------------------+
   ```
    - Verify Recordset Entries in the example.org. Zone
   ```
   root@hemant-openstack-lab-1-26074-master:/home/hemant# openstack recordset list  3e10776b-ec96-479a-92dc-d4c8e0b4892a
    +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
    | id                                   | name                    | type | records                                                                              | status | action |
    +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
    | 0685cf80-151b-443d-b44c-e125e9ab2907 | example.org.            | SOA  | hemant-openstack-lab-1-26074-cmp-1. mail.example.org. 1719923472 3562 600 86400 3600 | ACTIVE | NONE   |
    | b9d3b2cf-d448-4d8a-a3fe-635bcc3e2c23 | example.org.            | NS   | hemant-openstack-lab-1-26074-cmp-1.                                                  | ACTIVE | NONE   |
    | 7d0690b2-f5a3-4660-b07e-42ab3fe95716 | taikun.example.org.     | A    | 192.168.0.36                                                                         | ACTIVE | NONE   |
    +--------------------------------------+-------------------------+------+--------------------------------------------------------------------------------------+--------+--------+
   ```
    - Verify DNS Resolution
   ```
    root@hemant-openstack-lab-1-26074-master:/home/hemant# dig @10.233.55.82 taikun.example.org.
    ; <<>> DiG 9.18.12-0ubuntu0.22.04.1-Ubuntu <<>> @10.233.55.82 taikun.example.org.
    ; (1 server found)
    ;; global options: +cmd
    ;; Got answer:
    ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 26251
    ;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1
    ;; WARNING: recursion requested but not available
   
    ;; OPT PSEUDOSECTION:
    ; EDNS: version: 0, flags:; udp: 1232
    ;; QUESTION SECTION:
    ;taikun.example.org.            IN      A
   
    ;; ANSWER SECTION:
    taikun.example.org.     3600    IN      A       192.168.0.36
   
    ;; Query time: 8 msec
    ;; SERVER: 10.233.55.82#53(10.233.55.82) (UDP)
    ;; WHEN: Tue Jul 02 12:35:48 UTC 2024
    ;; MSG SIZE  rcvd: 63
   ```
- ## References:
  - https://docs.openstack.org/designate/latest
  - https://docs.openstack.org/designate/rocky/admin/backends/bind9.html
  - https://docs.openstack.org/designate/rocky/admin/backends/powerdns.html
  - https://docs.openstack.org/neutron/latest/admin/config-dns-int.html#config-dns-int
  - https://docs.openstack.org/neutron/latest/admin/config-dns-int-ext-serv.html#config-dns-int-ext-serv
  - https://www.modb.pro/db/124472