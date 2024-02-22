# Libvirt-down

**Initial runbook version.**

## Analysis
 * find problematic libvirt on a hostname based on `hostname` label
 * log on the host:
   * inspect whether `libvirtd` pods are running ok (exporter is included)
   * inspect whether libvirt-exporter metrics are exported (from debugger in default ns)
     * `curl -s $(netstat -nlp | grep -Eo '[0-9]+.[0-9]+.[0-9]+.[0-9]+:9098')/metrics | head`
     * `curl -s $(netstat -nlp | grep -Eo '[0-9]+.[0-9]+.[0-9]+.[0-9]+:9098')/metrics | grep ^libvirt_up`

## Resolution

Resolve the issue based on kubernetes logs/inspect

### case: up metric is missing
 * Promblem with scraping by Prometheus

### case: up metric is 0
 * Problem with pods/daemonset

## References
 * 
