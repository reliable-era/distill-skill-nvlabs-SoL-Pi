# Local Qwen transport readiness

AF_UNIX metadata transport passed; native inference is still unexecuted.
[Unix routing audit](unix-routing-audit.json) records the sole successful phase:
two metadata GETs, denied foreign authority/path, actual 1 CPU/512 MiB helpers,
proxy-only read-only socket mount, actor zero mounts, and verified cleanup.

The broker forwards only the fixed localhost model listing. Its POST route is
denied. One internal bridge has no gateway and IPv6 is disabled. No server,
firewall or existing job was changed. The localhost-port denial probe has a
narrow scope; it is not a universal host reachability assertion.

Consumed phases 1–3 preserve the initial missing error capture, corrected logging,
and instrumented container-to-host bridge timeout. These are infrastructure
attempts, not model quality results. Native code under native-readiness requires
its own reviewed plan, a hash-bound routing certificate, both existing inference
locks, an idle scheduler sample, and bounded execution. Usage and monetary
savings remain TBD until observed and audited.
