# Same-run performance comparison

Baseline: local source snapshot
Baseline source SHA256: c7b889435d8195294a425eb5d07569d41f36cadda637040590e72e018df4a83a

Both revisions run on the same runner and dependencies, in alternating order.
Each sample uses a fresh process and database. Both versions use identical timing boundaries.
Ratios below 1 are faster. Ranges show observed variation, not confidence intervals.

| Workload | Baseline median ns/op | Candidate median ns/op | Paired ratio (range) |
| --- | ---: | ---: | ---: |
| async_batch | 9204.2 | 8682.4 | 0.939 (0.917–0.969) |
| async_cached | 350.2 | 353.4 | 1.010 (0.989–1.079) |
| async_mixed_batch | 9594.6 | 9170.5 | 0.959 (0.840–0.978) |
| batch_cold_0 | 224829.0 | 221309.0 | 0.978 (0.916–1.106) |
| batch_cold_50 | 136179.0 | 140898.0 | 1.003 (0.957–1.077) |
| batch_cold_90 | 81897.0 | 81636.0 | 1.006 (0.776–1.041) |
| cached_batch | 8365.1 | 8491.1 | 1.015 (0.993–1.032) |
| cached_get | 117.0 | 114.8 | 0.980 (0.942–1.075) |
| cached_item | 108.1 | 107.9 | 1.000 (0.984–1.010) |
| disk_insert | 63522.0 | 62913.7 | 0.993 (0.859–1.556) |
| disk_update | 74903.7 | 80082.3 | 1.037 (0.978–1.131) |
| mixed_batch | 11877.4 | 10471.2 | 0.891 (0.856–0.904) |

## Python allocation peaks (separate samples)

These exclude existing model/fixture memory and SQLite/native memory; they are not process RSS.

| Workload | Baseline median bytes | Candidate median bytes |
| --- | ---: | ---: |

Cold reads clear only the application cache. OS pages may be warm.
batch_cold cases reset/warm outside each timed batch; value verification is outside timing.
v2_accept excludes flushing; v2_durable includes it. They are different contracts.
Full persisted values and database integrity are verified after each sample.
Raw samples, environment and source fingerprints are in the JSON artifact.
