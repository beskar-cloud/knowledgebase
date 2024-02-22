# Node High Swap Usage

**Initial runbook version.**

## Problem

Swap usage is reaching its limits.

## Analysis
 * [identify components stored data into swap](https://www.cyberciti.biz/faq/linux-which-process-is-using-swap/) (`smem`, `ps`)
   * for instance: `grep  VmSwap /proc/*/status | sort -n -k 2`

## Resolution
 * increase amount of memory on a node
 * reconfigure component to avoid such problems


## References
 * 
