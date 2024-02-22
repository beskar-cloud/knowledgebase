# Node Is Low on Available Memory

**Initial runbook version.**

## Problem

Node memory capacity will soon be reached.

## Analysis
 * identify what is eating most of the memory especially answer:
   * What ostack VM flavors are in use? (`promQL:libvirt_domain_state_code{hostname=~"meta-hdi-010.+"}`)
   * Do the libvirt domains consume expected amount od memory? (`ps`, `top`, `virsh dumpxml`)
   * What are the top 5 memory consumers apart from libvirtd/qemu/kvm? (`ps aux --sort -rss | head`)
     * compare their usage to another functional hypervisor.

## Resolution
 * Add data to [troubleshooting/node-low-memory.md](../troubleshooting/node-low-memory.md) until resolved.
 * Once there are data from 3 incidents decide:
   * Do we see other app memory usage explosion?
   * Do we see issues with particular ostack flavor[s] only?
   * Do we need to shring the problematic flavor[s]?

## References
