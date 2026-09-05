# Same-run performance comparison

Baseline commit: 58f0dd3df22e27cb20dba4997cf8dfe2f5dbb784

Both revisions run on the same runner and dependencies, in alternating order.
Each sample uses a fresh process and database. Times include the same result consumer.
Ratios below 1 are faster. Ranges show observed variation, not confidence intervals.

| Workload | Baseline median ns/op | Candidate median ns/op | Paired ratio (range) |
| --- | ---: | ---: | ---: |
| async_cached | 379.8 | 352.6 | 0.926 (0.787–0.960) |
| async_disk_bounded | unsupported | 158746.7 | — |
| async_disk_unbounded | 149463.3 | 147421.3 | 1.004 (0.865–1.297) |
| auto_get | unsupported | 12688.2 | — |
| cached_batch | 11616.7 | 8426.5 | 0.736 (0.702–0.743) |
| cached_get | 114.7 | 114.6 | 1.007 (0.951–1.021) |
| cached_item | 98.2 | 110.2 | 1.123 (1.064–1.182) |
| cold_get | 16267.2 | 16629.7 | 1.018 (0.984–1.044) |
| disk_insert | 63247.3 | 63905.7 | 1.023 (0.741–1.119) |
| disk_update | 74581.3 | 77210.3 | 1.064 (0.888–3.283) |
| export_encrypted | unsupported | 2499.7 | — |
| export_items | 1278.0 | 1254.0 | 1.004 (0.830–1.114) |
| export_stream | unsupported | 1333.3 | — |
| missing_get | 204.7 | 208.5 | 1.010 (0.989–1.150) |
| mixed_batch | 11639.1 | 11992.4 | 1.032 (0.979–1.162) |
| v2_accept | 1582.7 | 1765.0 | 1.107 (0.937–1.234) |
| v2_durable | 13913.7 | 49306.3 | 1.114 (0.976–7.127) |

## Python allocation peaks (separate samples)

These exclude existing model/fixture memory and SQLite/native memory; they are not process RSS.

| Workload | Baseline median bytes | Candidate median bytes |
| --- | ---: | ---: |
| async_disk_bounded | unsupported | 651475 |
| async_disk_unbounded | 1288133 | 1732652 |
| export_items | 3721442 | 3721442 |
| export_stream | unsupported | 502932 |

Cold reads clear only the application cache. OS pages may be warm.
v2_accept excludes flushing; v2_durable includes it. They are different contracts.
Full persisted values and database integrity are verified after each sample.
Raw samples, environment and source fingerprints are in the JSON artifact.
