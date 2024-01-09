# Prometheus not able to scrape/monitor expected application

## Problem

Application metrics aren't being scraped by Prometheus.

## Analysis
 * find monitored application based in `instance` label
 * observe list of scraping targets at prometheus instance:
   * g2 ostrava: https://prometheus.ostrava.openstack.cloud.dev/targets
 * try to scrape metric endpoint with `curl` from a monitoring / debugger container
 * doublecheck monitoring host is using control plane network segment to scrape metrics (the should be static route present)
 * doublecheck hypervisor networking, sometimes [bonding may be the issue](/howtos/linux-network-bonding.md).

## Resolution
 * restart the metric exporter or component providing metrics (`kubectl rollout restart deploy|ds <name>`)
 * restore static routes on the g2 hosts ([`infra-config.git`](https://github.com/beskar-cloud/infra-config)'s [play_single_networking.yml](https://github.com/beskar-cloud/infra-config/blob/main/play_single_networking.yml))

## References
 * 
