# Same-run performance comparison

Baseline commit: 58f0dd3df22e27cb20dba4997cf8dfe2f5dbb784

Both revisions run on the same runner and dependencies, in alternating order.
Each sample uses a fresh process and database. Times include the same result consumer.
Ratios below 1 are faster. Ranges show observed variation, not confidence intervals.

| Workload | Baseline median ns/op | Candidate median ns/op | Paired ratio (range) |
| --- | ---: | ---: | ---: |
| disk_insert | 148166.5 | 222672.2 | 1.061 (0.506–1.896) |
| disk_update | 176303.8 | 180970.8 | 0.973 (0.672–1.419) |
| v2_accept | 1450.1 | 1614.2 | 1.106 (0.950–1.179) |
| v2_durable | 5071.3 | 7756.0 | 1.167 (0.467–2.968) |

## Python allocation peaks (separate samples)

These exclude existing model/fixture memory and SQLite/native memory; they are not process RSS.

| Workload | Baseline median bytes | Candidate median bytes |
| --- | ---: | ---: |

Cold reads clear only the application cache. OS pages may be warm.
v2_accept excludes flushing; v2_durable includes it. They are different contracts.
Full persisted values and database integrity are verified after each sample.
Raw samples, environment and source fingerprints are in the JSON artifact.
