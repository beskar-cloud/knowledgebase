# Prometheus not able to scrape/monitor expected application

## Analysis
 * find monitored application based in `instance` label
 * observe list of scraping targets at prometheus instance:
   * TODO
 * try to scrape metric endpoint with `curl` from a monitoring / debugger container
 * doublecheck monitoring host is using control plane network segment to scrape metrics (the should be static route present)
 * doublecheck hypervisor networking, sometimes [bonding may be the issue](/howtos/linux-network-bonding.md).

## Resolution
 * restart the metric exporter or component providing metrics (`kubectl rollout restart deploy|ds <name>`)
 * restore static routes on the infrastructure nodes/hypervisors ([`infra-config.git`](https://github.com/beskar-cloud/infra-config)'s [play_single_networking.yml](https://github.com/beskar-cloud/infra-config/blob/main/play_single_networking.yml))

