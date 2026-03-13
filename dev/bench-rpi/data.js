window.BENCHMARK_DATA = {
  "lastUpdate": 1773394418609,
  "repoUrl": "https://github.com/disnana/NanaSQLite",
  "entries": {
    "NanaSQLite Performance (RPI)": [
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "14e295a59776e7111b34e3d139896e42baccb794",
          "message": "Refactor benchmark Docker commands for better structure\n\nUpdated Docker run commands to use named containers for benchmarks and added output directory creation within the container.",
          "timestamp": "2026-03-12T16:47:37+09:00",
          "tree_id": "c58f7bc7456cbb8ae602ae0723f1cc58090a24d4",
          "url": "https://github.com/disnana/NanaSQLite/commit/14e295a59776e7111b34e3d139896e42baccb794"
        },
        "date": 1773302120110,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4430.842655924503,
            "unit": "iter/sec",
            "range": "stddev: 0.003932549208024764",
            "extra": "mean: 225.69070437716735 usec\nrounds: 5001"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4195.183228332989,
            "unit": "iter/sec",
            "range": "stddev: 0.004316360631788237",
            "extra": "mean: 238.36861123163936 usec\nrounds: 6945"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 724.5494034489088,
            "unit": "iter/sec",
            "range": "stddev: 0.009866636592006869",
            "extra": "mean: 1.3801681365548382 msec\nrounds: 1687"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2280953.2982720085,
            "unit": "iter/sec",
            "range": "stddev: 5.0313272273981154e-8",
            "extra": "mean: 438.41318485458436 nsec\nrounds: 133672"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 86926.96470642352,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015969679061572288",
            "extra": "mean: 11.503910246691316 usec\nrounds: 10243"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 489.2845702515185,
            "unit": "iter/sec",
            "range": "stddev: 0.00016907756551387863",
            "extra": "mean: 2.0438003991949847 msec\nrounds: 276"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2650.1144210628354,
            "unit": "iter/sec",
            "range": "stddev: 0.00001587209340418625",
            "extra": "mean: 377.3421977753501 usec\nrounds: 1473"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2307331.9446475664,
            "unit": "iter/sec",
            "range": "stddev: 8.187451823271974e-8",
            "extra": "mean: 433.40101207359874 nsec\nrounds: 137760"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 116842.02746770495,
            "unit": "iter/sec",
            "range": "stddev: 0.000001237393087530783",
            "extra": "mean: 8.55856425699562 usec\nrounds: 9555"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 89525.63747178047,
            "unit": "iter/sec",
            "range": "stddev: 0.000001630640694291115",
            "extra": "mean: 11.169984690868151 usec\nrounds: 322"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 74185.45356577024,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010690527614181362",
            "extra": "mean: 13.479731563728121 usec\nrounds: 17550"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5813545.937071806,
            "unit": "iter/sec",
            "range": "stddev: 1.4161035178996504e-8",
            "extra": "mean: 172.01205784302405 nsec\nrounds: 147536"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1449363.655085318,
            "unit": "iter/sec",
            "range": "stddev: 2.6596603214214647e-7",
            "extra": "mean: 689.957966374653 nsec\nrounds: 3937"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 112701.81573323009,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016429021176463922",
            "extra": "mean: 8.87297150888005 usec\nrounds: 392"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 69743.19966113358,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016573509464822622",
            "extra": "mean: 14.338315489664563 usec\nrounds: 10868"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 4119.17336440448,
            "unit": "iter/sec",
            "range": "stddev: 0.0042159575341788064",
            "extra": "mean: 242.7671553330149 usec\nrounds: 5889"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4677.894547790157,
            "unit": "iter/sec",
            "range": "stddev: 0.003840298856474463",
            "extra": "mean: 213.77138577704815 usec\nrounds: 7053"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 50723.237954367025,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036705124988829968",
            "extra": "mean: 19.714829737400564 usec\nrounds: 7076"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9530.317521479376,
            "unit": "iter/sec",
            "range": "stddev: 0.002351587725663263",
            "extra": "mean: 104.92829832229678 usec\nrounds: 8262"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7427.598995216533,
            "unit": "iter/sec",
            "range": "stddev: 0.000014766134138906404",
            "extra": "mean: 134.63300868073418 usec\nrounds: 1021"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12440.907253121697,
            "unit": "iter/sec",
            "range": "stddev: 0.000006456175810202723",
            "extra": "mean: 80.37998995202524 usec\nrounds: 3762"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21928.530701558502,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032001466692602922",
            "extra": "mean: 45.60269055915033 usec\nrounds: 5731"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8152.007671549467,
            "unit": "iter/sec",
            "range": "stddev: 0.000005351651171595698",
            "extra": "mean: 122.66916817190975 usec\nrounds: 4193"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 7605.207978326764,
            "unit": "iter/sec",
            "range": "stddev: 0.0028681148546776175",
            "extra": "mean: 131.48884328341694 usec\nrounds: 7013"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 1629.2130583139294,
            "unit": "iter/sec",
            "range": "stddev: 0.009380713584360654",
            "extra": "mean: 613.7932635004158 usec\nrounds: 3513"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2167.509293066726,
            "unit": "iter/sec",
            "range": "stddev: 0.0051352103211919605",
            "extra": "mean: 461.3590369364175 usec\nrounds: 2739"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2090.6424781445558,
            "unit": "iter/sec",
            "range": "stddev: 0.00513122743319433",
            "extra": "mean: 478.3218606021531 usec\nrounds: 3853"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 446.37688429791535,
            "unit": "iter/sec",
            "range": "stddev: 0.008342037854576658",
            "extra": "mean: 2.2402593753770463 msec\nrounds: 1110"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1345.4652418415553,
            "unit": "iter/sec",
            "range": "stddev: 0.0035298416904152564",
            "extra": "mean: 743.2373344935224 usec\nrounds: 1032"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15518.247236648922,
            "unit": "iter/sec",
            "range": "stddev: 0.000005055770520978463",
            "extra": "mean: 64.44026730276173 usec\nrounds: 2210"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28521.59040732346,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034563128554477696",
            "extra": "mean: 35.061158431867504 usec\nrounds: 6288"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2232.19236514164,
            "unit": "iter/sec",
            "range": "stddev: 0.000027982664847863494",
            "extra": "mean: 447.9900637669937 usec\nrounds: 1017"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 112008.95590802524,
            "unit": "iter/sec",
            "range": "stddev: 0.000001040310647765836",
            "extra": "mean: 8.927857526152977 usec\nrounds: 13914"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 43157.13042696652,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020158415435784704",
            "extra": "mean: 23.171142059416322 usec\nrounds: 11593"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 56058.66150607998,
            "unit": "iter/sec",
            "range": "stddev: 0.000001863514469405626",
            "extra": "mean: 17.838456594107985 usec\nrounds: 11419"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70828.09439875602,
            "unit": "iter/sec",
            "range": "stddev: 0.000001020588628015603",
            "extra": "mean: 14.11869129741211 usec\nrounds: 15482"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 96971.24421260828,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013918942089042948",
            "extra": "mean: 10.31233545696817 usec\nrounds: 12417"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1335.8909536427122,
            "unit": "iter/sec",
            "range": "stddev: 0.005076226030351852",
            "extra": "mean: 748.5640929547404 usec\nrounds: 389"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 134.2780334522555,
            "unit": "iter/sec",
            "range": "stddev: 0.2006687871320919",
            "extra": "mean: 7.447234475291631 msec\nrounds: 1645"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 253779.66384125839,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010102424997665006",
            "extra": "mean: 3.9404260564609683 usec\nrounds: 24885"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4729.843793440939,
            "unit": "iter/sec",
            "range": "stddev: 0.003819104400967049",
            "extra": "mean: 211.42347267086058 usec\nrounds: 8172"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 153746.5529821025,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010536741142901444",
            "extra": "mean: 6.504210862642293 usec\nrounds: 14694"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 9368.11013383458,
            "unit": "iter/sec",
            "range": "stddev: 0.0026322166943491465",
            "extra": "mean: 106.74511568649517 usec\nrounds: 10508"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2628.7293707316717,
            "unit": "iter/sec",
            "range": "stddev: 0.0045819809594912185",
            "extra": "mean: 380.4119249147596 usec\nrounds: 3526"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1912.1735444971534,
            "unit": "iter/sec",
            "range": "stddev: 0.0053175322510345445",
            "extra": "mean: 522.9650848783034 usec\nrounds: 2067"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3644.061971482331,
            "unit": "iter/sec",
            "range": "stddev: 0.004422550311079231",
            "extra": "mean: 274.41904331643957 usec\nrounds: 3962"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 363348.9315327774,
            "unit": "iter/sec",
            "range": "stddev: 4.5270990502303004e-7",
            "extra": "mean: 2.752175424822436 usec\nrounds: 44227"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8200.060158999644,
            "unit": "iter/sec",
            "range": "stddev: 0.0026685335037107787",
            "extra": "mean: 121.95032482810392 usec\nrounds: 8373"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 36814.8864232815,
            "unit": "iter/sec",
            "range": "stddev: 0.000002706246387302986",
            "extra": "mean: 27.162925032619587 usec\nrounds: 9340"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 1919.3451396255925,
            "unit": "iter/sec",
            "range": "stddev: 0.0357569654671505",
            "extra": "mean: 521.0110361886609 usec\nrounds: 7492"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 3851.6283540703407,
            "unit": "iter/sec",
            "range": "stddev: 0.004727131006360145",
            "extra": "mean: 259.6304492730238 usec\nrounds: 6807"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4018.039759784153,
            "unit": "iter/sec",
            "range": "stddev: 0.004196420200193761",
            "extra": "mean: 248.87757707348308 usec\nrounds: 4070"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4009.685412835233,
            "unit": "iter/sec",
            "range": "stddev: 0.00424062012031714",
            "extra": "mean: 249.39612389514218 usec\nrounds: 5132"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4491.365765732764,
            "unit": "iter/sec",
            "range": "stddev: 0.0034387984689320332",
            "extra": "mean: 222.64942384109088 usec\nrounds: 1346"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1214921.1027155912,
            "unit": "iter/sec",
            "range": "stddev: 2.2794501036821637e-7",
            "extra": "mean: 823.0987162580356 nsec\nrounds: 106930"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1224390.1477493856,
            "unit": "iter/sec",
            "range": "stddev: 1.471456847540241e-7",
            "extra": "mean: 816.7331318682621 nsec\nrounds: 143247"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1219189.9663359574,
            "unit": "iter/sec",
            "range": "stddev: 2.230142591406332e-7",
            "extra": "mean: 820.2167239001392 nsec\nrounds: 136724"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1226139.743184466,
            "unit": "iter/sec",
            "range": "stddev: 3.9438694894804863e-7",
            "extra": "mean: 815.5677242814529 nsec\nrounds: 190151"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 83329.06986176594,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019647341733648457",
            "extra": "mean: 12.000613971317495 usec\nrounds: 11490"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 51151.45328508173,
            "unit": "iter/sec",
            "range": "stddev: 0.000003854044209533071",
            "extra": "mean: 19.54978667813626 usec\nrounds: 9222"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 37063.57343517059,
            "unit": "iter/sec",
            "range": "stddev: 0.000007099035615358747",
            "extra": "mean: 26.980668816220344 usec\nrounds: 158"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17079.463727618313,
            "unit": "iter/sec",
            "range": "stddev: 0.000009268619111565842",
            "extra": "mean: 58.54984769708852 usec\nrounds: 3350"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 52.62242192484285,
            "unit": "iter/sec",
            "range": "stddev: 0.030988958977126002",
            "extra": "mean: 19.003306260366244 msec\nrounds: 193"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 51.986845779877925,
            "unit": "iter/sec",
            "range": "stddev: 0.03184685416050943",
            "extra": "mean: 19.23563518806638 msec\nrounds: 188"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 50.95281965482334,
            "unit": "iter/sec",
            "range": "stddev: 0.0319297682532572",
            "extra": "mean: 19.62599924350481 msec\nrounds: 184"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 51.4388670058679,
            "unit": "iter/sec",
            "range": "stddev: 0.03105438351035733",
            "extra": "mean: 19.44055260559928 msec\nrounds: 194"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21776.98505408462,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023304703813213257",
            "extra": "mean: 45.920038862883544 usec\nrounds: 11758"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 16945.240287272023,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025722482213727326",
            "extra": "mean: 59.01362170420942 usec\nrounds: 8925"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21683.340387890737,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016128585735914376",
            "extra": "mean: 46.118355479880734 usec\nrounds: 13380"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4357.805917235338,
            "unit": "iter/sec",
            "range": "stddev: 0.000007212741986424851",
            "extra": "mean: 229.47327599995918 usec\nrounds: 2976"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 3877.477514803873,
            "unit": "iter/sec",
            "range": "stddev: 0.006065636914609436",
            "extra": "mean: 257.89962577012676 usec\nrounds: 12870"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 421077.1140332848,
            "unit": "iter/sec",
            "range": "stddev: 2.947605340746693e-7",
            "extra": "mean: 2.3748619116852625 usec\nrounds: 76923"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 4201.6099597405555,
            "unit": "iter/sec",
            "range": "stddev: 0.004027352371068318",
            "extra": "mean: 238.004005507867 usec\nrounds: 5242"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4171.776560895627,
            "unit": "iter/sec",
            "range": "stddev: 0.00002522901319147459",
            "extra": "mean: 239.70603060901058 usec\nrounds: 986"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3617.5707219378683,
            "unit": "iter/sec",
            "range": "stddev: 0.000020607914621430988",
            "extra": "mean: 276.42859721739393 usec\nrounds: 1231"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5086.005340962801,
            "unit": "iter/sec",
            "range": "stddev: 0.000014263600808194982",
            "extra": "mean: 196.61796104419665 usec\nrounds: 2786"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5105.202095854921,
            "unit": "iter/sec",
            "range": "stddev: 0.000011944357901927543",
            "extra": "mean: 195.87863148687737 usec\nrounds: 2620"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21614.225755909814,
            "unit": "iter/sec",
            "range": "stddev: 0.000007966903130338784",
            "extra": "mean: 46.26582563229579 usec\nrounds: 11712"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21518.242163075265,
            "unit": "iter/sec",
            "range": "stddev: 0.000004252430850016983",
            "extra": "mean: 46.47219751602078 usec\nrounds: 12605"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21488.10219361902,
            "unit": "iter/sec",
            "range": "stddev: 0.000008640863460709109",
            "extra": "mean: 46.537381058107314 usec\nrounds: 13028"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21500.424542319764,
            "unit": "iter/sec",
            "range": "stddev: 0.000004336901982727476",
            "extra": "mean: 46.51070949932536 usec\nrounds: 12486"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 207.7531621560345,
            "unit": "iter/sec",
            "range": "stddev: 0.01105341608060511",
            "extra": "mean: 4.813404472991572 msec\nrounds: 74"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 332.13445836729176,
            "unit": "iter/sec",
            "range": "stddev: 0.003336324879942937",
            "extra": "mean: 3.0108288219048545 msec\nrounds: 869"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 219973.10831394044,
            "unit": "iter/sec",
            "range": "stddev: 0.000020146355250051185",
            "extra": "mean: 4.5460102267265485 usec\nrounds: 36145"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 933165.1974856107,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012696471788976998",
            "extra": "mean: 1.0716216192957837 usec\nrounds: 66340"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 56.31387295851497,
            "unit": "iter/sec",
            "range": "stddev: 0.0023480261471310548",
            "extra": "mean: 17.757613665404886 msec\nrounds: 72"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 112.55657635296025,
            "unit": "iter/sec",
            "range": "stddev: 0.0013327358995055963",
            "extra": "mean: 8.884420905484479 msec\nrounds: 44"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 152016.16905949145,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015407111994318333",
            "extra": "mean: 6.578247604757429 usec\nrounds: 18331"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 117601.55617263123,
            "unit": "iter/sec",
            "range": "stddev: 0.000002327330232977484",
            "extra": "mean: 8.503288838559813 usec\nrounds: 4091"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 69611.8073493123,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023878152040105675",
            "extra": "mean: 14.365379065393268 usec\nrounds: 12620"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 81157.8418191103,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021290648320686185",
            "extra": "mean: 12.32166821573278 usec\nrounds: 11636"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2476.8491947757952,
            "unit": "iter/sec",
            "range": "stddev: 0.004278653200647906",
            "extra": "mean: 403.7387508731714 usec\nrounds: 2411"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 831.1662832400867,
            "unit": "iter/sec",
            "range": "stddev: 0.008691320139607822",
            "extra": "mean: 1.2031286881630456 msec\nrounds: 1664"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4815.530498063052,
            "unit": "iter/sec",
            "range": "stddev: 0.00003483822438753395",
            "extra": "mean: 207.66144050011303 usec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4700.87751889845,
            "unit": "iter/sec",
            "range": "stddev: 0.00002713748267070462",
            "extra": "mean: 212.72624014980263 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1346.8876984113035,
            "unit": "iter/sec",
            "range": "stddev: 0.0002707047143891283",
            "extra": "mean: 742.4523968698591 usec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 197.5663999427605,
            "unit": "iter/sec",
            "range": "stddev: 0.004552349431004658",
            "extra": "mean: 5.0615894215297885 msec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 9741.39474949443,
            "unit": "iter/sec",
            "range": "stddev: 0.000021363685305929506",
            "extra": "mean: 102.65470455880039 usec\nrounds: 3730"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7731.994678856066,
            "unit": "iter/sec",
            "range": "stddev: 0.0000209134715954378",
            "extra": "mean: 129.33273256571204 usec\nrounds: 3717"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 292.12911841103596,
            "unit": "iter/sec",
            "range": "stddev: 0.0003111505619413287",
            "extra": "mean: 3.423143866791686 msec\nrounds: 217"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7658.216068397085,
            "unit": "iter/sec",
            "range": "stddev: 0.000017111707587164994",
            "extra": "mean: 130.57871324976946 usec\nrounds: 2313"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1739.3262081771595,
            "unit": "iter/sec",
            "range": "stddev: 0.000030798136409022796",
            "extra": "mean: 574.9352797069707 usec\nrounds: 1006"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 7124.9460228309545,
            "unit": "iter/sec",
            "range": "stddev: 0.000017475584419372967",
            "extra": "mean: 140.35194046321632 usec\nrounds: 346"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 10271.891705995053,
            "unit": "iter/sec",
            "range": "stddev: 0.00001092294080516708",
            "extra": "mean: 97.35305128035603 usec\nrounds: 3668"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8721.685630848591,
            "unit": "iter/sec",
            "range": "stddev: 0.000012610643720217848",
            "extra": "mean: 114.65673521446372 usec\nrounds: 2938"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6453.971826844462,
            "unit": "iter/sec",
            "range": "stddev: 0.000016448468451871497",
            "extra": "mean: 154.94334757406736 usec\nrounds: 355"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2749.5891083898373,
            "unit": "iter/sec",
            "range": "stddev: 0.00006227393500226682",
            "extra": "mean: 363.690704530613 usec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 5275.83033618541,
            "unit": "iter/sec",
            "range": "stddev: 0.00002145884330201726",
            "extra": "mean: 189.54362371005118 usec\nrounds: 50"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7382.298914205038,
            "unit": "iter/sec",
            "range": "stddev: 0.00001294483900547632",
            "extra": "mean: 135.45915867424407 usec\nrounds: 3132"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1192.8841891578777,
            "unit": "iter/sec",
            "range": "stddev: 0.00011610619255474471",
            "extra": "mean: 838.3043459616601 usec\nrounds: 38"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 271.89281062472656,
            "unit": "iter/sec",
            "range": "stddev: 0.00027628848070733263",
            "extra": "mean: 3.677919977737939 msec\nrounds: 219"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 59.16577759984551,
            "unit": "iter/sec",
            "range": "stddev: 0.004484372220242457",
            "extra": "mean: 16.90166242322168 msec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 47.84796859652937,
            "unit": "iter/sec",
            "range": "stddev: 0.0031545132069957793",
            "extra": "mean: 20.899528847971503 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 18.297209977313898,
            "unit": "iter/sec",
            "range": "stddev: 0.012108080349468047",
            "extra": "mean: 54.653141175068036 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 30.394503105146722,
            "unit": "iter/sec",
            "range": "stddev: 0.0060228058678275034",
            "extra": "mean: 32.90068590825784 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 47.27807743987897,
            "unit": "iter/sec",
            "range": "stddev: 0.0028052946399652013",
            "extra": "mean: 21.15145230411806 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 66.7075484011146,
            "unit": "iter/sec",
            "range": "stddev: 0.002367388256166673",
            "extra": "mean: 14.990807246984533 msec\nrounds: 73"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 7028.989744730182,
            "unit": "iter/sec",
            "range": "stddev: 0.000016764217264630563",
            "extra": "mean: 142.26795546966423 usec\nrounds: 3457"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1657.943518393675,
            "unit": "iter/sec",
            "range": "stddev: 0.00007543284964897824",
            "extra": "mean: 603.1568560121192 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4815.05723974239,
            "unit": "iter/sec",
            "range": "stddev: 0.000017511342776824945",
            "extra": "mean: 207.68185095417493 usec\nrounds: 927"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 672.8244245487253,
            "unit": "iter/sec",
            "range": "stddev: 0.00011240067859096575",
            "extra": "mean: 1.486271846731362 msec\nrounds: 464"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 455.16362905496135,
            "unit": "iter/sec",
            "range": "stddev: 0.0002479092254352682",
            "extra": "mean: 2.197012098871479 msec\nrounds: 339"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 67.75457238465688,
            "unit": "iter/sec",
            "range": "stddev: 0.002162109543511186",
            "extra": "mean: 14.75915152003013 msec\nrounds: 63"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 62.815757947340266,
            "unit": "iter/sec",
            "range": "stddev: 0.0022188413732684435",
            "extra": "mean: 15.919572296466125 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.278410775412695,
            "unit": "iter/sec",
            "range": "stddev: 0.004587473303505679",
            "extra": "mean: 30.980459569642942 msec\nrounds: 21"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 63.21583307726602,
            "unit": "iter/sec",
            "range": "stddev: 0.0025663209558319995",
            "extra": "mean: 15.81882182550284 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 62.83873298317338,
            "unit": "iter/sec",
            "range": "stddev: 0.002823645240104257",
            "extra": "mean: 15.913751798079295 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 657.6392928398232,
            "unit": "iter/sec",
            "range": "stddev: 0.00011634225862644051",
            "extra": "mean: 1.5205904070631062 msec\nrounds: 475"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 64.29673104785994,
            "unit": "iter/sec",
            "range": "stddev: 0.0023836566109608436",
            "extra": "mean: 15.552890227897274 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 65.97615501833387,
            "unit": "iter/sec",
            "range": "stddev: 0.0018752727808387431",
            "extra": "mean: 15.156991184498608 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 647.3018550101181,
            "unit": "iter/sec",
            "range": "stddev: 0.00014376686127679444",
            "extra": "mean: 1.5448742997721963 msec\nrounds: 463"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 46.00429246003286,
            "unit": "iter/sec",
            "range": "stddev: 0.003062445481561237",
            "extra": "mean: 21.737102051265538 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 21.727479586255416,
            "unit": "iter/sec",
            "range": "stddev: 0.0032052122436208082",
            "extra": "mean: 46.02466641517822 msec\nrounds: 12"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 20.25295271777831,
            "unit": "iter/sec",
            "range": "stddev: 0.010263746002027504",
            "extra": "mean: 49.37551644616178 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 21.147601285664397,
            "unit": "iter/sec",
            "range": "stddev: 0.006990975552407635",
            "extra": "mean: 47.286686867785946 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 21.393702448381305,
            "unit": "iter/sec",
            "range": "stddev: 0.004648775339054952",
            "extra": "mean: 46.74272732421135 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.51642030938476,
            "unit": "iter/sec",
            "range": "stddev: 0.0004934112789140958",
            "extra": "mean: 12.118800067315426 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 82.20788890903692,
            "unit": "iter/sec",
            "range": "stddev: 0.0004660324030633952",
            "extra": "mean: 12.164282689542127 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 81.98137742874698,
            "unit": "iter/sec",
            "range": "stddev: 0.0004719757599377936",
            "extra": "mean: 12.197892147751928 msec\nrounds: 74"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 75.6363982127262,
            "unit": "iter/sec",
            "range": "stddev: 0.0006258546992512127",
            "extra": "mean: 13.221147802246154 msec\nrounds: 61"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 65.94716676327849,
            "unit": "iter/sec",
            "range": "stddev: 0.0028437289325434953",
            "extra": "mean: 15.163653710697883 msec\nrounds: 79"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 580.4566357804679,
            "unit": "iter/sec",
            "range": "stddev: 0.0001459768703284736",
            "extra": "mean: 1.7227815798081527 msec\nrounds: 426"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 60.25796809200576,
            "unit": "iter/sec",
            "range": "stddev: 0.0020509169743977334",
            "extra": "mean: 16.595315634824182 msec\nrounds: 49"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 60.57213483615571,
            "unit": "iter/sec",
            "range": "stddev: 0.0021002740685879665",
            "extra": "mean: 16.509241463998997 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 62.324955592543965,
            "unit": "iter/sec",
            "range": "stddev: 0.0019243272288261587",
            "extra": "mean: 16.044937224466015 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 53.608425134488044,
            "unit": "iter/sec",
            "range": "stddev: 0.012612425710308234",
            "extra": "mean: 18.6537843163885 msec\nrounds: 38"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 431.02472247347805,
            "unit": "iter/sec",
            "range": "stddev: 0.0017094189161243759",
            "extra": "mean: 2.3200525349483456 msec\nrounds: 595"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 408.0503913793595,
            "unit": "iter/sec",
            "range": "stddev: 0.001902569705024517",
            "extra": "mean: 2.4506777131609514 msec\nrounds: 433"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 679.7160718137636,
            "unit": "iter/sec",
            "range": "stddev: 0.00011848122170855845",
            "extra": "mean: 1.4712025233294637 msec\nrounds: 481"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 62.212487227133,
            "unit": "iter/sec",
            "range": "stddev: 0.0028709902173833833",
            "extra": "mean: 16.073943424719168 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 38.30844973485366,
            "unit": "iter/sec",
            "range": "stddev: 0.013433465880881434",
            "extra": "mean: 26.103901539251886 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 68.43735721511392,
            "unit": "iter/sec",
            "range": "stddev: 0.001783305734046637",
            "extra": "mean: 14.611902631727528 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 56.77959952294386,
            "unit": "iter/sec",
            "range": "stddev: 0.002921171094324151",
            "extra": "mean: 17.611959372765803 msec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 67.04366223211457,
            "unit": "iter/sec",
            "range": "stddev: 0.0021695310057028502",
            "extra": "mean: 14.915652974592284 msec\nrounds: 78"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 649.7797288152943,
            "unit": "iter/sec",
            "range": "stddev: 0.00011564819207578124",
            "extra": "mean: 1.5389830671129767 msec\nrounds: 477"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 728.7370049255464,
            "unit": "iter/sec",
            "range": "stddev: 0.0001260791567153551",
            "extra": "mean: 1.3722371627088814 msec\nrounds: 525"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 268.04311278558424,
            "unit": "iter/sec",
            "range": "stddev: 0.001957503740380799",
            "extra": "mean: 3.730743124147831 msec\nrounds: 244"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 652.9586205916064,
            "unit": "iter/sec",
            "range": "stddev: 0.00042598716662490914",
            "extra": "mean: 1.5314906158891972 msec\nrounds: 448"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 732.1332754289215,
            "unit": "iter/sec",
            "range": "stddev: 0.0000963651792822517",
            "extra": "mean: 1.3658715339965233 msec\nrounds: 496"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 84.58626022847434,
            "unit": "iter/sec",
            "range": "stddev: 0.0035178221549671965",
            "extra": "mean: 11.82225100505589 msec\nrounds: 11"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 99.60928958908562,
            "unit": "iter/sec",
            "range": "stddev: 0.0005633722417281722",
            "extra": "mean: 10.039224294493632 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 123.68367445185383,
            "unit": "iter/sec",
            "range": "stddev: 0.0007654048659135319",
            "extra": "mean: 8.085141425752747 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 125.53584186979651,
            "unit": "iter/sec",
            "range": "stddev: 0.000447721261878055",
            "extra": "mean: 7.96585250160812 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 117.67509042111988,
            "unit": "iter/sec",
            "range": "stddev: 0.00042926402412629076",
            "extra": "mean: 8.497975199520422 msec\nrounds: 113"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 115.78418056456938,
            "unit": "iter/sec",
            "range": "stddev: 0.00044160919630720474",
            "extra": "mean: 8.636758451145491 msec\nrounds: 107"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 114.76118290984547,
            "unit": "iter/sec",
            "range": "stddev: 0.00047498927883577927",
            "extra": "mean: 8.71374775550705 msec\nrounds: 131"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 123.98070879854649,
            "unit": "iter/sec",
            "range": "stddev: 0.000881783553986861",
            "extra": "mean: 8.065770954938465 msec\nrounds: 119"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 253.92392089675695,
            "unit": "iter/sec",
            "range": "stddev: 0.00021617146726499105",
            "extra": "mean: 3.9381874557875562 msec\nrounds: 48"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 7287.758474586537,
            "unit": "iter/sec",
            "range": "stddev: 0.00001580156822582315",
            "extra": "mean: 137.2164024764465 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7681.317208015275,
            "unit": "iter/sec",
            "range": "stddev: 0.00001242115257038023",
            "extra": "mean: 130.18600494151227 usec\nrounds: 58"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 40.513394178792495,
            "unit": "iter/sec",
            "range": "stddev: 0.012634166999192812",
            "extra": "mean: 24.683194787058078 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 83.62321037165624,
            "unit": "iter/sec",
            "range": "stddev: 0.0025640581470809877",
            "extra": "mean: 11.958402404734105 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 668.5641861201054,
            "unit": "iter/sec",
            "range": "stddev: 0.00020824022882408278",
            "extra": "mean: 1.4957426986978228 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 712.3648717959393,
            "unit": "iter/sec",
            "range": "stddev: 0.00013384315187562007",
            "extra": "mean: 1.403775002940425 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 67.9521421457722,
            "unit": "iter/sec",
            "range": "stddev: 0.001752732650420877",
            "extra": "mean: 14.716239524204866 msec\nrounds: 32"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "222d8f238ebdfa0cb6dccbce23eaf8a8a6430523",
          "message": "Add debug step to display benchmark result files\n\nAdded a debug step to show downloaded benchmark result files.",
          "timestamp": "2026-03-12T17:38:38+09:00",
          "tree_id": "b3742c0485ad335993c595a14cb886c5fd703a3a",
          "url": "https://github.com/disnana/NanaSQLite/commit/222d8f238ebdfa0cb6dccbce23eaf8a8a6430523"
        },
        "date": 1773305025245,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4226.980145571612,
            "unit": "iter/sec",
            "range": "stddev: 0.004186962033560408",
            "extra": "mean: 236.57551385654085 usec\nrounds: 5079"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4038.6356080303854,
            "unit": "iter/sec",
            "range": "stddev: 0.004421017271114405",
            "extra": "mean: 247.60837496990553 usec\nrounds: 7756"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 742.4288389365896,
            "unit": "iter/sec",
            "range": "stddev: 0.009281815300649065",
            "extra": "mean: 1.3469304363665882 msec\nrounds: 1741"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2571759.562888943,
            "unit": "iter/sec",
            "range": "stddev: 2.5388401998987674e-8",
            "extra": "mean: 388.8388379809442 nsec\nrounds: 55785"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 85919.14597363771,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018804361500103873",
            "extra": "mean: 11.638849393438184 usec\nrounds: 7925"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 494.81116424935925,
            "unit": "iter/sec",
            "range": "stddev: 0.00018371812466478582",
            "extra": "mean: 2.0209729938430647 msec\nrounds: 290"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2669.2196495208086,
            "unit": "iter/sec",
            "range": "stddev: 0.000014126652058025518",
            "extra": "mean: 374.6413301653631 usec\nrounds: 1506"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2281938.0901080053,
            "unit": "iter/sec",
            "range": "stddev: 8.926712452404539e-8",
            "extra": "mean: 438.2239835230015 nsec\nrounds: 140253"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 115671.92152403032,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013352569143382869",
            "extra": "mean: 8.645140383461639 usec\nrounds: 8738"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 96983.82612033084,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013489990366411987",
            "extra": "mean: 10.310997616852825 usec\nrounds: 327"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 71482.94803751833,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010969640436108316",
            "extra": "mean: 13.989350291976526 usec\nrounds: 16881"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5841913.576241452,
            "unit": "iter/sec",
            "range": "stddev: 1.5007269087068207e-8",
            "extra": "mean: 171.1767876996442 nsec\nrounds: 132346"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1419445.0706900253,
            "unit": "iter/sec",
            "range": "stddev: 3.111877454120231e-7",
            "extra": "mean: 704.5006676544917 nsec\nrounds: 3480"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 79507.3120503929,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025301310357051293",
            "extra": "mean: 12.577459534365662 usec\nrounds: 338"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70075.85742379964,
            "unit": "iter/sec",
            "range": "stddev: 0.000002373555313852889",
            "extra": "mean: 14.27024993718269 usec\nrounds: 13889"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 4258.776521576065,
            "unit": "iter/sec",
            "range": "stddev: 0.0040145540396850825",
            "extra": "mean: 234.80922160008654 usec\nrounds: 6251"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 5210.191166830471,
            "unit": "iter/sec",
            "range": "stddev: 0.003401447029133264",
            "extra": "mean: 191.93153724690157 usec\nrounds: 8418"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 50829.355554849484,
            "unit": "iter/sec",
            "range": "stddev: 0.00000322500573034653",
            "extra": "mean: 19.673670639418383 usec\nrounds: 9630"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9677.679104248184,
            "unit": "iter/sec",
            "range": "stddev: 0.0023079758019412507",
            "extra": "mean: 103.33055986130319 usec\nrounds: 12426"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7436.851852372989,
            "unit": "iter/sec",
            "range": "stddev: 0.000016608106851228885",
            "extra": "mean: 134.46549962951258 usec\nrounds: 1060"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12316.44005954353,
            "unit": "iter/sec",
            "range": "stddev: 0.00000766448882545284",
            "extra": "mean: 81.19229218552798 usec\nrounds: 3831"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21929.20166843191,
            "unit": "iter/sec",
            "range": "stddev: 0.000004974711674010417",
            "extra": "mean: 45.60129525551976 usec\nrounds: 5524"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8256.819409900092,
            "unit": "iter/sec",
            "range": "stddev: 0.0000085928086623285",
            "extra": "mean: 121.11201061282509 usec\nrounds: 3772"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8372.728036441673,
            "unit": "iter/sec",
            "range": "stddev: 0.002492382387269797",
            "extra": "mean: 119.4353854141177 usec\nrounds: 7940"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2102.257366190213,
            "unit": "iter/sec",
            "range": "stddev: 0.00528361519655771",
            "extra": "mean: 475.6791514124821 usec\nrounds: 3438"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2315.843026059387,
            "unit": "iter/sec",
            "range": "stddev: 0.004551382257226818",
            "extra": "mean: 431.8081963014519 usec\nrounds: 3295"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2239.6925511308377,
            "unit": "iter/sec",
            "range": "stddev: 0.004617746916022196",
            "extra": "mean: 446.4898539288763 usec\nrounds: 3756"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 436.0493501309764,
            "unit": "iter/sec",
            "range": "stddev: 0.007213639504535034",
            "extra": "mean: 2.293318404670548 msec\nrounds: 1219"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1373.8840265762071,
            "unit": "iter/sec",
            "range": "stddev: 0.0032060488687752848",
            "extra": "mean: 727.8634736674636 usec\nrounds: 1029"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15337.74151798859,
            "unit": "iter/sec",
            "range": "stddev: 0.000006963476054140234",
            "extra": "mean: 65.19864732543368 usec\nrounds: 2267"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28531.35747061809,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034750416932894482",
            "extra": "mean: 35.04915603927402 usec\nrounds: 6280"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2263.5988211583435,
            "unit": "iter/sec",
            "range": "stddev: 0.0000273650136398612",
            "extra": "mean: 441.7743951148876 usec\nrounds: 1076"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 113137.75215412347,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019832113611104543",
            "extra": "mean: 8.838782642930152 usec\nrounds: 20818"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 43755.61646202159,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026247056655208598",
            "extra": "mean: 22.85420891893882 usec\nrounds: 10409"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 56943.81264054097,
            "unit": "iter/sec",
            "range": "stddev: 0.000002812265376940856",
            "extra": "mean: 17.561170452574387 usec\nrounds: 15469"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 69998.44033657295,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021806497654717935",
            "extra": "mean: 14.286032591465007 usec\nrounds: 13596"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 97237.63559427862,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018964935032845698",
            "extra": "mean: 10.28408387234417 usec\nrounds: 12894"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1362.3792898695483,
            "unit": "iter/sec",
            "range": "stddev: 0.004457616916483005",
            "extra": "mean: 734.0099834428289 usec\nrounds: 319"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 1003.2913581301744,
            "unit": "iter/sec",
            "range": "stddev: 0.0070358771814879205",
            "extra": "mean: 996.7194393697275 usec\nrounds: 2392"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 252962.83404530818,
            "unit": "iter/sec",
            "range": "stddev: 5.920902958640144e-7",
            "extra": "mean: 3.953149891659143 usec\nrounds: 24943"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 594.8087833346194,
            "unit": "iter/sec",
            "range": "stddev: 0.06267285357058042",
            "extra": "mean: 1.681212564471217 msec\nrounds: 8875"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 156013.52053161728,
            "unit": "iter/sec",
            "range": "stddev: 9.216774226236654e-7",
            "extra": "mean: 6.409700881003725 usec\nrounds: 19537"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 9764.113358381022,
            "unit": "iter/sec",
            "range": "stddev: 0.0024971980676500665",
            "extra": "mean: 102.41585316516735 usec\nrounds: 14607"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2473.6612685887435,
            "unit": "iter/sec",
            "range": "stddev: 0.004930031021992977",
            "extra": "mean: 404.2590684093596 usec\nrounds: 3183"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 2040.2830463088642,
            "unit": "iter/sec",
            "range": "stddev: 0.004761252955148938",
            "extra": "mean: 490.1280740479265 usec\nrounds: 2112"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 4186.804545565412,
            "unit": "iter/sec",
            "range": "stddev: 0.0038472540292279417",
            "extra": "mean: 238.8456373152604 usec\nrounds: 4664"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 364548.7474149141,
            "unit": "iter/sec",
            "range": "stddev: 3.9195447076011675e-7",
            "extra": "mean: 2.743117366583191 usec\nrounds: 44011"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8606.55259501499,
            "unit": "iter/sec",
            "range": "stddev: 0.0024479980235009836",
            "extra": "mean: 116.190540749058 usec\nrounds: 9219"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37297.69959849981,
            "unit": "iter/sec",
            "range": "stddev: 0.000002351488325713015",
            "extra": "mean: 26.811305007138355 usec\nrounds: 10288"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 9309.372789461686,
            "unit": "iter/sec",
            "range": "stddev: 0.0022716359085124785",
            "extra": "mean: 107.4186223514447 usec\nrounds: 5738"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4439.147525449384,
            "unit": "iter/sec",
            "range": "stddev: 0.003934582856237865",
            "extra": "mean: 225.26847649623173 usec\nrounds: 6821"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4284.836287600985,
            "unit": "iter/sec",
            "range": "stddev: 0.003854970576923716",
            "extra": "mean: 233.38114524788176 usec\nrounds: 5422"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4353.699855575072,
            "unit": "iter/sec",
            "range": "stddev: 0.0037908891432920666",
            "extra": "mean: 229.68969684932767 usec\nrounds: 5071"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4422.620414001133,
            "unit": "iter/sec",
            "range": "stddev: 0.003299574373806229",
            "extra": "mean: 226.11029353416802 usec\nrounds: 1208"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1216960.5385169818,
            "unit": "iter/sec",
            "range": "stddev: 4.850533382252786e-7",
            "extra": "mean: 821.7193313586197 nsec\nrounds: 121625"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1231190.5884024177,
            "unit": "iter/sec",
            "range": "stddev: 1.3656177441412484e-7",
            "extra": "mean: 812.2219333219492 nsec\nrounds: 140628"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1224318.0958907783,
            "unit": "iter/sec",
            "range": "stddev: 4.1850192107924414e-7",
            "extra": "mean: 816.7811971058298 nsec\nrounds: 131389"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1239909.7240076114,
            "unit": "iter/sec",
            "range": "stddev: 1.5255215701028413e-7",
            "extra": "mean: 806.5103294519056 nsec\nrounds: 164150"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 84324.44320167316,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014149476344261543",
            "extra": "mean: 11.858957640649539 usec\nrounds: 11460"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 51303.4007504025,
            "unit": "iter/sec",
            "range": "stddev: 0.000003877703859908716",
            "extra": "mean: 19.49188524295155 usec\nrounds: 9502"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 32491.335533992413,
            "unit": "iter/sec",
            "range": "stddev: 0.000011355723035302985",
            "extra": "mean: 30.77743600147802 usec\nrounds: 148"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17432.311143190167,
            "unit": "iter/sec",
            "range": "stddev: 0.000007319635193513425",
            "extra": "mean: 57.364740210631474 usec\nrounds: 3691"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 21.70849306836102,
            "unit": "iter/sec",
            "range": "stddev: 0.32189150924128995",
            "extra": "mean: 46.06492016055445 msec\nrounds: 185"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 48.39135320088332,
            "unit": "iter/sec",
            "range": "stddev: 0.03885984165456328",
            "extra": "mean: 20.66484885943934 msec\nrounds: 187"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 56.27269474473359,
            "unit": "iter/sec",
            "range": "stddev: 0.028015655074623735",
            "extra": "mean: 17.770608010443418 msec\nrounds: 182"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 54.77412893879568,
            "unit": "iter/sec",
            "range": "stddev: 0.02892640807496047",
            "extra": "mean: 18.25679420876587 msec\nrounds: 186"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 22014.262645563256,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026733397969031872",
            "extra": "mean: 45.42509627055529 usec\nrounds: 12122"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17047.442263178775,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028652482271988688",
            "extra": "mean: 58.659826181662844 usec\nrounds: 9418"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21843.563937407816,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018696700299736488",
            "extra": "mean: 45.780075214167205 usec\nrounds: 13126"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4263.735340957143,
            "unit": "iter/sec",
            "range": "stddev: 0.000011117431958243213",
            "extra": "mean: 234.5361332337094 usec\nrounds: 2458"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4571.397429110013,
            "unit": "iter/sec",
            "range": "stddev: 0.003849037619955643",
            "extra": "mean: 218.7514902187548 usec\nrounds: 17209"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 423022.39849993394,
            "unit": "iter/sec",
            "range": "stddev: 3.2772583346199174e-7",
            "extra": "mean: 2.3639410195442787 usec\nrounds: 77924"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 4221.71789050792,
            "unit": "iter/sec",
            "range": "stddev: 0.003935943193108986",
            "extra": "mean: 236.87039871811254 usec\nrounds: 6075"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4112.451825872513,
            "unit": "iter/sec",
            "range": "stddev: 0.000025309066053417318",
            "extra": "mean: 243.16394266523386 usec\nrounds: 1081"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3585.509942796578,
            "unit": "iter/sec",
            "range": "stddev: 0.00002073536691425089",
            "extra": "mean: 278.900356142935 usec\nrounds: 1221"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5045.087289052203,
            "unit": "iter/sec",
            "range": "stddev: 0.000015566324532867037",
            "extra": "mean: 198.21262600748088 usec\nrounds: 3019"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5046.790564615741,
            "unit": "iter/sec",
            "range": "stddev: 0.000012970620455139661",
            "extra": "mean: 198.1457298845012 usec\nrounds: 2763"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21976.09108224283,
            "unit": "iter/sec",
            "range": "stddev: 0.000004023360382686009",
            "extra": "mean: 45.50399778821549 usec\nrounds: 12688"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21877.579810557305,
            "unit": "iter/sec",
            "range": "stddev: 0.000004283393504130151",
            "extra": "mean: 45.708895072453906 usec\nrounds: 11412"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21881.538651412928,
            "unit": "iter/sec",
            "range": "stddev: 0.000007813834353577437",
            "extra": "mean: 45.700625350467675 usec\nrounds: 13038"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21975.2383294795,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034641836366820442",
            "extra": "mean: 45.5057635783869 usec\nrounds: 14466"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 221.5732745876023,
            "unit": "iter/sec",
            "range": "stddev: 0.0093771845206702",
            "extra": "mean: 4.513179677744191 msec\nrounds: 77"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 339.73741297027783,
            "unit": "iter/sec",
            "range": "stddev: 0.003626058868530104",
            "extra": "mean: 2.9434497403660567 msec\nrounds: 877"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 215761.8567576188,
            "unit": "iter/sec",
            "range": "stddev: 0.000020721953034919595",
            "extra": "mean: 4.6347394995000135 usec\nrounds: 36660"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 953366.6527545562,
            "unit": "iter/sec",
            "range": "stddev: 6.843564690980018e-7",
            "extra": "mean: 1.0489143889297015 usec\nrounds: 64136"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 53.111916059250724,
            "unit": "iter/sec",
            "range": "stddev: 0.002602241456215161",
            "extra": "mean: 18.82816652452187 msec\nrounds: 82"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 112.21248863460333,
            "unit": "iter/sec",
            "range": "stddev: 0.0015612361498989111",
            "extra": "mean: 8.911664041747548 msec\nrounds: 49"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 158098.57329580313,
            "unit": "iter/sec",
            "range": "stddev: 7.774581794676675e-7",
            "extra": "mean: 6.325167768142952 usec\nrounds: 23831"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 121526.37256491746,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018387406705057748",
            "extra": "mean: 8.228666575774042 usec\nrounds: 4553"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 70169.50286404278,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015629024231654015",
            "extra": "mean: 14.251205426630346 usec\nrounds: 12460"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82132.28895752587,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014368908080303814",
            "extra": "mean: 12.175479494028748 usec\nrounds: 14335"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2584.835232991652,
            "unit": "iter/sec",
            "range": "stddev: 0.004240450267189868",
            "extra": "mean: 386.8718544363905 usec\nrounds: 2650"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 791.3493851016099,
            "unit": "iter/sec",
            "range": "stddev: 0.009272984797243986",
            "extra": "mean: 1.2636643419791111 msec\nrounds: 1608"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4618.709570243215,
            "unit": "iter/sec",
            "range": "stddev: 0.000036260338315431424",
            "extra": "mean: 216.5106908740619 usec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4532.1459837950715,
            "unit": "iter/sec",
            "range": "stddev: 0.000027092931457856407",
            "extra": "mean: 220.6460258728543 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1355.1505560932594,
            "unit": "iter/sec",
            "range": "stddev: 0.00032144928624938543",
            "extra": "mean: 737.9253880711846 usec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 225.9926940588371,
            "unit": "iter/sec",
            "range": "stddev: 0.0007050287655808874",
            "extra": "mean: 4.424921806275961 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 8970.479581446323,
            "unit": "iter/sec",
            "range": "stddev: 0.000024616564908693367",
            "extra": "mean: 111.47676006846989 usec\nrounds: 3696"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7160.855540854298,
            "unit": "iter/sec",
            "range": "stddev: 0.00004990698699048823",
            "extra": "mean: 139.64811806281725 usec\nrounds: 3604"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 295.1262060884549,
            "unit": "iter/sec",
            "range": "stddev: 0.0016273220134045254",
            "extra": "mean: 3.3883809006790844 msec\nrounds: 260"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7632.8802574591455,
            "unit": "iter/sec",
            "range": "stddev: 0.000020879780178170038",
            "extra": "mean: 131.01214302723554 usec\nrounds: 2444"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1747.2683287838336,
            "unit": "iter/sec",
            "range": "stddev: 0.00003284445723869762",
            "extra": "mean: 572.3219402116896 usec\nrounds: 1063"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6820.65330509302,
            "unit": "iter/sec",
            "range": "stddev: 0.00001598665458992059",
            "extra": "mean: 146.61352150142193 usec\nrounds: 350"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 9362.685331162953,
            "unit": "iter/sec",
            "range": "stddev: 0.000018371682172650187",
            "extra": "mean: 106.80696452240893 usec\nrounds: 4192"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8136.465412548717,
            "unit": "iter/sec",
            "range": "stddev: 0.00001864014860776953",
            "extra": "mean: 122.90349055717965 usec\nrounds: 2728"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6493.426103429888,
            "unit": "iter/sec",
            "range": "stddev: 0.0000443263340446308",
            "extra": "mean: 154.00190655466008 usec\nrounds: 345"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2699.5815815464343,
            "unit": "iter/sec",
            "range": "stddev: 0.00004109079702381108",
            "extra": "mean: 370.4277754877694 usec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 4317.145388234561,
            "unit": "iter/sec",
            "range": "stddev: 0.00004305449988806611",
            "extra": "mean: 231.6345432158208 usec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7317.618667683232,
            "unit": "iter/sec",
            "range": "stddev: 0.000036633426574894894",
            "extra": "mean: 136.65647875534913 usec\nrounds: 2798"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1160.076421551594,
            "unit": "iter/sec",
            "range": "stddev: 0.000045812450121220436",
            "extra": "mean: 862.012175596593 usec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 271.9088915492809,
            "unit": "iter/sec",
            "range": "stddev: 0.00023680246312723224",
            "extra": "mean: 3.677702462402777 msec\nrounds: 228"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.040126586089976,
            "unit": "iter/sec",
            "range": "stddev: 0.004792344556853122",
            "extra": "mean: 17.229459320987463 msec\nrounds: 57"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 46.86726873410088,
            "unit": "iter/sec",
            "range": "stddev: 0.0033485919844787157",
            "extra": "mean: 21.33685249877586 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.29876898093833,
            "unit": "iter/sec",
            "range": "stddev: 0.004436743439004029",
            "extra": "mean: 51.816776551277144 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 4.128641489069765,
            "unit": "iter/sec",
            "range": "stddev: 0.7218046253135696",
            "extra": "mean: 242.21042264081703 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 21.358146662858772,
            "unit": "iter/sec",
            "range": "stddev: 0.015184186658070078",
            "extra": "mean: 46.82054186559981 msec\nrounds: 8"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 44.537700315797046,
            "unit": "iter/sec",
            "range": "stddev: 0.014642212376014378",
            "extra": "mean: 22.452888068073662 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 7025.227297722764,
            "unit": "iter/sec",
            "range": "stddev: 0.00001857985427412312",
            "extra": "mean: 142.34414882549797 usec\nrounds: 3651"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1465.844772313309,
            "unit": "iter/sec",
            "range": "stddev: 0.00016482260091961503",
            "extra": "mean: 682.2004750351973 usec\nrounds: 49"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4527.834811673933,
            "unit": "iter/sec",
            "range": "stddev: 0.00002043082020697251",
            "extra": "mean: 220.85611370400278 usec\nrounds: 916"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 459.9615505235274,
            "unit": "iter/sec",
            "range": "stddev: 0.0016477528674486155",
            "extra": "mean: 2.1740947669686776 msec\nrounds: 639"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 443.27569612064815,
            "unit": "iter/sec",
            "range": "stddev: 0.00022020214800112876",
            "extra": "mean: 2.2559323886952423 msec\nrounds: 307"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 66.05566436268367,
            "unit": "iter/sec",
            "range": "stddev: 0.0017665311483000073",
            "extra": "mean: 15.138747140736086 msec\nrounds: 80"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 58.73527663669652,
            "unit": "iter/sec",
            "range": "stddev: 0.006022470635758444",
            "extra": "mean: 17.02554337464756 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.944498343215535,
            "unit": "iter/sec",
            "range": "stddev: 0.004324488322195524",
            "extra": "mean: 30.354081873762578 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 63.30312191803463,
            "unit": "iter/sec",
            "range": "stddev: 0.0023849131416251133",
            "extra": "mean: 15.797009210616938 msec\nrounds: 19"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 64.720521017017,
            "unit": "iter/sec",
            "range": "stddev: 0.0021328657119981075",
            "extra": "mean: 15.451049903276726 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 626.6895861463485,
            "unit": "iter/sec",
            "range": "stddev: 0.0004668678353051836",
            "extra": "mean: 1.5956863207975402 msec\nrounds: 492"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 63.84397296175761,
            "unit": "iter/sec",
            "range": "stddev: 0.0026062757074190356",
            "extra": "mean: 15.663185632244375 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 61.32727822783204,
            "unit": "iter/sec",
            "range": "stddev: 0.002546299261473022",
            "extra": "mean: 16.30595762435405 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 641.8564226089902,
            "unit": "iter/sec",
            "range": "stddev: 0.0001767039948909436",
            "extra": "mean: 1.5579808268261044 msec\nrounds: 456"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 45.70593952979562,
            "unit": "iter/sec",
            "range": "stddev: 0.0022835904144574842",
            "extra": "mean: 21.878994508976273 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 21.68371548164238,
            "unit": "iter/sec",
            "range": "stddev: 0.0027695075320342305",
            "extra": "mean: 46.11755770576351 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 20.65824509515943,
            "unit": "iter/sec",
            "range": "stddev: 0.0051237937793289865",
            "extra": "mean: 48.40682233140493 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 18.476692051034494,
            "unit": "iter/sec",
            "range": "stddev: 0.0036146277778779977",
            "extra": "mean: 54.122242078717264 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 18.63917964128962,
            "unit": "iter/sec",
            "range": "stddev: 0.005085150828813487",
            "extra": "mean: 53.6504298603783 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 81.21006127379702,
            "unit": "iter/sec",
            "range": "stddev: 0.00044648168426278227",
            "extra": "mean: 12.313745172886067 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 80.66882188829872,
            "unit": "iter/sec",
            "range": "stddev: 0.00040358796555806396",
            "extra": "mean: 12.396363013515801 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 80.69564672484414,
            "unit": "iter/sec",
            "range": "stddev: 0.0005275331834991333",
            "extra": "mean: 12.39224221611109 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 76.35152941248982,
            "unit": "iter/sec",
            "range": "stddev: 0.0005472871889878706",
            "extra": "mean: 13.09731458812686 msec\nrounds: 63"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 64.58838016098176,
            "unit": "iter/sec",
            "range": "stddev: 0.005146588608134212",
            "extra": "mean: 15.482661084045985 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 572.3438033767052,
            "unit": "iter/sec",
            "range": "stddev: 0.00014170135356224447",
            "extra": "mean: 1.7472015842579502 msec\nrounds: 453"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 58.93200453763238,
            "unit": "iter/sec",
            "range": "stddev: 0.002207812567724363",
            "extra": "mean: 16.96870839276182 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 60.05090843690911,
            "unit": "iter/sec",
            "range": "stddev: 0.001995903136982536",
            "extra": "mean: 16.652537422487512 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 60.06800688594386,
            "unit": "iter/sec",
            "range": "stddev: 0.0025561148922752575",
            "extra": "mean: 16.647797252517194 msec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 63.178091960478405,
            "unit": "iter/sec",
            "range": "stddev: 0.0018988424096387096",
            "extra": "mean: 15.82827162025657 msec\nrounds: 58"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 695.5851423737984,
            "unit": "iter/sec",
            "range": "stddev: 0.0001245522677038903",
            "extra": "mean: 1.4376385277398767 msec\nrounds: 445"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 656.1927543074924,
            "unit": "iter/sec",
            "range": "stddev: 0.0001263051700192118",
            "extra": "mean: 1.5239424596441056 msec\nrounds: 477"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 679.1910462727701,
            "unit": "iter/sec",
            "range": "stddev: 0.00012660407115284292",
            "extra": "mean: 1.472339786408771 msec\nrounds: 506"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 61.10405597802862,
            "unit": "iter/sec",
            "range": "stddev: 0.0020831525343982618",
            "extra": "mean: 16.36552572483197 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 52.34719515743625,
            "unit": "iter/sec",
            "range": "stddev: 0.003206260591760705",
            "extra": "mean: 19.10322027746588 msec\nrounds: 50"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 67.62196274150057,
            "unit": "iter/sec",
            "range": "stddev: 0.0026294115751465588",
            "extra": "mean: 14.788094865313422 msec\nrounds: 60"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 60.302576569293294,
            "unit": "iter/sec",
            "range": "stddev: 0.003566960918355503",
            "extra": "mean: 16.58303934742998 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 66.52690290254681,
            "unit": "iter/sec",
            "range": "stddev: 0.0020995573518644726",
            "extra": "mean: 15.031512912375748 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 645.0763871918936,
            "unit": "iter/sec",
            "range": "stddev: 0.00013605677747656253",
            "extra": "mean: 1.5502040066187166 msec\nrounds: 450"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 739.137312143624,
            "unit": "iter/sec",
            "range": "stddev: 0.00010460527350698946",
            "extra": "mean: 1.35292858792344 msec\nrounds: 507"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 270.44893795808196,
            "unit": "iter/sec",
            "range": "stddev: 0.0021781634630890366",
            "extra": "mean: 3.6975556552379376 msec\nrounds: 212"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 658.2702783519527,
            "unit": "iter/sec",
            "range": "stddev: 0.00019592226772363448",
            "extra": "mean: 1.519132843888384 msec\nrounds: 482"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 714.552847458206,
            "unit": "iter/sec",
            "range": "stddev: 0.00013301712019239448",
            "extra": "mean: 1.3994766147209143 msec\nrounds: 545"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 80.70992833473346,
            "unit": "iter/sec",
            "range": "stddev: 0.00340331900158483",
            "extra": "mean: 12.39004941068261 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 100.08181135849476,
            "unit": "iter/sec",
            "range": "stddev: 0.0004132141514778887",
            "extra": "mean: 9.991825551777664 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 127.05665108188354,
            "unit": "iter/sec",
            "range": "stddev: 0.00041464410672097384",
            "extra": "mean: 7.87050494000141 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 113.7842827893438,
            "unit": "iter/sec",
            "range": "stddev: 0.0005289675925210265",
            "extra": "mean: 8.78856003206844 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 117.4186075099263,
            "unit": "iter/sec",
            "range": "stddev: 0.0003995192029687573",
            "extra": "mean: 8.516537720952467 msec\nrounds: 131"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 115.14215330313371,
            "unit": "iter/sec",
            "range": "stddev: 0.0004464568525049861",
            "extra": "mean: 8.684916612314076 msec\nrounds: 117"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 117.20269857974529,
            "unit": "iter/sec",
            "range": "stddev: 0.0006473324474380156",
            "extra": "mean: 8.532226750048721 msec\nrounds: 128"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 124.8540113655275,
            "unit": "iter/sec",
            "range": "stddev: 0.0007739252836135306",
            "extra": "mean: 8.009354197458348 msec\nrounds: 122"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 247.27104507361167,
            "unit": "iter/sec",
            "range": "stddev: 0.0003588596270777448",
            "extra": "mean: 4.044145159423351 msec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 6375.457411968196,
            "unit": "iter/sec",
            "range": "stddev: 0.00003183981990787577",
            "extra": "mean: 156.85149086287842 usec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 8558.65344206529,
            "unit": "iter/sec",
            "range": "stddev: 0.0000213226460597559",
            "extra": "mean: 116.8408099205253 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 25.73548468435278,
            "unit": "iter/sec",
            "range": "stddev: 0.10311429588411991",
            "extra": "mean: 38.85685512688252 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 80.64057575068271,
            "unit": "iter/sec",
            "range": "stddev: 0.0037844641476500597",
            "extra": "mean: 12.40070511266822 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 648.4993759530058,
            "unit": "iter/sec",
            "range": "stddev: 0.00014455172027669905",
            "extra": "mean: 1.542021530137087 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 647.5237695877737,
            "unit": "iter/sec",
            "range": "stddev: 0.00015123339834476437",
            "extra": "mean: 1.5443448518293306 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 66.29003629993115,
            "unit": "iter/sec",
            "range": "stddev: 0.0021907692404909067",
            "extra": "mean: 15.085223297743749 msec\nrounds: 30"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "be464da7bc6900d0364a2b0a097691df24be3b96",
          "message": "Update artifact download steps in bench-rpi workflow",
          "timestamp": "2026-03-12T17:47:21+09:00",
          "tree_id": "205551290815e0d3097f09ddf4e95d5d5092f2c1",
          "url": "https://github.com/disnana/NanaSQLite/commit/be464da7bc6900d0364a2b0a097691df24be3b96"
        },
        "date": 1773305553790,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4380.044677847633,
            "unit": "iter/sec",
            "range": "stddev: 0.004134811121791514",
            "extra": "mean: 228.3081734434278 usec\nrounds: 4888"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4102.726168942108,
            "unit": "iter/sec",
            "range": "stddev: 0.004422541374481605",
            "extra": "mean: 243.74037135845478 usec\nrounds: 7939"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 662.5142863825345,
            "unit": "iter/sec",
            "range": "stddev: 0.011245662604284874",
            "extra": "mean: 1.509401413002288 msec\nrounds: 1496"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2382515.363321835,
            "unit": "iter/sec",
            "range": "stddev: 5.541593712104669e-8",
            "extra": "mean: 419.72447078189856 nsec\nrounds: 132680"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 88213.13372091299,
            "unit": "iter/sec",
            "range": "stddev: 0.000001706729667789224",
            "extra": "mean: 11.336180428231705 usec\nrounds: 8884"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 496.37798022800416,
            "unit": "iter/sec",
            "range": "stddev: 0.00016490063295452944",
            "extra": "mean: 2.014593797131501 msec\nrounds: 188"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2774.272383090001,
            "unit": "iter/sec",
            "range": "stddev: 0.000019682474672511535",
            "extra": "mean: 360.4548731751401 usec\nrounds: 1451"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2403762.0682264767,
            "unit": "iter/sec",
            "range": "stddev: 1.0168971212178961e-7",
            "extra": "mean: 416.01455203002325 nsec\nrounds: 155618"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 117438.20166541,
            "unit": "iter/sec",
            "range": "stddev: 0.00000147267432287604",
            "extra": "mean: 8.515116766255266 usec\nrounds: 8260"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 76670.60933929861,
            "unit": "iter/sec",
            "range": "stddev: 6.665624829685099e-7",
            "extra": "mean: 13.042807519301086 usec\nrounds: 304"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 71702.909775308,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016362939930866873",
            "extra": "mean: 13.94643541152866 usec\nrounds: 17253"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5663900.470100968,
            "unit": "iter/sec",
            "range": "stddev: 1.626457605503968e-8",
            "extra": "mean: 176.55677483736721 nsec\nrounds: 133654"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1478572.1276167673,
            "unit": "iter/sec",
            "range": "stddev: 2.317323946808079e-7",
            "extra": "mean: 676.3281826581212 nsec\nrounds: 3609"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 81682.61159524253,
            "unit": "iter/sec",
            "range": "stddev: 8.566058329459128e-7",
            "extra": "mean: 12.242507682727462 usec\nrounds: 338"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 71251.02480489464,
            "unit": "iter/sec",
            "range": "stddev: 0.000001298692208740943",
            "extra": "mean: 14.034885852354847 usec\nrounds: 15055"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3285.1814307734735,
            "unit": "iter/sec",
            "range": "stddev: 0.005703493898567315",
            "extra": "mean: 304.3971911665642 usec\nrounds: 5727"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4604.19831724011,
            "unit": "iter/sec",
            "range": "stddev: 0.004006285265765641",
            "extra": "mean: 217.19307707827605 usec\nrounds: 8879"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51360.65726791042,
            "unit": "iter/sec",
            "range": "stddev: 0.000003034270682611481",
            "extra": "mean: 19.470155819536 usec\nrounds: 10610"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9079.207690454723,
            "unit": "iter/sec",
            "range": "stddev: 0.002544717926539754",
            "extra": "mean: 110.14176942458688 usec\nrounds: 8466"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7523.130260149086,
            "unit": "iter/sec",
            "range": "stddev: 0.00001513794509266608",
            "extra": "mean: 132.9233929787337 usec\nrounds: 1046"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12507.331969547477,
            "unit": "iter/sec",
            "range": "stddev: 0.000005766565937341333",
            "extra": "mean: 79.95310290274327 usec\nrounds: 3801"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21917.433518230762,
            "unit": "iter/sec",
            "range": "stddev: 0.000004292648892537233",
            "extra": "mean: 45.62578000604894 usec\nrounds: 5479"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8303.592968016825,
            "unit": "iter/sec",
            "range": "stddev: 0.0000077867894402554",
            "extra": "mean: 120.42979513226713 usec\nrounds: 3969"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 7758.316373165442,
            "unit": "iter/sec",
            "range": "stddev: 0.0028926167490139895",
            "extra": "mean: 128.89394449790834 usec\nrounds: 7337"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2092.3049577490656,
            "unit": "iter/sec",
            "range": "stddev: 0.005227565728745693",
            "extra": "mean: 477.9418011205287 usec\nrounds: 4093"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2092.824282152779,
            "unit": "iter/sec",
            "range": "stddev: 0.005296979595496208",
            "extra": "mean: 477.82320213302967 usec\nrounds: 3074"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2211.508299466445,
            "unit": "iter/sec",
            "range": "stddev: 0.0048665784640612225",
            "extra": "mean: 452.1800801024636 usec\nrounds: 3458"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 417.72326803389996,
            "unit": "iter/sec",
            "range": "stddev: 0.007834865311224336",
            "extra": "mean: 2.3939293702902993 msec\nrounds: 1270"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1311.8249856336301,
            "unit": "iter/sec",
            "range": "stddev: 0.003952033646613788",
            "extra": "mean: 762.296808607427 usec\nrounds: 995"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15263.659278577074,
            "unit": "iter/sec",
            "range": "stddev: 0.000006914814179313569",
            "extra": "mean: 65.51508925540057 usec\nrounds: 2264"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28571.574970749167,
            "unit": "iter/sec",
            "range": "stddev: 0.000003894305744983744",
            "extra": "mean: 34.999820661751194 usec\nrounds: 6245"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2331.7624950966733,
            "unit": "iter/sec",
            "range": "stddev: 0.00002531588486884864",
            "extra": "mean: 428.8601442483278 usec\nrounds: 1111"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 114005.7123290925,
            "unit": "iter/sec",
            "range": "stddev: 0.000001107546990789189",
            "extra": "mean: 8.771490301410234 usec\nrounds: 18399"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44513.866712696035,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027257336325366056",
            "extra": "mean: 22.46490978764567 usec\nrounds: 12054"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 57845.02163864183,
            "unit": "iter/sec",
            "range": "stddev: 0.000002410344289213112",
            "extra": "mean: 17.287572407648245 usec\nrounds: 14092"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70829.61296070016,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020347790240726883",
            "extra": "mean: 14.118388597645598 usec\nrounds: 13440"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 97713.53303735658,
            "unit": "iter/sec",
            "range": "stddev: 0.000001955341611579749",
            "extra": "mean: 10.233996959435423 usec\nrounds: 13162"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1371.1347323897269,
            "unit": "iter/sec",
            "range": "stddev: 0.0046499835801591905",
            "extra": "mean: 729.3229296708992 usec\nrounds: 345"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 905.8688739775536,
            "unit": "iter/sec",
            "range": "stddev: 0.00811565985887484",
            "extra": "mean: 1.1039125294250687 msec\nrounds: 1462"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 255998.32858401776,
            "unit": "iter/sec",
            "range": "stddev: 5.722353419244813e-7",
            "extra": "mean: 3.9062755039504236 usec\nrounds: 26920"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4702.971829925483,
            "unit": "iter/sec",
            "range": "stddev: 0.00388569122476947",
            "extra": "mean: 212.63150964181827 usec\nrounds: 9330"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 155998.74530004276,
            "unit": "iter/sec",
            "range": "stddev: 8.69965474176542e-7",
            "extra": "mean: 6.410307968032906 usec\nrounds: 15302"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 8425.660182788042,
            "unit": "iter/sec",
            "range": "stddev: 0.002982678679807338",
            "extra": "mean: 118.68506185934274 usec\nrounds: 12981"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2531.0798334932033,
            "unit": "iter/sec",
            "range": "stddev: 0.004903029138443525",
            "extra": "mean: 395.0882887087272 usec\nrounds: 2979"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 2039.897645226553,
            "unit": "iter/sec",
            "range": "stddev: 0.005085227841541805",
            "extra": "mean: 490.22067471867643 usec\nrounds: 1906"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 4213.686666956873,
            "unit": "iter/sec",
            "range": "stddev: 0.004011893934484389",
            "extra": "mean: 237.3218701432778 usec\nrounds: 3906"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 359321.43752633664,
            "unit": "iter/sec",
            "range": "stddev: 8.921591672540767e-7",
            "extra": "mean: 2.783023486948798 usec\nrounds: 47329"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 7890.731092946549,
            "unit": "iter/sec",
            "range": "stddev: 0.0027579021933138385",
            "extra": "mean: 126.73096931333657 usec\nrounds: 9050"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37281.04247704381,
            "unit": "iter/sec",
            "range": "stddev: 0.00000264333300473494",
            "extra": "mean: 26.823284263463407 usec\nrounds: 9741"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 8614.10745533737,
            "unit": "iter/sec",
            "range": "stddev: 0.002541569591497914",
            "extra": "mean: 116.08863775902773 usec\nrounds: 6795"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4221.048656321743,
            "unit": "iter/sec",
            "range": "stddev: 0.00428907677777787",
            "extra": "mean: 236.90795378592207 usec\nrounds: 6235"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4053.3285779751986,
            "unit": "iter/sec",
            "range": "stddev: 0.004192433369075195",
            "extra": "mean: 246.71081575615574 usec\nrounds: 5492"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 3642.704954908154,
            "unit": "iter/sec",
            "range": "stddev: 0.004983146547266383",
            "extra": "mean: 274.5212726198446 usec\nrounds: 4389"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4201.0209748972065,
            "unit": "iter/sec",
            "range": "stddev: 0.003715001002180478",
            "extra": "mean: 238.03737376590195 usec\nrounds: 1263"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1228190.779188491,
            "unit": "iter/sec",
            "range": "stddev: 1.399656305315606e-7",
            "extra": "mean: 814.2057544681578 nsec\nrounds: 109314"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1230562.9076665055,
            "unit": "iter/sec",
            "range": "stddev: 1.8552050203470048e-7",
            "extra": "mean: 812.6362283227617 nsec\nrounds: 132363"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1234886.077018328,
            "unit": "iter/sec",
            "range": "stddev: 1.9183633376598477e-7",
            "extra": "mean: 809.7912986552833 nsec\nrounds: 140628"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1240171.6047947204,
            "unit": "iter/sec",
            "range": "stddev: 2.587409468962568e-7",
            "extra": "mean: 806.3400227305841 nsec\nrounds: 167702"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 84780.30530485035,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017673432650393054",
            "extra": "mean: 11.79519224900443 usec\nrounds: 10866"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 58883.300468289905,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031897359364109783",
            "extra": "mean: 16.982743698929113 usec\nrounds: 7857"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 53911.93627615846,
            "unit": "iter/sec",
            "range": "stddev: 0.000003066676044663068",
            "extra": "mean: 18.54876802935811 usec\nrounds: 8127"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17513.46859919303,
            "unit": "iter/sec",
            "range": "stddev: 0.000008648916227998755",
            "extra": "mean: 57.09891186524165 usec\nrounds: 4248"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 51.46035732011907,
            "unit": "iter/sec",
            "range": "stddev: 0.03147044279494678",
            "extra": "mean: 19.432434053640694 msec\nrounds: 189"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 51.42470976051363,
            "unit": "iter/sec",
            "range": "stddev: 0.031772522287138685",
            "extra": "mean: 19.44590459833471 msec\nrounds: 183"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 49.7746162217257,
            "unit": "iter/sec",
            "range": "stddev: 0.033075157981972095",
            "extra": "mean: 20.09056173422626 msec\nrounds: 192"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 49.493061123916895,
            "unit": "iter/sec",
            "range": "stddev: 0.032792064504910325",
            "extra": "mean: 20.20485250440011 msec\nrounds: 184"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 22324.839649250538,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027403134174299786",
            "extra": "mean: 44.793154876414576 usec\nrounds: 13304"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17269.468362524698,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027897959679814302",
            "extra": "mean: 57.905662120440965 usec\nrounds: 9501"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21965.309150146124,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017112922934724298",
            "extra": "mean: 45.5263339643616 usec\nrounds: 13779"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4343.802738146969,
            "unit": "iter/sec",
            "range": "stddev: 0.000008145211894305503",
            "extra": "mean: 230.21303228575982 usec\nrounds: 2481"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 1356.4292377431443,
            "unit": "iter/sec",
            "range": "stddev: 0.04774803083267119",
            "extra": "mean: 737.2297589690866 usec\nrounds: 16802"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 425698.73967472895,
            "unit": "iter/sec",
            "range": "stddev: 6.314700487824464e-7",
            "extra": "mean: 2.3490790711856167 usec\nrounds: 80238"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 3863.2062036601747,
            "unit": "iter/sec",
            "range": "stddev: 0.004503772334926699",
            "extra": "mean: 258.85234887347076 usec\nrounds: 6084"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4054.653591414591,
            "unit": "iter/sec",
            "range": "stddev: 0.00021089838522503647",
            "extra": "mean: 246.63019354290117 usec\nrounds: 1089"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3596.4706685825427,
            "unit": "iter/sec",
            "range": "stddev: 0.0000228701890692361",
            "extra": "mean: 278.05036997399577 usec\nrounds: 1215"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 4715.090588313391,
            "unit": "iter/sec",
            "range": "stddev: 0.0007991562066562433",
            "extra": "mean: 212.08500266751068 usec\nrounds: 2797"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5197.506462829132,
            "unit": "iter/sec",
            "range": "stddev: 0.000012758510925568401",
            "extra": "mean: 192.39995316055365 usec\nrounds: 2699"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21942.32679438572,
            "unit": "iter/sec",
            "range": "stddev: 0.000004157214290632139",
            "extra": "mean: 45.574018169115284 usec\nrounds: 13268"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21852.588073992505,
            "unit": "iter/sec",
            "range": "stddev: 0.000004230795271461334",
            "extra": "mean: 45.76117010095173 usec\nrounds: 12256"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21791.27692047258,
            "unit": "iter/sec",
            "range": "stddev: 0.000007682503673872699",
            "extra": "mean: 45.88992208439675 usec\nrounds: 12757"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 22073.80418573279,
            "unit": "iter/sec",
            "range": "stddev: 0.000003815703526378948",
            "extra": "mean: 45.30256731399027 usec\nrounds: 13272"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 213.02560118681598,
            "unit": "iter/sec",
            "range": "stddev: 0.010459839556651989",
            "extra": "mean: 4.6942714604665525 msec\nrounds: 200"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 346.51676483251117,
            "unit": "iter/sec",
            "range": "stddev: 0.0032241870479901356",
            "extra": "mean: 2.8858632582563497 msec\nrounds: 820"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 223748.50394749478,
            "unit": "iter/sec",
            "range": "stddev: 0.000017912366229869965",
            "extra": "mean: 4.4693036259793795 usec\nrounds: 36388"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 930971.215410723,
            "unit": "iter/sec",
            "range": "stddev: 9.399550407941778e-7",
            "extra": "mean: 1.074147066468455 usec\nrounds: 61433"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 51.999029559964804,
            "unit": "iter/sec",
            "range": "stddev: 0.0032838349725173993",
            "extra": "mean: 19.231128128012642 msec\nrounds: 78"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 108.427893728633,
            "unit": "iter/sec",
            "range": "stddev: 0.0018732484275401225",
            "extra": "mean: 9.222719040385877 msec\nrounds: 52"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 156860.9687790783,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013833974347792332",
            "extra": "mean: 6.37507219153027 usec\nrounds: 21609"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 119676.5481271536,
            "unit": "iter/sec",
            "range": "stddev: 0.000002275940007736193",
            "extra": "mean: 8.35585597720886 usec\nrounds: 4481"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 70539.253823383,
            "unit": "iter/sec",
            "range": "stddev: 0.000002305749398290576",
            "extra": "mean: 14.176503801752874 usec\nrounds: 13490"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 83183.51353147457,
            "unit": "iter/sec",
            "range": "stddev: 0.000001892984140742678",
            "extra": "mean: 12.021612907966732 usec\nrounds: 15571"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2354.9307046450203,
            "unit": "iter/sec",
            "range": "stddev: 0.004918838650820203",
            "extra": "mean: 424.6409450721986 usec\nrounds: 2476"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 752.3216381701219,
            "unit": "iter/sec",
            "range": "stddev: 0.010524304209465988",
            "extra": "mean: 1.3292187134645073 msec\nrounds: 1755"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4434.085848326945,
            "unit": "iter/sec",
            "range": "stddev: 0.00005867575592913987",
            "extra": "mean: 225.52562900362355 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4741.581979743291,
            "unit": "iter/sec",
            "range": "stddev: 0.00001797122583742888",
            "extra": "mean: 210.90007602360168 usec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1379.8734177500387,
            "unit": "iter/sec",
            "range": "stddev: 0.00029913374582273873",
            "extra": "mean: 724.7041555670783 usec\nrounds: 39"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 191.30213754771907,
            "unit": "iter/sec",
            "range": "stddev: 0.004834271396592785",
            "extra": "mean: 5.227333122456912 msec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10366.817939694114,
            "unit": "iter/sec",
            "range": "stddev: 0.00001720015308930235",
            "extra": "mean: 96.46161491570538 usec\nrounds: 3921"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7202.1578517762455,
            "unit": "iter/sec",
            "range": "stddev: 0.000018354667518186417",
            "extra": "mean: 138.8472761331346 usec\nrounds: 2912"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 287.7094969538732,
            "unit": "iter/sec",
            "range": "stddev: 0.0002809436065334233",
            "extra": "mean: 3.475728158394174 msec\nrounds: 224"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7464.612219264753,
            "unit": "iter/sec",
            "range": "stddev: 0.000020840476263966294",
            "extra": "mean: 133.96543191074136 usec\nrounds: 2002"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1713.7295164731033,
            "unit": "iter/sec",
            "range": "stddev: 0.00003787096299537874",
            "extra": "mean: 583.522656514678 usec\nrounds: 788"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 7170.384301957899,
            "unit": "iter/sec",
            "range": "stddev: 0.000010205664596183258",
            "extra": "mean: 139.462538950241 usec\nrounds: 428"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 10290.783240538589,
            "unit": "iter/sec",
            "range": "stddev: 0.000010611081042969292",
            "extra": "mean: 97.17433324809424 usec\nrounds: 3760"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 7730.335100040814,
            "unit": "iter/sec",
            "range": "stddev: 0.000014588698300601101",
            "extra": "mean: 129.36049822661894 usec\nrounds: 2727"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 7039.83355087443,
            "unit": "iter/sec",
            "range": "stddev: 0.000016507500488998074",
            "extra": "mean: 142.0488130540797 usec\nrounds: 346"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2911.5196925972623,
            "unit": "iter/sec",
            "range": "stddev: 0.00004137558771300384",
            "extra": "mean: 343.46324448451037 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 4273.110246173583,
            "unit": "iter/sec",
            "range": "stddev: 0.000038500218001878824",
            "extra": "mean: 234.02157735000267 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7584.516561524996,
            "unit": "iter/sec",
            "range": "stddev: 0.000018230400679473016",
            "extra": "mean: 131.84755968136918 usec\nrounds: 3375"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1125.0742802878426,
            "unit": "iter/sec",
            "range": "stddev: 0.00010507106368513117",
            "extra": "mean: 888.8302021659911 usec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 270.62076156053223,
            "unit": "iter/sec",
            "range": "stddev: 0.00019887070642239034",
            "extra": "mean: 3.695207988601868 msec\nrounds: 189"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 59.00144917844101,
            "unit": "iter/sec",
            "range": "stddev: 0.004651611204709724",
            "extra": "mean: 16.948736241641292 msec\nrounds: 58"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 46.61661589010348,
            "unit": "iter/sec",
            "range": "stddev: 0.002395302922585666",
            "extra": "mean: 21.45157860359177 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.318415190262606,
            "unit": "iter/sec",
            "range": "stddev: 0.0032586551444495934",
            "extra": "mean: 51.764080549632624 msec\nrounds: 11"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 24.857851015974898,
            "unit": "iter/sec",
            "range": "stddev: 0.016452222640854303",
            "extra": "mean: 40.22873897495604 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 48.812238440709564,
            "unit": "iter/sec",
            "range": "stddev: 0.0023907578626418337",
            "extra": "mean: 20.48666547457485 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 61.01119104423807,
            "unit": "iter/sec",
            "range": "stddev: 0.006529832169369927",
            "extra": "mean: 16.39043563786386 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6976.265918751556,
            "unit": "iter/sec",
            "range": "stddev: 0.000017913062611084597",
            "extra": "mean: 143.34315974282072 usec\nrounds: 3896"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1735.6656621711566,
            "unit": "iter/sec",
            "range": "stddev: 0.000047387091212033015",
            "extra": "mean: 576.147827196796 usec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4266.2742772582715,
            "unit": "iter/sec",
            "range": "stddev: 0.000020125514159860783",
            "extra": "mean: 234.3965565764449 usec\nrounds: 1267"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 662.7866188257624,
            "unit": "iter/sec",
            "range": "stddev: 0.00011368806745654542",
            "extra": "mean: 1.5087812149431556 msec\nrounds: 510"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 466.1960872537236,
            "unit": "iter/sec",
            "range": "stddev: 0.00018492842022954469",
            "extra": "mean: 2.145020147832682 msec\nrounds: 326"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 67.05413964828297,
            "unit": "iter/sec",
            "range": "stddev: 0.002135069119281705",
            "extra": "mean: 14.913322357803255 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 60.89741707039931,
            "unit": "iter/sec",
            "range": "stddev: 0.0024120924903378344",
            "extra": "mean: 16.42105770830919 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 24.233737650654113,
            "unit": "iter/sec",
            "range": "stddev: 0.01876542442933087",
            "extra": "mean: 41.264786076984215 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 59.456248143733625,
            "unit": "iter/sec",
            "range": "stddev: 0.0033775884909667806",
            "extra": "mean: 16.819090191875738 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 65.44266014704428,
            "unit": "iter/sec",
            "range": "stddev: 0.002456594000444417",
            "extra": "mean: 15.280552437096569 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 661.2243717581463,
            "unit": "iter/sec",
            "range": "stddev: 0.00011056891450773491",
            "extra": "mean: 1.5123459489871411 msec\nrounds: 457"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 63.53654640949334,
            "unit": "iter/sec",
            "range": "stddev: 0.003423434598055145",
            "extra": "mean: 15.738973181749529 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 63.277845127125026,
            "unit": "iter/sec",
            "range": "stddev: 0.0030667886547667846",
            "extra": "mean: 15.803319439702832 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 647.1328372067383,
            "unit": "iter/sec",
            "range": "stddev: 0.0001482765189429068",
            "extra": "mean: 1.545277789203783 msec\nrounds: 431"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 43.564651012236006,
            "unit": "iter/sec",
            "range": "stddev: 0.003563846763608111",
            "extra": "mean: 22.95439023990184 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 21.730411704410173,
            "unit": "iter/sec",
            "range": "stddev: 0.001997775276649035",
            "extra": "mean: 46.018456235555384 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 19.889459413690542,
            "unit": "iter/sec",
            "range": "stddev: 0.013113176808193882",
            "extra": "mean: 50.277887357344085 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 21.966622470724566,
            "unit": "iter/sec",
            "range": "stddev: 0.0015918355841159997",
            "extra": "mean: 45.52361207703749 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 21.71222703970281,
            "unit": "iter/sec",
            "range": "stddev: 0.0032484726354494284",
            "extra": "mean: 46.05699812236708 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.84761015083643,
            "unit": "iter/sec",
            "range": "stddev: 0.00033301997258227783",
            "extra": "mean: 12.070354210330882 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 81.78587757013716,
            "unit": "iter/sec",
            "range": "stddev: 0.0005595707874854498",
            "extra": "mean: 12.227049824615865 msec\nrounds: 73"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 81.7963260381048,
            "unit": "iter/sec",
            "range": "stddev: 0.00044317604850428396",
            "extra": "mean: 12.225487970378405 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.11539522217217,
            "unit": "iter/sec",
            "range": "stddev: 0.000409363880576904",
            "extra": "mean: 12.967579263763932 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 64.14291442868698,
            "unit": "iter/sec",
            "range": "stddev: 0.002407968478807371",
            "extra": "mean: 15.590186521876603 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 568.4060399854787,
            "unit": "iter/sec",
            "range": "stddev: 0.00015044647245768416",
            "extra": "mean: 1.7593057245231725 msec\nrounds: 406"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 13.37884984183111,
            "unit": "iter/sec",
            "range": "stddev: 0.09050967180821147",
            "extra": "mean: 74.74484068677864 msec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 9.490191605314026,
            "unit": "iter/sec",
            "range": "stddev: 0.07021387521857213",
            "extra": "mean: 105.37195049255388 msec\nrounds: 8"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 11.79084235932043,
            "unit": "iter/sec",
            "range": "stddev: 0.01688001097306591",
            "extra": "mean: 84.81158254223621 msec\nrounds: 11"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 10.759382409146632,
            "unit": "iter/sec",
            "range": "stddev: 0.048652201070120214",
            "extra": "mean: 92.94213756636184 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 701.2427338163856,
            "unit": "iter/sec",
            "range": "stddev: 0.00010019842678580351",
            "extra": "mean: 1.4260397317169797 msec\nrounds: 499"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 659.0502922514621,
            "unit": "iter/sec",
            "range": "stddev: 0.00011182219744273329",
            "extra": "mean: 1.517334885906473 msec\nrounds: 415"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 671.8824366679781,
            "unit": "iter/sec",
            "range": "stddev: 0.00013363857107180215",
            "extra": "mean: 1.4883556191157987 msec\nrounds: 426"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 14.940958822330744,
            "unit": "iter/sec",
            "range": "stddev: 0.010322230630918352",
            "extra": "mean: 66.93010882978949 msec\nrounds: 6"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 10.530484346424446,
            "unit": "iter/sec",
            "range": "stddev: 0.0924550395515054",
            "extra": "mean: 94.9623936661131 msec\nrounds: 12"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 69.59256670196862,
            "unit": "iter/sec",
            "range": "stddev: 0.0017025838075514276",
            "extra": "mean: 14.369350742335994 msec\nrounds: 81"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 57.060820997963056,
            "unit": "iter/sec",
            "range": "stddev: 0.004352131672349088",
            "extra": "mean: 17.525159689442564 msec\nrounds: 75"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 64.90063938872493,
            "unit": "iter/sec",
            "range": "stddev: 0.005193162450394355",
            "extra": "mean: 15.408168693230598 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 650.8425345827133,
            "unit": "iter/sec",
            "range": "stddev: 0.00012573972250069538",
            "extra": "mean: 1.5364699552728964 msec\nrounds: 441"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 730.2385081862459,
            "unit": "iter/sec",
            "range": "stddev: 0.00010881667985331081",
            "extra": "mean: 1.3694155933843903 msec\nrounds: 522"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 268.73668690214976,
            "unit": "iter/sec",
            "range": "stddev: 0.002051424099091571",
            "extra": "mean: 3.7211145658133082 msec\nrounds: 246"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 665.7138988761167,
            "unit": "iter/sec",
            "range": "stddev: 0.00024893189681710266",
            "extra": "mean: 1.5021467956253245 msec\nrounds: 509"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 724.2262765913451,
            "unit": "iter/sec",
            "range": "stddev: 0.00011658505132278247",
            "extra": "mean: 1.3807839239230808 msec\nrounds: 499"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 82.2353467312756,
            "unit": "iter/sec",
            "range": "stddev: 0.003233246037155593",
            "extra": "mean: 12.160221118392656 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 99.73729233409009,
            "unit": "iter/sec",
            "range": "stddev: 0.0006279289357408894",
            "extra": "mean: 10.026339963694815 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 121.07201756380397,
            "unit": "iter/sec",
            "range": "stddev: 0.0008414602492029878",
            "extra": "mean: 8.259546839326504 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 119.79043765415435,
            "unit": "iter/sec",
            "range": "stddev: 0.0007473343521204668",
            "extra": "mean: 8.347911733047416 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 114.92542162297627,
            "unit": "iter/sec",
            "range": "stddev: 0.0004220001729974038",
            "extra": "mean: 8.70129503009869 msec\nrounds: 132"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 114.01148260895738,
            "unit": "iter/sec",
            "range": "stddev: 0.00045953671465199234",
            "extra": "mean: 8.771046364074161 msec\nrounds: 113"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 116.64376244917787,
            "unit": "iter/sec",
            "range": "stddev: 0.0006111022687167895",
            "extra": "mean: 8.573111660691705 msec\nrounds: 118"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 117.58467079299552,
            "unit": "iter/sec",
            "range": "stddev: 0.0006373371069414195",
            "extra": "mean: 8.504509926812414 msec\nrounds: 120"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 252.2438158379589,
            "unit": "iter/sec",
            "range": "stddev: 0.0002954359940511525",
            "extra": "mean: 3.964418301705358 msec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 6831.383401179098,
            "unit": "iter/sec",
            "range": "stddev: 0.000016069246737235706",
            "extra": "mean: 146.38323473798877 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7170.921425452549,
            "unit": "iter/sec",
            "range": "stddev: 0.000015903470676025854",
            "extra": "mean: 139.45209278832547 usec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 48.085753626196784,
            "unit": "iter/sec",
            "range": "stddev: 0.0027423949193332233",
            "extra": "mean: 20.79618025275592 msec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 89.48198956061401,
            "unit": "iter/sec",
            "range": "stddev: 0.0016697703597660122",
            "extra": "mean: 11.17543323422209 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 659.9214178663672,
            "unit": "iter/sec",
            "range": "stddev: 0.0001364383571165511",
            "extra": "mean: 1.515331936388975 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 614.6125857374093,
            "unit": "iter/sec",
            "range": "stddev: 0.00023207828300051217",
            "extra": "mean: 1.6270412015728652 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 65.0800885275617,
            "unit": "iter/sec",
            "range": "stddev: 0.003975191910013591",
            "extra": "mean: 15.36568284747332 msec\nrounds: 33"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f2d96da56d772f759be9998b418f947c2ddd83e5",
          "message": "Add BENCH_DATA_PATH to benchmark summary step\n\nSet BENCH_DATA_PATH environment variable for benchmark summary generation.",
          "timestamp": "2026-03-12T17:59:11+09:00",
          "tree_id": "fa3fdb59169295c5c194c0f47a42ea2ff59de2a4",
          "url": "https://github.com/disnana/NanaSQLite/commit/f2d96da56d772f759be9998b418f947c2ddd83e5"
        },
        "date": 1773306293910,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4030.625717610733,
            "unit": "iter/sec",
            "range": "stddev: 0.0044359245750148855",
            "extra": "mean: 248.10043652298688 usec\nrounds: 5073"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 3926.8680845082677,
            "unit": "iter/sec",
            "range": "stddev: 0.004615476173154916",
            "extra": "mean: 254.65586785180295 usec\nrounds: 6532"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 327.4806120364592,
            "unit": "iter/sec",
            "range": "stddev: 0.034833110860575674",
            "extra": "mean: 3.0536158882244533 msec\nrounds: 1651"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2263080.210452796,
            "unit": "iter/sec",
            "range": "stddev: 5.377433484605629e-8",
            "extra": "mean: 441.87563276863284 nsec\nrounds: 125882"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 87204.52498457608,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019991186029222075",
            "extra": "mean: 11.467294847106507 usec\nrounds: 8160"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 497.6349857559006,
            "unit": "iter/sec",
            "range": "stddev: 0.00020091703996582026",
            "extra": "mean: 2.0095050159727297 msec\nrounds: 301"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2748.689064822138,
            "unit": "iter/sec",
            "range": "stddev: 0.000019514216287732326",
            "extra": "mean: 363.8097931112147 usec\nrounds: 1368"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2279906.0399635904,
            "unit": "iter/sec",
            "range": "stddev: 1.0945646619461426e-7",
            "extra": "mean: 438.6145667722209 nsec\nrounds: 142106"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 118168.10140523169,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012476851143978805",
            "extra": "mean: 8.462520664275704 usec\nrounds: 9402"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 85654.99636807886,
            "unit": "iter/sec",
            "range": "stddev: 8.685818860740895e-7",
            "extra": "mean: 11.674742191369365 usec\nrounds: 344"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 73715.29298277115,
            "unit": "iter/sec",
            "range": "stddev: 9.596943029879798e-7",
            "extra": "mean: 13.56570610434556 usec\nrounds: 18894"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5801412.703850266,
            "unit": "iter/sec",
            "range": "stddev: 1.5920830891911128e-8",
            "extra": "mean: 172.3718085660452 nsec\nrounds: 135667"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1467911.5811136838,
            "unit": "iter/sec",
            "range": "stddev: 1.201612835574823e-7",
            "extra": "mean: 681.2399417418004 nsec\nrounds: 3608"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 74400.50577088259,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010846990643552312",
            "extra": "mean: 13.440768844764499 usec\nrounds: 309"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70122.1238476582,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024119747505771276",
            "extra": "mean: 14.260834457503329 usec\nrounds: 8882"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3756.8628720437837,
            "unit": "iter/sec",
            "range": "stddev: 0.004608921587403071",
            "extra": "mean: 266.1795317155099 usec\nrounds: 6015"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4438.649441983051,
            "unit": "iter/sec",
            "range": "stddev: 0.004137565569797995",
            "extra": "mean: 225.29375501959692 usec\nrounds: 9707"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51189.57980922713,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032210176327758938",
            "extra": "mean: 19.53522579647638 usec\nrounds: 10100"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9097.865501343163,
            "unit": "iter/sec",
            "range": "stddev: 0.0025810373576891726",
            "extra": "mean: 109.91589179378008 usec\nrounds: 9806"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7607.140913928107,
            "unit": "iter/sec",
            "range": "stddev: 0.000006825269015348719",
            "extra": "mean: 131.45543264080658 usec\nrounds: 1328"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12429.525253527469,
            "unit": "iter/sec",
            "range": "stddev: 0.000007591088261896686",
            "extra": "mean: 80.45359574101211 usec\nrounds: 3521"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21966.93778865335,
            "unit": "iter/sec",
            "range": "stddev: 0.00000400566818566461",
            "extra": "mean: 45.52295862177627 usec\nrounds: 4979"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8309.101775983469,
            "unit": "iter/sec",
            "range": "stddev: 0.000009120435937253665",
            "extra": "mean: 120.34995201170703 usec\nrounds: 3647"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8168.686193135513,
            "unit": "iter/sec",
            "range": "stddev: 0.0027711732420020265",
            "extra": "mean: 122.41870679771509 usec\nrounds: 6899"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2017.1416047715627,
            "unit": "iter/sec",
            "range": "stddev: 0.005383379354161232",
            "extra": "mean: 495.75101600923455 usec\nrounds: 3271"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 1539.7859335125606,
            "unit": "iter/sec",
            "range": "stddev: 0.006956426081513044",
            "extra": "mean: 649.4409243749873 usec\nrounds: 2081"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 1657.4597972228657,
            "unit": "iter/sec",
            "range": "stddev: 0.006207789184986761",
            "extra": "mean: 603.3328842579087 usec\nrounds: 2928"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 443.00583456568137,
            "unit": "iter/sec",
            "range": "stddev: 0.00840040443948135",
            "extra": "mean: 2.257306613084205 msec\nrounds: 1078"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1059.851963672104,
            "unit": "iter/sec",
            "range": "stddev: 0.004269314656985693",
            "extra": "mean: 943.5279966225352 usec\nrounds: 1039"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15407.850448663978,
            "unit": "iter/sec",
            "range": "stddev: 0.000009280889181569567",
            "extra": "mean: 64.9019798921212 usec\nrounds: 2199"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28527.692261863176,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035124157370402407",
            "extra": "mean: 35.05365911903204 usec\nrounds: 7041"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2293.3103082923594,
            "unit": "iter/sec",
            "range": "stddev: 0.000030113546838132886",
            "extra": "mean: 436.05088957395316 usec\nrounds: 1073"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 113044.30998287162,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016770706792739445",
            "extra": "mean: 8.846088760694979 usec\nrounds: 17556"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44527.37468896188,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026589702994749464",
            "extra": "mean: 22.458094755986036 usec\nrounds: 12451"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 57609.019306333954,
            "unit": "iter/sec",
            "range": "stddev: 0.000002442723665746143",
            "extra": "mean: 17.358393044022062 usec\nrounds: 16062"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 71100.83550970933,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023333233315254605",
            "extra": "mean: 14.064532333989844 usec\nrounds: 16058"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 98379.85334390144,
            "unit": "iter/sec",
            "range": "stddev: 0.000002030661083866317",
            "extra": "mean: 10.164682767968264 usec\nrounds: 13091"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1261.083033788277,
            "unit": "iter/sec",
            "range": "stddev: 0.005591779974326651",
            "extra": "mean: 792.969196481863 usec\nrounds: 320"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 883.9931204383399,
            "unit": "iter/sec",
            "range": "stddev: 0.008548271259335216",
            "extra": "mean: 1.1312305230431392 msec\nrounds: 1626"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 258908.03273322055,
            "unit": "iter/sec",
            "range": "stddev: 7.294279508161249e-7",
            "extra": "mean: 3.8623753363048503 usec\nrounds: 26879"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4499.3507940100735,
            "unit": "iter/sec",
            "range": "stddev: 0.004060643502049491",
            "extra": "mean: 222.25428640311551 usec\nrounds: 9638"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 157658.92614424293,
            "unit": "iter/sec",
            "range": "stddev: 8.565086310192679e-7",
            "extra": "mean: 6.342806109722549 usec\nrounds: 20890"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 8572.908250194785,
            "unit": "iter/sec",
            "range": "stddev: 0.002949496949312688",
            "extra": "mean: 116.64653007073522 usec\nrounds: 13220"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2258.9423855167674,
            "unit": "iter/sec",
            "range": "stddev: 0.006062620209576298",
            "extra": "mean: 442.6850398715392 usec\nrounds: 2985"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1860.820003492798,
            "unit": "iter/sec",
            "range": "stddev: 0.005942163875669772",
            "extra": "mean: 537.3974904198037 usec\nrounds: 2206"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3577.77582986303,
            "unit": "iter/sec",
            "range": "stddev: 0.00465206449500767",
            "extra": "mean: 279.5032577651137 usec\nrounds: 4117"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 364552.9065991123,
            "unit": "iter/sec",
            "range": "stddev: 5.123522496065013e-7",
            "extra": "mean: 2.7430860703565023 usec\nrounds: 43760"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8018.790805693098,
            "unit": "iter/sec",
            "range": "stddev: 0.0028683427360980816",
            "extra": "mean: 124.70708168244398 usec\nrounds: 8881"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37355.598583612256,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029080459814074412",
            "extra": "mean: 26.76974905814241 usec\nrounds: 8142"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 7380.537217535111,
            "unit": "iter/sec",
            "range": "stddev: 0.0030393102321056927",
            "extra": "mean: 135.4914920859882 usec\nrounds: 8067"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 3937.9579396968666,
            "unit": "iter/sec",
            "range": "stddev: 0.004608729122257631",
            "extra": "mean: 253.93872035031873 usec\nrounds: 6062"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 3914.8076345171175,
            "unit": "iter/sec",
            "range": "stddev: 0.004383296373665445",
            "extra": "mean: 255.44039282618485 usec\nrounds: 5187"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 3765.457076855049,
            "unit": "iter/sec",
            "range": "stddev: 0.0045492254190019265",
            "extra": "mean: 265.5720088131269 usec\nrounds: 5152"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 3953.6000335765007,
            "unit": "iter/sec",
            "range": "stddev: 0.003918096602080357",
            "extra": "mean: 252.93403265564555 usec\nrounds: 1148"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1213610.4229861484,
            "unit": "iter/sec",
            "range": "stddev: 1.8935329702122512e-7",
            "extra": "mean: 823.987649627671 nsec\nrounds: 100553"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1225227.403946411,
            "unit": "iter/sec",
            "range": "stddev: 1.8279805180578405e-7",
            "extra": "mean: 816.1750192487027 nsec\nrounds: 130123"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1234380.6419442608,
            "unit": "iter/sec",
            "range": "stddev: 1.531405482157625e-7",
            "extra": "mean: 810.1228794587298 nsec\nrounds: 109975"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1243209.8292047977,
            "unit": "iter/sec",
            "range": "stddev: 1.6686615379572436e-7",
            "extra": "mean: 804.3694447297255 nsec\nrounds: 181192"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 82810.18683309751,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024537720669774123",
            "extra": "mean: 12.07580900663203 usec\nrounds: 7548"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 52778.76672010779,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033923154637754654",
            "extra": "mean: 18.94701339466914 usec\nrounds: 8140"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 35635.700128004275,
            "unit": "iter/sec",
            "range": "stddev: 0.000004844447251737381",
            "extra": "mean: 28.06174696745052 usec\nrounds: 162"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17477.2095648922,
            "unit": "iter/sec",
            "range": "stddev: 0.00000768437579934741",
            "extra": "mean: 57.21737193154541 usec\nrounds: 4152"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 48.50335714195522,
            "unit": "iter/sec",
            "range": "stddev: 0.03422813000482451",
            "extra": "mean: 20.61712959524205 msec\nrounds: 192"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 47.89203789110176,
            "unit": "iter/sec",
            "range": "stddev: 0.03460128965936995",
            "extra": "mean: 20.880297519888956 msec\nrounds: 211"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 48.214608458419335,
            "unit": "iter/sec",
            "range": "stddev: 0.03400756915578028",
            "extra": "mean: 20.740601904138824 msec\nrounds: 190"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 12.711710747115673,
            "unit": "iter/sec",
            "range": "stddev: 0.4967304880808199",
            "extra": "mean: 78.6676175924553 msec\nrounds: 188"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21709.99833352061,
            "unit": "iter/sec",
            "range": "stddev: 0.000002066026547211847",
            "extra": "mean: 46.06172624416939 usec\nrounds: 11566"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 16948.041480593634,
            "unit": "iter/sec",
            "range": "stddev: 0.000002381057689761652",
            "extra": "mean: 59.00386785960198 usec\nrounds: 8939"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21807.385848406284,
            "unit": "iter/sec",
            "range": "stddev: 0.000002061286460959113",
            "extra": "mean: 45.856023594551175 usec\nrounds: 12025"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4321.325543484644,
            "unit": "iter/sec",
            "range": "stddev: 0.000008841526214598453",
            "extra": "mean: 231.41047577582336 usec\nrounds: 2812"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 3991.605351132454,
            "unit": "iter/sec",
            "range": "stddev: 0.00454092673827168",
            "extra": "mean: 250.52576896568473 usec\nrounds: 16320"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 423390.621620853,
            "unit": "iter/sec",
            "range": "stddev: 2.9969049051192393e-7",
            "extra": "mean: 2.3618850983796746 usec\nrounds: 68701"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 3841.9896900155504,
            "unit": "iter/sec",
            "range": "stddev: 0.004393390574098093",
            "extra": "mean: 260.28180205656736 usec\nrounds: 5559"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4187.507123280105,
            "unit": "iter/sec",
            "range": "stddev: 0.00002297694195107264",
            "extra": "mean: 238.80556392145138 usec\nrounds: 1093"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3652.438562278503,
            "unit": "iter/sec",
            "range": "stddev: 0.000017212527624585567",
            "extra": "mean: 273.7896840559501 usec\nrounds: 1614"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5144.011640085935,
            "unit": "iter/sec",
            "range": "stddev: 0.00001320997152118905",
            "extra": "mean: 194.40080426864938 usec\nrounds: 2791"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5132.698966056094,
            "unit": "iter/sec",
            "range": "stddev: 0.00001382063735703247",
            "extra": "mean: 194.82927142489098 usec\nrounds: 2806"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21482.86494939475,
            "unit": "iter/sec",
            "range": "stddev: 0.000004325623248015684",
            "extra": "mean: 46.54872626884775 usec\nrounds: 13009"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21231.31989141067,
            "unit": "iter/sec",
            "range": "stddev: 0.000003931212997746748",
            "extra": "mean: 47.10022764079587 usec\nrounds: 12195"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21165.393705467457,
            "unit": "iter/sec",
            "range": "stddev: 0.000007385874320223963",
            "extra": "mean: 47.246935914151194 usec\nrounds: 12739"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21225.854064998446,
            "unit": "iter/sec",
            "range": "stddev: 0.000003843774080982432",
            "extra": "mean: 47.11235632440373 usec\nrounds: 13288"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 209.6872218194772,
            "unit": "iter/sec",
            "range": "stddev: 0.01143895957980288",
            "extra": "mean: 4.769007817085367 msec\nrounds: 200"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 339.745909850859,
            "unit": "iter/sec",
            "range": "stddev: 0.003637126946623574",
            "extra": "mean: 2.943376126114301 msec\nrounds: 840"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 225486.702074388,
            "unit": "iter/sec",
            "range": "stddev: 0.000017719110343144016",
            "extra": "mean: 4.434851327374952 usec\nrounds: 37554"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 917478.4332691218,
            "unit": "iter/sec",
            "range": "stddev: 9.549064465785183e-7",
            "extra": "mean: 1.0899438763228915 usec\nrounds: 72876"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 51.836981138694576,
            "unit": "iter/sec",
            "range": "stddev: 0.0030620157533778215",
            "extra": "mean: 19.29124686725889 msec\nrounds: 66"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 73.74516665861502,
            "unit": "iter/sec",
            "range": "stddev: 0.012019990637254722",
            "extra": "mean: 13.560210727155209 msec\nrounds: 15"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 157549.01700069002,
            "unit": "iter/sec",
            "range": "stddev: 8.119033759912854e-7",
            "extra": "mean: 6.347230970001039 usec\nrounds: 21111"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 122212.19360474017,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016548116017148395",
            "extra": "mean: 8.182489574110823 usec\nrounds: 4558"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 70957.62690800524,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016597725849023608",
            "extra": "mean: 14.09291775352739 usec\nrounds: 13063"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82805.49048031031,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015196960732114047",
            "extra": "mean: 12.07649389188489 usec\nrounds: 13165"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2417.1150784367214,
            "unit": "iter/sec",
            "range": "stddev: 0.0048072529421736105",
            "extra": "mean: 413.7163385066275 usec\nrounds: 2606"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 741.6806629288511,
            "unit": "iter/sec",
            "range": "stddev: 0.010210378483231744",
            "extra": "mean: 1.3482891626850049 msec\nrounds: 2386"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4581.187878207538,
            "unit": "iter/sec",
            "range": "stddev: 0.000030384454136552795",
            "extra": "mean: 218.28399676794433 usec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4630.040026916115,
            "unit": "iter/sec",
            "range": "stddev: 0.00003534408883594618",
            "extra": "mean: 215.98085420139665 usec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1336.543121338486,
            "unit": "iter/sec",
            "range": "stddev: 0.00031492892364369947",
            "extra": "mean: 748.1988302768311 usec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 225.19540662917683,
            "unit": "iter/sec",
            "range": "stddev: 0.0006487460160666717",
            "extra": "mean: 4.440587909711112 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 9571.690157969182,
            "unit": "iter/sec",
            "range": "stddev: 0.000018525915041969008",
            "extra": "mean: 104.47475665177289 usec\nrounds: 3250"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7237.379868489732,
            "unit": "iter/sec",
            "range": "stddev: 0.000018520742263457423",
            "extra": "mean: 138.1715507781791 usec\nrounds: 3574"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 289.3963691085455,
            "unit": "iter/sec",
            "range": "stddev: 0.0017859051984098465",
            "extra": "mean: 3.455468370527221 msec\nrounds: 233"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7644.578349348447,
            "unit": "iter/sec",
            "range": "stddev: 0.00004802492208773481",
            "extra": "mean: 130.81166210890242 usec\nrounds: 2871"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1794.8024389411034,
            "unit": "iter/sec",
            "range": "stddev: 0.00007950068491612995",
            "extra": "mean: 557.1643866218387 usec\nrounds: 1090"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6950.984906773407,
            "unit": "iter/sec",
            "range": "stddev: 0.000015169422156661782",
            "extra": "mean: 143.86450458632808 usec\nrounds: 355"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 9401.041499783172,
            "unit": "iter/sec",
            "range": "stddev: 0.00002789025439190168",
            "extra": "mean: 106.37119302399252 usec\nrounds: 3788"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8010.762936832043,
            "unit": "iter/sec",
            "range": "stddev: 0.000014827626688191999",
            "extra": "mean: 124.83205505959744 usec\nrounds: 2937"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6654.496801097232,
            "unit": "iter/sec",
            "range": "stddev: 0.0000203222273566636",
            "extra": "mean: 150.27432274595344 usec\nrounds: 339"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 1790.134872793153,
            "unit": "iter/sec",
            "range": "stddev: 0.0003686560276576441",
            "extra": "mean: 558.6171272333783 usec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 4068.525860734815,
            "unit": "iter/sec",
            "range": "stddev: 0.00006849468206762239",
            "extra": "mean: 245.7892696838826 usec\nrounds: 38"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7435.34009486285,
            "unit": "iter/sec",
            "range": "stddev: 0.000024859212890411988",
            "extra": "mean: 134.49283923016648 usec\nrounds: 3371"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1197.5458157622213,
            "unit": "iter/sec",
            "range": "stddev: 0.00011407770366017514",
            "extra": "mean: 835.0411206301229 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 273.2494025909084,
            "unit": "iter/sec",
            "range": "stddev: 0.00025677628060173397",
            "extra": "mean: 3.659660334178795 msec\nrounds: 214"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.86958973673626,
            "unit": "iter/sec",
            "range": "stddev: 0.004844517765879699",
            "extra": "mean: 16.986698981120504 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 45.454567214192906,
            "unit": "iter/sec",
            "range": "stddev: 0.00337412221879586",
            "extra": "mean: 21.999989468335677 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.51295313535548,
            "unit": "iter/sec",
            "range": "stddev: 0.003947184564838444",
            "extra": "mean: 51.24800910776043 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.621680512251896,
            "unit": "iter/sec",
            "range": "stddev: 0.005283376893716876",
            "extra": "mean: 33.759056971341906 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 48.934309686760415,
            "unit": "iter/sec",
            "range": "stddev: 0.0022807259777414724",
            "extra": "mean: 20.435559557317276 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 66.31026086825514,
            "unit": "iter/sec",
            "range": "stddev: 0.002287366754361983",
            "extra": "mean: 15.080622318569889 msec\nrounds: 82"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6775.118486685363,
            "unit": "iter/sec",
            "range": "stddev: 0.00001497965786302121",
            "extra": "mean: 147.59889468578677 usec\nrounds: 3992"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1487.9924921826948,
            "unit": "iter/sec",
            "range": "stddev: 0.00008169201280528643",
            "extra": "mean: 672.0464016139812 usec\nrounds: 49"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4709.376005014405,
            "unit": "iter/sec",
            "range": "stddev: 0.000019376674536623205",
            "extra": "mean: 212.34235680804196 usec\nrounds: 911"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 674.4641752328164,
            "unit": "iter/sec",
            "range": "stddev: 0.00012419271062184633",
            "extra": "mean: 1.4826584372028548 msec\nrounds: 465"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 457.88870824195385,
            "unit": "iter/sec",
            "range": "stddev: 0.0001758155042934743",
            "extra": "mean: 2.1839367994888144 msec\nrounds: 328"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 67.22020230064567,
            "unit": "iter/sec",
            "range": "stddev: 0.002637664432845273",
            "extra": "mean: 14.876480072574772 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 64.63302374259197,
            "unit": "iter/sec",
            "range": "stddev: 0.002004218897841518",
            "extra": "mean: 15.47196683823131 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.34023103758375,
            "unit": "iter/sec",
            "range": "stddev: 0.004413117554598632",
            "extra": "mean: 30.921238590963185 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 53.57428001838636,
            "unit": "iter/sec",
            "range": "stddev: 0.009222083374079364",
            "extra": "mean: 18.665673148697586 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 64.4108484465367,
            "unit": "iter/sec",
            "range": "stddev: 0.0022155909934527753",
            "extra": "mean: 15.525335003621876 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 666.0309212065252,
            "unit": "iter/sec",
            "range": "stddev: 0.00012018937054128682",
            "extra": "mean: 1.5014317926688516 msec\nrounds: 483"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 15.081912469621264,
            "unit": "iter/sec",
            "range": "stddev: 0.02495400859065127",
            "extra": "mean: 66.30458849394927 msec\nrounds: 8"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 18.06290078018797,
            "unit": "iter/sec",
            "range": "stddev: 0.008614935552772663",
            "extra": "mean: 55.36209339625202 msec\nrounds: 10"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 651.8694519236809,
            "unit": "iter/sec",
            "range": "stddev: 0.00015563488132870542",
            "extra": "mean: 1.53404948958565 msec\nrounds: 454"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 8.408267270231724,
            "unit": "iter/sec",
            "range": "stddev: 0.07123615543694245",
            "extra": "mean: 118.93056772117104 msec\nrounds: 7"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 7.545490364267468,
            "unit": "iter/sec",
            "range": "stddev: 0.021966132842074933",
            "extra": "mean: 132.52949135494418 msec\nrounds: 6"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 8.73252703924833,
            "unit": "iter/sec",
            "range": "stddev: 0.013246268312896785",
            "extra": "mean: 114.51438919175416 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 9.33411232895252,
            "unit": "iter/sec",
            "range": "stddev: 0.01612923870844333",
            "extra": "mean: 107.13391533742349 msec\nrounds: 6"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 6.846394134076551,
            "unit": "iter/sec",
            "range": "stddev: 0.05888693320991058",
            "extra": "mean: 146.0622892016545 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 83.45835982962697,
            "unit": "iter/sec",
            "range": "stddev: 0.00033683437125507653",
            "extra": "mean: 11.98202315551628 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 82.8942562722559,
            "unit": "iter/sec",
            "range": "stddev: 0.00044262535941444074",
            "extra": "mean: 12.063562000190027 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.67585740352382,
            "unit": "iter/sec",
            "range": "stddev: 0.001021291158181169",
            "extra": "mean: 12.095429444646774 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.52603226658672,
            "unit": "iter/sec",
            "range": "stddev: 0.0004783702742040604",
            "extra": "mean: 12.898893065510256 msec\nrounds: 62"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 9.602196450568957,
            "unit": "iter/sec",
            "range": "stddev: 0.07302632485810384",
            "extra": "mean: 104.1428391043538 msec\nrounds: 19"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 582.5995454982202,
            "unit": "iter/sec",
            "range": "stddev: 0.00014584919621918004",
            "extra": "mean: 1.7164448680522613 msec\nrounds: 414"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 10.543545861639796,
            "unit": "iter/sec",
            "range": "stddev: 0.05903488677969991",
            "extra": "mean: 94.84475271628153 msec\nrounds: 11"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 58.728344311993325,
            "unit": "iter/sec",
            "range": "stddev: 0.002498084343343765",
            "extra": "mean: 17.02755307875729 msec\nrounds: 12"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 58.531010420556356,
            "unit": "iter/sec",
            "range": "stddev: 0.002512174880627119",
            "extra": "mean: 17.084960481884924 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 61.01283507553523,
            "unit": "iter/sec",
            "range": "stddev: 0.0019860388085010724",
            "extra": "mean: 16.38999398670752 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 702.3735253459811,
            "unit": "iter/sec",
            "range": "stddev: 0.00010330909515430324",
            "extra": "mean: 1.4237438683461363 msec\nrounds: 515"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 665.9583030994728,
            "unit": "iter/sec",
            "range": "stddev: 0.00012574405635542744",
            "extra": "mean: 1.501595513331459 msec\nrounds: 475"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 676.7249580786089,
            "unit": "iter/sec",
            "range": "stddev: 0.00014808703258280641",
            "extra": "mean: 1.477705215482594 msec\nrounds: 455"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 64.13536423790076,
            "unit": "iter/sec",
            "range": "stddev: 0.0018752386550701058",
            "extra": "mean: 15.592021841345536 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 51.75277901138667,
            "unit": "iter/sec",
            "range": "stddev: 0.003050827937619513",
            "extra": "mean: 19.322633858560128 msec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 66.06671602591543,
            "unit": "iter/sec",
            "range": "stddev: 0.002351099012730471",
            "extra": "mean: 15.136214725849829 msec\nrounds: 58"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 57.59744823847365,
            "unit": "iter/sec",
            "range": "stddev: 0.0044086125432805925",
            "extra": "mean: 17.361880266980734 msec\nrounds: 80"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 68.79338965710014,
            "unit": "iter/sec",
            "range": "stddev: 0.001883064139904151",
            "extra": "mean: 14.536280374967545 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 652.4497942967745,
            "unit": "iter/sec",
            "range": "stddev: 0.00011494847297457447",
            "extra": "mean: 1.5326849801183908 msec\nrounds: 436"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 737.7434525464357,
            "unit": "iter/sec",
            "range": "stddev: 0.00011407719238733237",
            "extra": "mean: 1.3554847508959182 msec\nrounds: 539"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 271.9866170096613,
            "unit": "iter/sec",
            "range": "stddev: 0.002141944629760521",
            "extra": "mean: 3.676651487468145 msec\nrounds: 217"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 679.0806649533251,
            "unit": "iter/sec",
            "range": "stddev: 0.0001334834876430981",
            "extra": "mean: 1.4725791082105577 msec\nrounds: 484"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 721.1568294479143,
            "unit": "iter/sec",
            "range": "stddev: 0.00011449634012012825",
            "extra": "mean: 1.386660930279972 msec\nrounds: 486"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 87.10616961630986,
            "unit": "iter/sec",
            "range": "stddev: 0.003207019498418403",
            "extra": "mean: 11.480243068945128 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 99.81075883781845,
            "unit": "iter/sec",
            "range": "stddev: 0.00035140491577300933",
            "extra": "mean: 10.01895999633557 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 123.4510222359776,
            "unit": "iter/sec",
            "range": "stddev: 0.0008580204442230965",
            "extra": "mean: 8.100378448778594 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 118.50174436761785,
            "unit": "iter/sec",
            "range": "stddev: 0.0008199823639372122",
            "extra": "mean: 8.438694344429104 msec\nrounds: 38"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 114.3476976210894,
            "unit": "iter/sec",
            "range": "stddev: 0.000475103628729632",
            "extra": "mean: 8.745256973285729 msec\nrounds: 119"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 121.57219278884628,
            "unit": "iter/sec",
            "range": "stddev: 0.0007282840131835986",
            "extra": "mean: 8.22556521405235 msec\nrounds: 117"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 119.07642221707182,
            "unit": "iter/sec",
            "range": "stddev: 0.0005222782089796484",
            "extra": "mean: 8.397968139965087 msec\nrounds: 125"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 118.74625651229995,
            "unit": "iter/sec",
            "range": "stddev: 0.0005790474392415103",
            "extra": "mean: 8.421318106111567 msec\nrounds: 131"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 256.43625367382293,
            "unit": "iter/sec",
            "range": "stddev: 0.0003803148927288213",
            "extra": "mean: 3.8996046217082925 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 6905.600537202824,
            "unit": "iter/sec",
            "range": "stddev: 0.00001340345075548844",
            "extra": "mean: 144.80999800273113 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7453.697347408274,
            "unit": "iter/sec",
            "range": "stddev: 0.000008939326399750678",
            "extra": "mean: 134.16160509223118 usec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 47.56358493423171,
            "unit": "iter/sec",
            "range": "stddev: 0.003895687612726929",
            "extra": "mean: 21.024487565071986 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 91.4998369330294,
            "unit": "iter/sec",
            "range": "stddev: 0.0012504715814623912",
            "extra": "mean: 10.928981225747108 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 667.7120106742345,
            "unit": "iter/sec",
            "range": "stddev: 0.0002462619829297841",
            "extra": "mean: 1.4976516582204826 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 667.1043709891602,
            "unit": "iter/sec",
            "range": "stddev: 0.0002179438257146167",
            "extra": "mean: 1.4990158114497636 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 68.76210582721866,
            "unit": "iter/sec",
            "range": "stddev: 0.002456354127548594",
            "extra": "mean: 14.542893763503125 msec\nrounds: 29"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5086490d7ef4bc86820e412d10a325655ea1e806",
          "message": "Merge pull request #131 from disnana/alert-autofix-491\n\nPotential fix for code scanning alert no. 491: Unnecessary lambda",
          "timestamp": "2026-03-12T18:28:04+09:00",
          "tree_id": "c8dfc066dcf9e8a039e9f6cb10f49f6ca594e5f6",
          "url": "https://github.com/disnana/NanaSQLite/commit/5086490d7ef4bc86820e412d10a325655ea1e806"
        },
        "date": 1773307984494,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4676.039819474122,
            "unit": "iter/sec",
            "range": "stddev: 0.0037353919974904537",
            "extra": "mean: 213.85617715130195 usec\nrounds: 5127"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4398.291888078166,
            "unit": "iter/sec",
            "range": "stddev: 0.004038505851861908",
            "extra": "mean: 227.36099045871876 usec\nrounds: 8421"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 710.906751364055,
            "unit": "iter/sec",
            "range": "stddev: 0.010125419656445608",
            "extra": "mean: 1.406654245555055 msec\nrounds: 2155"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2463369.4356661267,
            "unit": "iter/sec",
            "range": "stddev: 2.4688921113262276e-8",
            "extra": "mean: 405.9480423525774 nsec\nrounds: 60946"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 88255.91531362987,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016564999017839344",
            "extra": "mean: 11.330685274141214 usec\nrounds: 8531"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 480.36133829910773,
            "unit": "iter/sec",
            "range": "stddev: 0.00022301647633528757",
            "extra": "mean: 2.08176620445946 msec\nrounds: 280"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2776.1985584767444,
            "unit": "iter/sec",
            "range": "stddev: 0.000016325453566117716",
            "extra": "mean: 360.2047832445687 usec\nrounds: 1493"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2327451.1594394655,
            "unit": "iter/sec",
            "range": "stddev: 2.1547711782500302e-7",
            "extra": "mean: 429.65455835422824 nsec\nrounds: 145561"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 118455.12488343791,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016559183561928397",
            "extra": "mean: 8.44201549729502 usec\nrounds: 8939"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 81952.70988995582,
            "unit": "iter/sec",
            "range": "stddev: 5.731622626383259e-7",
            "extra": "mean: 12.202159041998447 usec\nrounds: 385"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 70911.30295005666,
            "unit": "iter/sec",
            "range": "stddev: 0.000001186181523319956",
            "extra": "mean: 14.102124180461148 usec\nrounds: 16029"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5914550.2148005,
            "unit": "iter/sec",
            "range": "stddev: 1.616701841093808e-8",
            "extra": "mean: 169.07456419874427 nsec\nrounds: 135337"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1423312.8439571545,
            "unit": "iter/sec",
            "range": "stddev: 3.117918567283895e-8",
            "extra": "mean: 702.5862263841854 nsec\nrounds: 3591"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 94012.58317264527,
            "unit": "iter/sec",
            "range": "stddev: 0.0000041735648212130605",
            "extra": "mean: 10.636873982747543 usec\nrounds: 338"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70846.91147205219,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021890299061423227",
            "extra": "mean: 14.114941346377275 usec\nrounds: 13307"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 964.4435774184013,
            "unit": "iter/sec",
            "range": "stddev: 0.04511658214482872",
            "extra": "mean: 1.036867291580473 msec\nrounds: 6815"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4425.0597069657715,
            "unit": "iter/sec",
            "range": "stddev: 0.0041007592969531685",
            "extra": "mean: 225.98565131806825 usec\nrounds: 8478"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51691.87575851483,
            "unit": "iter/sec",
            "range": "stddev: 0.000002827802248986202",
            "extra": "mean: 19.345399742729924 usec\nrounds: 10593"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9486.974302794726,
            "unit": "iter/sec",
            "range": "stddev: 0.0024283567195995245",
            "extra": "mean: 105.407685114675 usec\nrounds: 9695"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7329.333774669837,
            "unit": "iter/sec",
            "range": "stddev: 0.00001722684555072683",
            "extra": "mean: 136.43804890643648 usec\nrounds: 952"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12442.534358607083,
            "unit": "iter/sec",
            "range": "stddev: 0.000006374479096054167",
            "extra": "mean: 80.36947869131285 usec\nrounds: 3630"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21985.993237692768,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037765655523629303",
            "extra": "mean: 45.483503482826556 usec\nrounds: 6517"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8338.19004430855,
            "unit": "iter/sec",
            "range": "stddev: 0.000007920543975144",
            "extra": "mean: 119.93010409766038 usec\nrounds: 3961"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8413.465408184464,
            "unit": "iter/sec",
            "range": "stddev: 0.0025343964941673728",
            "extra": "mean: 118.85708818951325 usec\nrounds: 7217"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2192.527682381914,
            "unit": "iter/sec",
            "range": "stddev: 0.004915979450074056",
            "extra": "mean: 456.0945834506508 usec\nrounds: 3406"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2104.1183098618467,
            "unit": "iter/sec",
            "range": "stddev: 0.005314493235855335",
            "extra": "mean: 475.25844688156275 usec\nrounds: 3075"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2170.723540245816,
            "unit": "iter/sec",
            "range": "stddev: 0.005202256982297413",
            "extra": "mean: 460.67589053130115 usec\nrounds: 3488"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 435.60437602417335,
            "unit": "iter/sec",
            "range": "stddev: 0.008023448212279391",
            "extra": "mean: 2.2956610517257667 msec\nrounds: 1169"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1308.723761285551,
            "unit": "iter/sec",
            "range": "stddev: 0.003855914367450001",
            "extra": "mean: 764.1031893680195 usec\nrounds: 972"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15378.307091989618,
            "unit": "iter/sec",
            "range": "stddev: 0.000008493730871630073",
            "extra": "mean: 65.02666346940674 usec\nrounds: 2233"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28424.7556738408,
            "unit": "iter/sec",
            "range": "stddev: 0.000003876852215285962",
            "extra": "mean: 35.180601426252416 usec\nrounds: 6300"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2337.1197363281076,
            "unit": "iter/sec",
            "range": "stddev: 0.000022841623163467104",
            "extra": "mean: 427.87709352500644 usec\nrounds: 1092"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 113110.2271815873,
            "unit": "iter/sec",
            "range": "stddev: 0.000001154952443581563",
            "extra": "mean: 8.840933529331515 usec\nrounds: 15804"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44781.39411304313,
            "unit": "iter/sec",
            "range": "stddev: 0.00000203753483468412",
            "extra": "mean: 22.330702735061518 usec\nrounds: 12168"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 58243.846744274175,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018061236347073828",
            "extra": "mean: 17.169195647234748 usec\nrounds: 15491"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 71018.9361800091,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021074442754739396",
            "extra": "mean: 14.080751610603352 usec\nrounds: 14343"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 98736.47120700961,
            "unit": "iter/sec",
            "range": "stddev: 0.000001669283238284305",
            "extra": "mean: 10.127969814754803 usec\nrounds: 11714"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 2135.924089648121,
            "unit": "iter/sec",
            "range": "stddev: 0.00004689162197984808",
            "extra": "mean: 468.18143249872855 usec\nrounds: 187"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 956.0472112585497,
            "unit": "iter/sec",
            "range": "stddev: 0.0075467421386677305",
            "extra": "mean: 1.0459734500805566 msec\nrounds: 2292"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 249990.26623843977,
            "unit": "iter/sec",
            "range": "stddev: 7.035738214192113e-7",
            "extra": "mean: 4.000155746248951 usec\nrounds: 19313"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4923.258750170976,
            "unit": "iter/sec",
            "range": "stddev: 0.0036681428137937404",
            "extra": "mean: 203.11749813378626 usec\nrounds: 8717"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 157337.02795058268,
            "unit": "iter/sec",
            "range": "stddev: 8.63108139929696e-7",
            "extra": "mean: 6.355782952211896 usec\nrounds: 22814"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 9752.66193211212,
            "unit": "iter/sec",
            "range": "stddev: 0.002496928354341286",
            "extra": "mean: 102.53610829135256 usec\nrounds: 14482"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2756.1831655867727,
            "unit": "iter/sec",
            "range": "stddev: 0.0043076780965992535",
            "extra": "mean: 362.82058917049756 usec\nrounds: 3067"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1968.0353322607548,
            "unit": "iter/sec",
            "range": "stddev: 0.0052069796870993085",
            "extra": "mean: 508.12095880985186 usec\nrounds: 2098"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 2181.5937650725787,
            "unit": "iter/sec",
            "range": "stddev: 0.01441744807554466",
            "extra": "mean: 458.38048128393484 usec\nrounds: 3369"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 364452.8279551237,
            "unit": "iter/sec",
            "range": "stddev: 3.27697394618122e-7",
            "extra": "mean: 2.7438393210194363 usec\nrounds: 41539"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8167.308325133899,
            "unit": "iter/sec",
            "range": "stddev: 0.0026557635266450377",
            "extra": "mean: 122.43935947937968 usec\nrounds: 8058"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37399.25132965596,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027381102068037475",
            "extra": "mean: 26.738503163753013 usec\nrounds: 11061"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 8635.30363426603,
            "unit": "iter/sec",
            "range": "stddev: 0.002484731469811827",
            "extra": "mean: 115.8036870911947 usec\nrounds: 8466"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4410.915151158571,
            "unit": "iter/sec",
            "range": "stddev: 0.004089555370634577",
            "extra": "mean: 226.71032330724844 usec\nrounds: 6269"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 3962.375206643284,
            "unit": "iter/sec",
            "range": "stddev: 0.004280086509765095",
            "extra": "mean: 252.37387875923727 usec\nrounds: 5900"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4143.916714873768,
            "unit": "iter/sec",
            "range": "stddev: 0.004042388713363021",
            "extra": "mean: 241.31759125628616 usec\nrounds: 5131"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4231.707669488119,
            "unit": "iter/sec",
            "range": "stddev: 0.003647929359869751",
            "extra": "mean: 236.31121951317664 usec\nrounds: 1228"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1238348.8400842135,
            "unit": "iter/sec",
            "range": "stddev: 1.3425853666896552e-7",
            "extra": "mean: 807.5269000389222 nsec\nrounds: 115876"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1240580.2170036028,
            "unit": "iter/sec",
            "range": "stddev: 1.5392402633030564e-7",
            "extra": "mean: 806.0744370205413 nsec\nrounds: 125866"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1239766.8432293085,
            "unit": "iter/sec",
            "range": "stddev: 1.2566606346864205e-7",
            "extra": "mean: 806.6032782383736 nsec\nrounds: 127357"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1249827.0691641718,
            "unit": "iter/sec",
            "range": "stddev: 1.4501764541759105e-7",
            "extra": "mean: 800.1106910484465 nsec\nrounds: 195655"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 84299.57387195386,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016563539462462138",
            "extra": "mean: 11.86245616755954 usec\nrounds: 11497"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 58429.35073795274,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036045312503632327",
            "extra": "mean: 17.114686152938045 usec\nrounds: 8002"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 53440.486924601566,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025560889191238677",
            "extra": "mean: 18.712404350111665 usec\nrounds: 9172"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17960.33479036412,
            "unit": "iter/sec",
            "range": "stddev: 0.000006126847150740157",
            "extra": "mean: 55.678249413062666 usec\nrounds: 4212"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 52.89405978386319,
            "unit": "iter/sec",
            "range": "stddev: 0.031566145574557766",
            "extra": "mean: 18.905714631968518 msec\nrounds: 193"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 16.150259767406094,
            "unit": "iter/sec",
            "range": "stddev: 0.28706282298665303",
            "extra": "mean: 61.918508705238665 msec\nrounds: 197"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 51.80710757982447,
            "unit": "iter/sec",
            "range": "stddev: 0.03112236537001791",
            "extra": "mean: 19.302370788780255 msec\nrounds: 195"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 50.01567481207639,
            "unit": "iter/sec",
            "range": "stddev: 0.03448241713874309",
            "extra": "mean: 19.9937320401513 msec\nrounds: 199"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21815.585549357133,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018507159336094758",
            "extra": "mean: 45.8387879499053 usec\nrounds: 11681"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17012.70492215536,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021735961231153865",
            "extra": "mean: 58.779600573552344 usec\nrounds: 10181"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 22064.110460240114,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019022461165567897",
            "extra": "mean: 45.322470706535675 usec\nrounds: 14478"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4359.564338652193,
            "unit": "iter/sec",
            "range": "stddev: 0.000007691110616651072",
            "extra": "mean: 229.38071842040088 usec\nrounds: 2763"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4346.98670829178,
            "unit": "iter/sec",
            "range": "stddev: 0.004050529355006025",
            "extra": "mean: 230.04441170535958 usec\nrounds: 16595"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 422416.83416336885,
            "unit": "iter/sec",
            "range": "stddev: 3.2836406239433516e-7",
            "extra": "mean: 2.3673298957902134 usec\nrounds: 72580"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 4061.0135896620422,
            "unit": "iter/sec",
            "range": "stddev: 0.004129992998943475",
            "extra": "mean: 246.24394327210808 usec\nrounds: 5063"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4126.046452056314,
            "unit": "iter/sec",
            "range": "stddev: 0.000026534377718369576",
            "extra": "mean: 242.362758543745 usec\nrounds: 1027"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3606.3138588779643,
            "unit": "iter/sec",
            "range": "stddev: 0.000023898088128007683",
            "extra": "mean: 277.2914502541748 usec\nrounds: 1291"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5144.980191695353,
            "unit": "iter/sec",
            "range": "stddev: 0.00001747153589083344",
            "extra": "mean: 194.36420797384724 usec\nrounds: 2661"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5074.394249725657,
            "unit": "iter/sec",
            "range": "stddev: 0.00001411248286947843",
            "extra": "mean: 197.06785692776322 usec\nrounds: 3347"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21656.96999294914,
            "unit": "iter/sec",
            "range": "stddev: 0.000004294050066520045",
            "extra": "mean: 46.174511038504924 usec\nrounds: 12332"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21813.0915774567,
            "unit": "iter/sec",
            "range": "stddev: 0.000004189636649370453",
            "extra": "mean: 45.84402886904284 usec\nrounds: 11976"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21998.041443517664,
            "unit": "iter/sec",
            "range": "stddev: 0.000008395908818606312",
            "extra": "mean: 45.45859241913002 usec\nrounds: 12321"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21676.526240120093,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033769700140873616",
            "extra": "mean: 46.1328530652271 usec\nrounds: 13337"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 208.61357306308045,
            "unit": "iter/sec",
            "range": "stddev: 0.010754975642603732",
            "extra": "mean: 4.7935519502253126 msec\nrounds: 190"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 340.5421004589283,
            "unit": "iter/sec",
            "range": "stddev: 0.0035953820451341506",
            "extra": "mean: 2.936494485270278 msec\nrounds: 807"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 224544.44107641885,
            "unit": "iter/sec",
            "range": "stddev: 0.000019409317627216365",
            "extra": "mean: 4.453461395909915 usec\nrounds: 35362"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 945224.2223101606,
            "unit": "iter/sec",
            "range": "stddev: 9.573193953116989e-7",
            "extra": "mean: 1.0579500359776703 usec\nrounds: 70220"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 56.080655709065695,
            "unit": "iter/sec",
            "range": "stddev: 0.002811047997416313",
            "extra": "mean: 17.83146055188412 msec\nrounds: 78"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 91.95386047095981,
            "unit": "iter/sec",
            "range": "stddev: 0.0035778788125694857",
            "extra": "mean: 10.875019220273114 msec\nrounds: 45"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 156183.68543333086,
            "unit": "iter/sec",
            "range": "stddev: 0.000001400418602837632",
            "extra": "mean: 6.402717397950401 usec\nrounds: 21260"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 119862.92360722151,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021752569238799426",
            "extra": "mean: 8.342863413518073 usec\nrounds: 4360"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 71326.23142684143,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021125119810507824",
            "extra": "mean: 14.020087420792581 usec\nrounds: 13609"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82973.13900354592,
            "unit": "iter/sec",
            "range": "stddev: 0.000001907588820425972",
            "extra": "mean: 12.052093147365007 usec\nrounds: 14166"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 1562.6722806172243,
            "unit": "iter/sec",
            "range": "stddev: 0.014724391934842393",
            "extra": "mean: 639.9294416389212 usec\nrounds: 2618"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 803.9078602167616,
            "unit": "iter/sec",
            "range": "stddev: 0.009406195535050014",
            "extra": "mean: 1.2439236503177928 msec\nrounds: 1517"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4583.401674159005,
            "unit": "iter/sec",
            "range": "stddev: 0.00003699937459340806",
            "extra": "mean: 218.1785649811037 usec\nrounds: 39"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4561.92502961232,
            "unit": "iter/sec",
            "range": "stddev: 0.00008402411564056493",
            "extra": "mean: 219.20570669373356 usec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1392.8718846882816,
            "unit": "iter/sec",
            "range": "stddev: 0.00032697915439278927",
            "extra": "mean: 717.9411193469493 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 194.34204812431733,
            "unit": "iter/sec",
            "range": "stddev: 0.004476121376912024",
            "extra": "mean: 5.145566847995329 msec\nrounds: 46"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10479.455757541584,
            "unit": "iter/sec",
            "range": "stddev: 0.000015411502541758175",
            "extra": "mean: 95.42480288447669 usec\nrounds: 3683"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7202.78956217912,
            "unit": "iter/sec",
            "range": "stddev: 0.00001466600708302118",
            "extra": "mean: 138.83509873047876 usec\nrounds: 2656"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 302.41612370828716,
            "unit": "iter/sec",
            "range": "stddev: 0.0003237561383315945",
            "extra": "mean: 3.306701996367784 msec\nrounds: 228"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 8116.5254434640965,
            "unit": "iter/sec",
            "range": "stddev: 0.000015749040462987186",
            "extra": "mean: 123.20542909223043 usec\nrounds: 2575"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1740.1465273364975,
            "unit": "iter/sec",
            "range": "stddev: 0.00003626982468339323",
            "extra": "mean: 574.6642505620603 usec\nrounds: 964"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6840.079001792481,
            "unit": "iter/sec",
            "range": "stddev: 0.000017524784598995142",
            "extra": "mean: 146.19714183680398 usec\nrounds: 355"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 9371.396338931865,
            "unit": "iter/sec",
            "range": "stddev: 0.00001574410810147632",
            "extra": "mean: 106.70768408819409 usec\nrounds: 4126"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8544.630526229525,
            "unit": "iter/sec",
            "range": "stddev: 0.00001724864003701357",
            "extra": "mean: 117.0325617860587 usec\nrounds: 2339"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6700.0059145885425,
            "unit": "iter/sec",
            "range": "stddev: 0.000013271100134548328",
            "extra": "mean: 149.25359958602536 usec\nrounds: 310"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2928.31230932895,
            "unit": "iter/sec",
            "range": "stddev: 0.00004907806813662086",
            "extra": "mean: 341.4936299021873 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 4689.562256488684,
            "unit": "iter/sec",
            "range": "stddev: 0.00002306635040804333",
            "extra": "mean: 213.23951902256036 usec\nrounds: 48"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 6947.77305591687,
            "unit": "iter/sec",
            "range": "stddev: 0.000015921680661217963",
            "extra": "mean: 143.93101098032827 usec\nrounds: 3192"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1175.0416790830525,
            "unit": "iter/sec",
            "range": "stddev: 0.0001141407323891297",
            "extra": "mean: 851.0336422962913 usec\nrounds: 48"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 273.6498261625614,
            "unit": "iter/sec",
            "range": "stddev: 0.00024110031147585195",
            "extra": "mean: 3.654305263128328 msec\nrounds: 190"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.491660402232135,
            "unit": "iter/sec",
            "range": "stddev: 0.0046790173278268175",
            "extra": "mean: 17.096454317132675 msec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 41.35415781910597,
            "unit": "iter/sec",
            "range": "stddev: 0.009185287318926068",
            "extra": "mean: 24.181365375018988 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.56714321627786,
            "unit": "iter/sec",
            "range": "stddev: 0.003491553300584853",
            "extra": "mean: 51.106080685713096 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.491936297936043,
            "unit": "iter/sec",
            "range": "stddev: 0.007399343150335835",
            "extra": "mean: 33.90757357867967 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 47.49443050241283,
            "unit": "iter/sec",
            "range": "stddev: 0.0032095280120040095",
            "extra": "mean: 21.055100343801314 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 66.59711290031396,
            "unit": "iter/sec",
            "range": "stddev: 0.002219510115038494",
            "extra": "mean: 15.015665941808203 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 7137.5658618311,
            "unit": "iter/sec",
            "range": "stddev: 0.000019056829587286424",
            "extra": "mean: 140.10378599062847 usec\nrounds: 3993"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1615.6190789757952,
            "unit": "iter/sec",
            "range": "stddev: 0.00006693337540056559",
            "extra": "mean: 618.9577809603112 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4202.791812678339,
            "unit": "iter/sec",
            "range": "stddev: 0.000023809070859344636",
            "extra": "mean: 237.93707720267113 usec\nrounds: 931"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 666.1297019920463,
            "unit": "iter/sec",
            "range": "stddev: 0.0001261894483763282",
            "extra": "mean: 1.5012091444196558 msec\nrounds: 459"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 468.1394113563747,
            "unit": "iter/sec",
            "range": "stddev: 0.00018738971949151762",
            "extra": "mean: 2.1361158145233414 msec\nrounds: 325"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 52.22164579401504,
            "unit": "iter/sec",
            "range": "stddev: 0.012072449976843045",
            "extra": "mean: 19.149147538253324 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 61.20488714356682,
            "unit": "iter/sec",
            "range": "stddev: 0.0020389857142693027",
            "extra": "mean: 16.338564560282975 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.39659199826969,
            "unit": "iter/sec",
            "range": "stddev: 0.004694638166162984",
            "extra": "mean: 30.86744433036074 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 61.54186129106618,
            "unit": "iter/sec",
            "range": "stddev: 0.0020913235097846624",
            "extra": "mean: 16.24910230242202 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 53.985473122450614,
            "unit": "iter/sec",
            "range": "stddev: 0.012061174486870843",
            "extra": "mean: 18.523501641483918 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 665.417570621437,
            "unit": "iter/sec",
            "range": "stddev: 0.00013335465749725306",
            "extra": "mean: 1.5028157417996861 msec\nrounds: 479"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 65.71634476698793,
            "unit": "iter/sec",
            "range": "stddev: 0.001957644339288489",
            "extra": "mean: 15.216914506516222 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 65.14722574470136,
            "unit": "iter/sec",
            "range": "stddev: 0.0036136318385192414",
            "extra": "mean: 15.34984780347816 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 651.3321263995258,
            "unit": "iter/sec",
            "range": "stddev: 0.00013613603106181092",
            "extra": "mean: 1.5353150251130128 msec\nrounds: 511"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 44.45682440547353,
            "unit": "iter/sec",
            "range": "stddev: 0.003146281725677328",
            "extra": "mean: 22.493734390009195 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 21.804517387873144,
            "unit": "iter/sec",
            "range": "stddev: 0.002739717325972797",
            "extra": "mean: 45.86205611485639 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 20.12982417435592,
            "unit": "iter/sec",
            "range": "stddev: 0.017326844005926424",
            "extra": "mean: 49.677532766229255 msec\nrounds: 13"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 20.30036097045436,
            "unit": "iter/sec",
            "range": "stddev: 0.005198454640054509",
            "extra": "mean: 49.26020780888697 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 17.99857936330404,
            "unit": "iter/sec",
            "range": "stddev: 0.004948190601447524",
            "extra": "mean: 55.55994058280097 msec\nrounds: 12"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.92100014929905,
            "unit": "iter/sec",
            "range": "stddev: 0.0004851804785301413",
            "extra": "mean: 12.059671231648228 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 84.05455133945951,
            "unit": "iter/sec",
            "range": "stddev: 0.0005213750631927208",
            "extra": "mean: 11.897035723401082 msec\nrounds: 74"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.39791263638091,
            "unit": "iter/sec",
            "range": "stddev: 0.0005472710241078435",
            "extra": "mean: 12.136229766073866 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.32825956304825,
            "unit": "iter/sec",
            "range": "stddev: 0.0005218662875558775",
            "extra": "mean: 12.931882931939874 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 68.15050372695913,
            "unit": "iter/sec",
            "range": "stddev: 0.0025196227966083748",
            "extra": "mean: 14.673405849007946 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 581.353325746679,
            "unit": "iter/sec",
            "range": "stddev: 0.00014334474472275683",
            "extra": "mean: 1.7201243300975688 msec\nrounds: 418"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 60.54259180208161,
            "unit": "iter/sec",
            "range": "stddev: 0.002952402630942171",
            "extra": "mean: 16.517297496431553 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 62.943059680917194,
            "unit": "iter/sec",
            "range": "stddev: 0.0019181643342570359",
            "extra": "mean: 15.887375114419099 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 61.17191622515158,
            "unit": "iter/sec",
            "range": "stddev: 0.0020120661412652814",
            "extra": "mean: 16.347370847749215 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 57.02024044931455,
            "unit": "iter/sec",
            "range": "stddev: 0.010872428828978832",
            "extra": "mean: 17.537632113089785 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 691.7830766940848,
            "unit": "iter/sec",
            "range": "stddev: 0.00013551634193906882",
            "extra": "mean: 1.4455398428924167 msec\nrounds: 521"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 655.4387224938815,
            "unit": "iter/sec",
            "range": "stddev: 0.00012013972427508303",
            "extra": "mean: 1.5256956381751385 msec\nrounds: 464"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 683.9761150611871,
            "unit": "iter/sec",
            "range": "stddev: 0.00012151274300663491",
            "extra": "mean: 1.462039357778659 msec\nrounds: 459"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 59.36260742596023,
            "unit": "iter/sec",
            "range": "stddev: 0.0036522986545234996",
            "extra": "mean: 16.845621231298608 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 53.044072199241455,
            "unit": "iter/sec",
            "range": "stddev: 0.002728157673461724",
            "extra": "mean: 18.85224792402534 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 67.22270683212085,
            "unit": "iter/sec",
            "range": "stddev: 0.0030438619089215506",
            "extra": "mean: 14.875925816217991 msec\nrounds: 74"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 58.42965354074936,
            "unit": "iter/sec",
            "range": "stddev: 0.007089882548617634",
            "extra": "mean: 17.11459745867894 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 64.86379057257271,
            "unit": "iter/sec",
            "range": "stddev: 0.0029484400167300263",
            "extra": "mean: 15.416922001823993 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 646.8588096252646,
            "unit": "iter/sec",
            "range": "stddev: 0.00012998810588114735",
            "extra": "mean: 1.5459324123286124 msec\nrounds: 432"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 732.5089369701467,
            "unit": "iter/sec",
            "range": "stddev: 0.00013672576791937948",
            "extra": "mean: 1.3651710573474614 msec\nrounds: 486"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 273.46610034946565,
            "unit": "iter/sec",
            "range": "stddev: 0.0020765990984248396",
            "extra": "mean: 3.65676037622977 msec\nrounds: 232"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 681.2998650404629,
            "unit": "iter/sec",
            "range": "stddev: 0.00013849559691599868",
            "extra": "mean: 1.467782471879118 msec\nrounds: 463"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 733.6918795835244,
            "unit": "iter/sec",
            "range": "stddev: 0.0001102686655845496",
            "extra": "mean: 1.3629699712195857 msec\nrounds: 550"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 89.00710789524108,
            "unit": "iter/sec",
            "range": "stddev: 0.0032226419130883025",
            "extra": "mean: 11.235057779621068 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 99.2368678376585,
            "unit": "iter/sec",
            "range": "stddev: 0.0003189198551616",
            "extra": "mean: 10.076900065365818 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 113.62863415645606,
            "unit": "iter/sec",
            "range": "stddev: 0.0006983402367025143",
            "extra": "mean: 8.800598611641261 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 132.70265895645667,
            "unit": "iter/sec",
            "range": "stddev: 0.00045756558715152293",
            "extra": "mean: 7.535644032031996 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 116.93455659878418,
            "unit": "iter/sec",
            "range": "stddev: 0.000481999751609369",
            "extra": "mean: 8.551791951724878 msec\nrounds: 103"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 116.19539692851407,
            "unit": "iter/sec",
            "range": "stddev: 0.0004990478472177099",
            "extra": "mean: 8.606192899493443 msec\nrounds: 97"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 123.16243491251028,
            "unit": "iter/sec",
            "range": "stddev: 0.000703290473910168",
            "extra": "mean: 8.119358802140932 msec\nrounds: 127"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 116.44338550210367,
            "unit": "iter/sec",
            "range": "stddev: 0.0005717091187218028",
            "extra": "mean: 8.58786435732697 msec\nrounds: 118"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 254.51639159598193,
            "unit": "iter/sec",
            "range": "stddev: 0.00035765068807341855",
            "extra": "mean: 3.9290200278628613 msec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 7314.9063778526515,
            "unit": "iter/sec",
            "range": "stddev: 0.000013823098061728054",
            "extra": "mean: 136.70714953067628 usec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7262.900286293541,
            "unit": "iter/sec",
            "range": "stddev: 0.00001730882747969084",
            "extra": "mean: 137.68604284533384 usec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 46.78055139255929,
            "unit": "iter/sec",
            "range": "stddev: 0.0034389880575687363",
            "extra": "mean: 21.376404728719287 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 93.20438791663385,
            "unit": "iter/sec",
            "range": "stddev: 0.0014935574273739769",
            "extra": "mean: 10.72910860049255 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 690.6689177545157,
            "unit": "iter/sec",
            "range": "stddev: 0.00017032645453653636",
            "extra": "mean: 1.4478717288323517 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 655.3484890910729,
            "unit": "iter/sec",
            "range": "stddev: 0.00023307132331113723",
            "extra": "mean: 1.5259057076440916 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 61.89080214801595,
            "unit": "iter/sec",
            "range": "stddev: 0.0042399543227879324",
            "extra": "mean: 16.157489728577662 msec\nrounds: 33"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "54761247577fcbddb5d496e0f471c0f7066c218b",
          "message": "Merge pull request #133 from disnana/copilot/conduct-audit-based-on-prompt\n\nv1.4.0 security audit: fix SQL injection in create_table(), V2Engine callback ordering, async attribute inheritance",
          "timestamp": "2026-03-12T20:30:44+09:00",
          "tree_id": "59670ae6a3245cf4bdbf913b377908f3dc20749a",
          "url": "https://github.com/disnana/NanaSQLite/commit/54761247577fcbddb5d496e0f471c0f7066c218b"
        },
        "date": 1773315350832,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4196.082413386023,
            "unit": "iter/sec",
            "range": "stddev: 0.004283392111741639",
            "extra": "mean: 238.31753084969827 usec\nrounds: 4704"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 3860.441662787535,
            "unit": "iter/sec",
            "range": "stddev: 0.004635697313774725",
            "extra": "mean: 259.03771831068764 usec\nrounds: 6238"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 409.8197901671064,
            "unit": "iter/sec",
            "range": "stddev: 0.03892202603800419",
            "extra": "mean: 2.4400969011092513 msec\nrounds: 1805"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2534473.222619506,
            "unit": "iter/sec",
            "range": "stddev: 3.509264485161747e-8",
            "extra": "mean: 394.559307660147 nsec\nrounds: 54934"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 87312.6800347901,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018758044718424968",
            "extra": "mean: 11.453090199516792 usec\nrounds: 7332"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 493.42668025085624,
            "unit": "iter/sec",
            "range": "stddev: 0.0001536367068828017",
            "extra": "mean: 2.026643552171933 msec\nrounds: 303"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2807.8776439180624,
            "unit": "iter/sec",
            "range": "stddev: 0.0000042332431719074",
            "extra": "mean: 356.1408746446009 usec\nrounds: 2055"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2297157.470403687,
            "unit": "iter/sec",
            "range": "stddev: 1.0706260417547396e-7",
            "extra": "mean: 435.3206137950424 nsec\nrounds: 139179"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 118089.96465413367,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012276338073509268",
            "extra": "mean: 8.468120072089425 usec\nrounds: 7956"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 78951.41460129069,
            "unit": "iter/sec",
            "range": "stddev: 0.00000416503200255504",
            "extra": "mean: 12.666017512796435 usec\nrounds: 334"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 71260.5790252315,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010570270123959116",
            "extra": "mean: 14.03300413326597 usec\nrounds: 18001"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5821988.669500169,
            "unit": "iter/sec",
            "range": "stddev: 1.2884486617828786e-8",
            "extra": "mean: 171.7626152795038 nsec\nrounds: 138103"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1949917.969205666,
            "unit": "iter/sec",
            "range": "stddev: 3.2981481746232214e-7",
            "extra": "mean: 512.8420865865285 nsec\nrounds: 3961"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 89939.34982327544,
            "unit": "iter/sec",
            "range": "stddev: 5.065913327459566e-7",
            "extra": "mean: 11.118603836529065 usec\nrounds: 345"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70848.9960073882,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016234050669534787",
            "extra": "mean: 14.114526053350412 usec\nrounds: 11724"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3783.69969093384,
            "unit": "iter/sec",
            "range": "stddev: 0.004554868532945108",
            "extra": "mean: 264.2915880443974 usec\nrounds: 6431"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4674.505297439963,
            "unit": "iter/sec",
            "range": "stddev: 0.003918148330377265",
            "extra": "mean: 213.92638073330656 usec\nrounds: 8360"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51324.904683960616,
            "unit": "iter/sec",
            "range": "stddev: 0.000003443227901127261",
            "extra": "mean: 19.4837185993354 usec\nrounds: 9607"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 8890.635733827732,
            "unit": "iter/sec",
            "range": "stddev: 0.002610332575941865",
            "extra": "mean: 112.47789583765399 usec\nrounds: 8433"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7471.785730430871,
            "unit": "iter/sec",
            "range": "stddev: 0.00001552669391926839",
            "extra": "mean: 133.83681439461375 usec\nrounds: 1090"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12450.523384180038,
            "unit": "iter/sec",
            "range": "stddev: 0.000005287728912805596",
            "extra": "mean: 80.31790866483784 usec\nrounds: 3555"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21975.11026120141,
            "unit": "iter/sec",
            "range": "stddev: 0.000004205022796725986",
            "extra": "mean: 45.5060287804594 usec\nrounds: 5406"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8317.469959312173,
            "unit": "iter/sec",
            "range": "stddev: 0.0000077919307356494",
            "extra": "mean: 120.22886826064311 usec\nrounds: 3985"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8716.198807481616,
            "unit": "iter/sec",
            "range": "stddev: 0.002497749099996996",
            "extra": "mean: 114.72891131643787 usec\nrounds: 7767"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2114.511176085384,
            "unit": "iter/sec",
            "range": "stddev: 0.005081002951785599",
            "extra": "mean: 472.9225417721888 usec\nrounds: 3534"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2169.8434886359923,
            "unit": "iter/sec",
            "range": "stddev: 0.005060035185343119",
            "extra": "mean: 460.8627328363763 usec\nrounds: 2901"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2072.152352468494,
            "unit": "iter/sec",
            "range": "stddev: 0.0053361944416439305",
            "extra": "mean: 482.58999817688573 usec\nrounds: 5159"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 423.66854386799355,
            "unit": "iter/sec",
            "range": "stddev: 0.007901431619405127",
            "extra": "mean: 2.36033572582528 msec\nrounds: 1235"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1361.1486940528039,
            "unit": "iter/sec",
            "range": "stddev: 0.0035333572721149425",
            "extra": "mean: 734.6735917752761 usec\nrounds: 1107"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15422.49358439113,
            "unit": "iter/sec",
            "range": "stddev: 0.000007268832558817564",
            "extra": "mean: 64.8403576586399 usec\nrounds: 2166"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28639.77100788798,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032419615076643363",
            "extra": "mean: 34.91648029324604 usec\nrounds: 6520"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2328.3952008968936,
            "unit": "iter/sec",
            "range": "stddev: 0.000022226670049007856",
            "extra": "mean: 429.4803560902384 usec\nrounds: 1195"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 113339.60672342313,
            "unit": "iter/sec",
            "range": "stddev: 0.000001162271063930323",
            "extra": "mean: 8.82304102607528 usec\nrounds: 15939"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44444.27700098568,
            "unit": "iter/sec",
            "range": "stddev: 0.000001575359231195259",
            "extra": "mean: 22.50008476857036 usec\nrounds: 12391"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 57874.29815912505,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016645821563381446",
            "extra": "mean: 17.27882724815955 usec\nrounds: 17024"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70992.65387149235,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017445540990068608",
            "extra": "mean: 14.085964469086536 usec\nrounds: 12635"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 98496.40272353787,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013496540646607918",
            "extra": "mean: 10.152655044741326 usec\nrounds: 13035"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1282.2135181009862,
            "unit": "iter/sec",
            "range": "stddev: 0.005244223304315444",
            "extra": "mean: 779.9013080762425 usec\nrounds: 305"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 902.783069344665,
            "unit": "iter/sec",
            "range": "stddev: 0.008117183760939378",
            "extra": "mean: 1.1076858150717261 msec\nrounds: 2098"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 257543.10535030504,
            "unit": "iter/sec",
            "range": "stddev: 6.097649170255347e-7",
            "extra": "mean: 3.882845159608601 usec\nrounds: 28317"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 3318.4626437504144,
            "unit": "iter/sec",
            "range": "stddev: 0.010002709011900823",
            "extra": "mean: 301.34435952843324 usec\nrounds: 7828"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 159148.56995136492,
            "unit": "iter/sec",
            "range": "stddev: 8.294160178316945e-7",
            "extra": "mean: 6.283436918758337 usec\nrounds: 17258"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 8276.909477378058,
            "unit": "iter/sec",
            "range": "stddev: 0.00323570208458731",
            "extra": "mean: 120.81804237839482 usec\nrounds: 12763"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2488.0466461361143,
            "unit": "iter/sec",
            "range": "stddev: 0.005081958996380751",
            "extra": "mean: 401.92172504200414 usec\nrounds: 2954"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 2005.8464191234548,
            "unit": "iter/sec",
            "range": "stddev: 0.005101873775989918",
            "extra": "mean: 498.5426553429724 usec\nrounds: 2228"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3866.7773223418553,
            "unit": "iter/sec",
            "range": "stddev: 0.004300346426803707",
            "extra": "mean: 258.6132886996361 usec\nrounds: 4240"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 363753.6352098031,
            "unit": "iter/sec",
            "range": "stddev: 3.9182518337645255e-7",
            "extra": "mean: 2.7491134196452154 usec\nrounds: 49633"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8354.506059092886,
            "unit": "iter/sec",
            "range": "stddev: 0.002571264211489222",
            "extra": "mean: 119.69588542121159 usec\nrounds: 8266"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37342.21267207561,
            "unit": "iter/sec",
            "range": "stddev: 0.000002753193916590222",
            "extra": "mean: 26.779345101523585 usec\nrounds: 9751"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 8389.460760334083,
            "unit": "iter/sec",
            "range": "stddev: 0.0026203584992554848",
            "extra": "mean: 119.19717232936654 usec\nrounds: 7662"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4221.441165205717,
            "unit": "iter/sec",
            "range": "stddev: 0.004211032374303452",
            "extra": "mean: 236.8859261245368 usec\nrounds: 6076"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4021.6610169848864,
            "unit": "iter/sec",
            "range": "stddev: 0.004279632720003499",
            "extra": "mean: 248.6534781963594 usec\nrounds: 5537"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4099.175634572943,
            "unit": "iter/sec",
            "range": "stddev: 0.004268240262834026",
            "extra": "mean: 243.951489066699 usec\nrounds: 4864"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4410.9476223020965,
            "unit": "iter/sec",
            "range": "stddev: 0.003484995842169724",
            "extra": "mean: 226.70865438163938 usec\nrounds: 1272"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1205481.8051954692,
            "unit": "iter/sec",
            "range": "stddev: 1.293709872872738e-7",
            "extra": "mean: 829.5438352450701 nsec\nrounds: 109987"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1229010.6023030742,
            "unit": "iter/sec",
            "range": "stddev: 4.46338762223482e-7",
            "extra": "mean: 813.6626308398597 nsec\nrounds: 149165"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1242870.5521010605,
            "unit": "iter/sec",
            "range": "stddev: 2.583911179778916e-7",
            "extra": "mean: 804.5890204008051 nsec\nrounds: 143616"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1242842.081557894,
            "unit": "iter/sec",
            "range": "stddev: 2.6864607298494755e-7",
            "extra": "mean: 804.6074516132468 nsec\nrounds: 186848"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 86277.25408204127,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019226538318807814",
            "extra": "mean: 11.590540411138923 usec\nrounds: 14078"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 64069.194882097785,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025524279675182637",
            "extra": "mean: 15.608124963022128 usec\nrounds: 9274"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 36347.301862605906,
            "unit": "iter/sec",
            "range": "stddev: 0.000005623684553986227",
            "extra": "mean: 27.5123585178354 usec\nrounds: 143"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 18911.744932251633,
            "unit": "iter/sec",
            "range": "stddev: 0.000006181214933056569",
            "extra": "mean: 52.87719370065235 usec\nrounds: 3921"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 23.941257554637705,
            "unit": "iter/sec",
            "range": "stddev: 0.17551078292360542",
            "extra": "mean: 41.76890030600286 msec\nrounds: 180"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 50.71400692494639,
            "unit": "iter/sec",
            "range": "stddev: 0.03217212040275232",
            "extra": "mean: 19.718418256319964 msec\nrounds: 195"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 45.63032282149506,
            "unit": "iter/sec",
            "range": "stddev: 0.03763674880953439",
            "extra": "mean: 21.91525148555229 msec\nrounds: 192"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 20.795553601350754,
            "unit": "iter/sec",
            "range": "stddev: 0.2672630189343557",
            "extra": "mean: 48.087202638118086 msec\nrounds: 190"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21542.34666406135,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024158988246786784",
            "extra": "mean: 46.42019811464083 usec\nrounds: 13223"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 16745.514577580958,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032554651591276842",
            "extra": "mean: 59.717484068170045 usec\nrounds: 9364"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21544.805710732908,
            "unit": "iter/sec",
            "range": "stddev: 0.000002433625983270486",
            "extra": "mean: 46.414899880105814 usec\nrounds: 14455"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4325.066248887427,
            "unit": "iter/sec",
            "range": "stddev: 0.000009283842624198154",
            "extra": "mean: 231.21033123070393 usec\nrounds: 2515"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4182.850506501447,
            "unit": "iter/sec",
            "range": "stddev: 0.004272396388326689",
            "extra": "mean: 239.07141755262109 usec\nrounds: 17624"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 408851.3764067036,
            "unit": "iter/sec",
            "range": "stddev: 4.7324247707901135e-7",
            "extra": "mean: 2.4458765647036813 usec\nrounds: 36736"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 3816.4822096699695,
            "unit": "iter/sec",
            "range": "stddev: 0.004389872532162027",
            "extra": "mean: 262.0213969467121 usec\nrounds: 6230"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4194.281232239173,
            "unit": "iter/sec",
            "range": "stddev: 0.00002378174310161613",
            "extra": "mean: 238.419873305953 usec\nrounds: 969"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3633.4743117801863,
            "unit": "iter/sec",
            "range": "stddev: 0.000022517269075094123",
            "extra": "mean: 275.2186789260826 usec\nrounds: 1272"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5149.444434660925,
            "unit": "iter/sec",
            "range": "stddev: 0.000015948393493867543",
            "extra": "mean: 194.19570648612057 usec\nrounds: 2595"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5148.960249004335,
            "unit": "iter/sec",
            "range": "stddev: 0.000012911805508638664",
            "extra": "mean: 194.21396779929927 usec\nrounds: 2653"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21637.83692544249,
            "unit": "iter/sec",
            "range": "stddev: 0.000004088686845301397",
            "extra": "mean: 46.21534044487444 usec\nrounds: 12273"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21664.87854317355,
            "unit": "iter/sec",
            "range": "stddev: 0.000004333903194430983",
            "extra": "mean: 46.15765548868461 usec\nrounds: 10881"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21723.929542341386,
            "unit": "iter/sec",
            "range": "stddev: 0.000008476295650743862",
            "extra": "mean: 46.03218759529363 usec\nrounds: 13047"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21612.057157084073,
            "unit": "iter/sec",
            "range": "stddev: 0.000003605805948735566",
            "extra": "mean: 46.270468041595784 usec\nrounds: 13057"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 212.92029570232808,
            "unit": "iter/sec",
            "range": "stddev: 0.010882254223263475",
            "extra": "mean: 4.696593139237623 msec\nrounds: 202"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3756.167654073699,
            "unit": "iter/sec",
            "range": "stddev: 0.003770262345683889",
            "extra": "mean: 266.228798098366 usec\nrounds: 4798"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 227775.40023272706,
            "unit": "iter/sec",
            "range": "stddev: 0.000018055404459346805",
            "extra": "mean: 4.390289728294894 usec\nrounds: 40785"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 934334.6196803424,
            "unit": "iter/sec",
            "range": "stddev: 8.35816432628155e-7",
            "extra": "mean: 1.0702803673721555 usec\nrounds: 75735"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 50.30048332710223,
            "unit": "iter/sec",
            "range": "stddev: 0.006442810483973435",
            "extra": "mean: 19.880524676016254 msec\nrounds: 74"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 95.20671735135397,
            "unit": "iter/sec",
            "range": "stddev: 0.0036108953767302237",
            "extra": "mean: 10.503460552153767 msec\nrounds: 49"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 155729.03142515544,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010997250672002634",
            "extra": "mean: 6.421410258886813 usec\nrounds: 21740"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 120922.04614179014,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023046976190849206",
            "extra": "mean: 8.26979059573161 usec\nrounds: 4497"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 72070.14361369515,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016833849301921175",
            "extra": "mean: 13.875371268303878 usec\nrounds: 12518"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 83367.27730283045,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015710654072133827",
            "extra": "mean: 11.995114058571376 usec\nrounds: 14595"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 1888.9627360952072,
            "unit": "iter/sec",
            "range": "stddev: 0.007160786519046763",
            "extra": "mean: 529.3910678551354 usec\nrounds: 2772"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 770.0697531729852,
            "unit": "iter/sec",
            "range": "stddev: 0.009721063325542973",
            "extra": "mean: 1.2985836619080455 msec\nrounds: 1736"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 3878.857493958244,
            "unit": "iter/sec",
            "range": "stddev: 0.0000603253789063861",
            "extra": "mean: 257.8078729516648 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4885.336381715451,
            "unit": "iter/sec",
            "range": "stddev: 0.00002389140631090998",
            "extra": "mean: 204.6941954176873 usec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1405.5802014303438,
            "unit": "iter/sec",
            "range": "stddev: 0.0003265252098562633",
            "extra": "mean: 711.4499755918459 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 190.84960650317234,
            "unit": "iter/sec",
            "range": "stddev: 0.004740190877128027",
            "extra": "mean: 5.239727858612995 msec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 9351.848842388985,
            "unit": "iter/sec",
            "range": "stddev: 0.000026968789263465975",
            "extra": "mean: 106.93072748003743 usec\nrounds: 3916"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7299.319445486519,
            "unit": "iter/sec",
            "range": "stddev: 0.000017927422133982588",
            "extra": "mean: 136.9990733339315 usec\nrounds: 3211"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 292.1819284037928,
            "unit": "iter/sec",
            "range": "stddev: 0.0003677630136283985",
            "extra": "mean: 3.422525155690016 msec\nrounds: 216"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7930.919415452792,
            "unit": "iter/sec",
            "range": "stddev: 0.000015960162588461804",
            "extra": "mean: 126.08878587917262 usec\nrounds: 2346"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1575.681198190423,
            "unit": "iter/sec",
            "range": "stddev: 0.000049646691346808474",
            "extra": "mean: 634.6461461547178 usec\nrounds: 944"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6796.451187885751,
            "unit": "iter/sec",
            "range": "stddev: 0.000019749238082230725",
            "extra": "mean: 147.13561127054624 usec\nrounds: 343"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 9913.415031627317,
            "unit": "iter/sec",
            "range": "stddev: 0.000011113285157521689",
            "extra": "mean: 100.87341211980377 usec\nrounds: 3448"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8680.454604381186,
            "unit": "iter/sec",
            "range": "stddev: 0.000024663578663921695",
            "extra": "mean: 115.20133974265376 usec\nrounds: 3015"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6509.288349890791,
            "unit": "iter/sec",
            "range": "stddev: 0.0000133063316988552",
            "extra": "mean: 153.62662494691565 usec\nrounds: 344"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2704.7456562856937,
            "unit": "iter/sec",
            "range": "stddev: 0.000055661090092624795",
            "extra": "mean: 369.7205309031738 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 4765.499966435978,
            "unit": "iter/sec",
            "range": "stddev: 0.000018365963679100614",
            "extra": "mean: 209.84157109288154 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7993.150514356784,
            "unit": "iter/sec",
            "range": "stddev: 0.000010642539333690124",
            "extra": "mean: 125.10711492344154 usec\nrounds: 3244"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1149.7232317379776,
            "unit": "iter/sec",
            "range": "stddev: 0.00011652831556660538",
            "extra": "mean: 869.7745443382503 usec\nrounds: 46"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 269.2482172634656,
            "unit": "iter/sec",
            "range": "stddev: 0.00024080652831332452",
            "extra": "mean: 3.7140450182497466 msec\nrounds: 228"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.178454059584766,
            "unit": "iter/sec",
            "range": "stddev: 0.005060781940131665",
            "extra": "mean: 17.188493853340063 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 44.59876048986114,
            "unit": "iter/sec",
            "range": "stddev: 0.004289267353320811",
            "extra": "mean: 22.42214781344282 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 15.537651123767265,
            "unit": "iter/sec",
            "range": "stddev: 0.013915023337244405",
            "extra": "mean: 64.35979235435038 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.489892874031508,
            "unit": "iter/sec",
            "range": "stddev: 0.005997712773104914",
            "extra": "mean: 33.90992311405069 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 47.793338623921294,
            "unit": "iter/sec",
            "range": "stddev: 0.003525083097028599",
            "extra": "mean: 20.92341796560504 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 61.65804328834174,
            "unit": "iter/sec",
            "range": "stddev: 0.0105567854643053",
            "extra": "mean: 16.218484185810667 msec\nrounds: 80"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6925.851792511459,
            "unit": "iter/sec",
            "range": "stddev: 0.000014808224723130568",
            "extra": "mean: 144.38657221646653 usec\nrounds: 3831"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1558.450167019868,
            "unit": "iter/sec",
            "range": "stddev: 0.0000812868117959672",
            "extra": "mean: 641.6631222236902 usec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4260.553054566098,
            "unit": "iter/sec",
            "range": "stddev: 0.000021742410081986702",
            "extra": "mean: 234.71131263775374 usec\nrounds: 938"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 675.6326830546859,
            "unit": "iter/sec",
            "range": "stddev: 0.00015293557026218403",
            "extra": "mean: 1.4800941770294134 msec\nrounds: 498"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 452.3186869378758,
            "unit": "iter/sec",
            "range": "stddev: 0.00016661231524209448",
            "extra": "mean: 2.210830613189647 msec\nrounds: 310"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 67.33402612491471,
            "unit": "iter/sec",
            "range": "stddev: 0.002046790294507299",
            "extra": "mean: 14.851332343395745 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 62.49934665689359,
            "unit": "iter/sec",
            "range": "stddev: 0.002458748240147373",
            "extra": "mean: 16.000167257583666 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 33.06205704769381,
            "unit": "iter/sec",
            "range": "stddev: 0.004615106976993686",
            "extra": "mean: 30.246151912370294 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 61.83414433690624,
            "unit": "iter/sec",
            "range": "stddev: 0.002495126608409191",
            "extra": "mean: 16.172294623362994 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 64.41331899460772,
            "unit": "iter/sec",
            "range": "stddev: 0.0021157359202383453",
            "extra": "mean: 15.524739535370221 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 665.6007460908872,
            "unit": "iter/sec",
            "range": "stddev: 0.00011690722230084613",
            "extra": "mean: 1.5024021620664632 msec\nrounds: 462"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 66.05865618621188,
            "unit": "iter/sec",
            "range": "stddev: 0.002233940806845225",
            "extra": "mean: 15.138061500692856 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 63.53482856426387,
            "unit": "iter/sec",
            "range": "stddev: 0.003073029064106375",
            "extra": "mean: 15.739398729761666 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 647.3950457112151,
            "unit": "iter/sec",
            "range": "stddev: 0.00014719892629718373",
            "extra": "mean: 1.5446519194496158 msec\nrounds: 438"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 43.11410628974233,
            "unit": "iter/sec",
            "range": "stddev: 0.003950784962834457",
            "extra": "mean: 23.194264848716557 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 18.52758298760432,
            "unit": "iter/sec",
            "range": "stddev: 0.00542229449914551",
            "extra": "mean: 53.97358093978255 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 18.23552351894136,
            "unit": "iter/sec",
            "range": "stddev: 0.011075120697420178",
            "extra": "mean: 54.83801981123785 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 17.779481975067778,
            "unit": "iter/sec",
            "range": "stddev: 0.011906466164248227",
            "extra": "mean: 56.2446083301135 msec\nrounds: 12"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 18.473902507032104,
            "unit": "iter/sec",
            "range": "stddev: 0.004082139032673881",
            "extra": "mean: 54.130414492517176 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.96599288193232,
            "unit": "iter/sec",
            "range": "stddev: 0.000612466508368878",
            "extra": "mean: 12.053131232010749 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 81.6464636587006,
            "unit": "iter/sec",
            "range": "stddev: 0.00040657736521402935",
            "extra": "mean: 12.24792789777412 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.83839767194232,
            "unit": "iter/sec",
            "range": "stddev: 0.0003527796024814539",
            "extra": "mean: 12.071696557437201 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.62158333523215,
            "unit": "iter/sec",
            "range": "stddev: 0.0004416983312708443",
            "extra": "mean: 12.883014711014066 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 67.89227838681808,
            "unit": "iter/sec",
            "range": "stddev: 0.001975840761344615",
            "extra": "mean: 14.72921551258706 msec\nrounds: 74"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 569.514708907428,
            "unit": "iter/sec",
            "range": "stddev: 0.00022208864665540176",
            "extra": "mean: 1.7558809006327971 msec\nrounds: 450"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 61.82641810337535,
            "unit": "iter/sec",
            "range": "stddev: 0.002120597761932787",
            "extra": "mean: 16.17431561906068 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 60.4317695040244,
            "unit": "iter/sec",
            "range": "stddev: 0.0026123674472031517",
            "extra": "mean: 16.54758760511565 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 58.52426270211345,
            "unit": "iter/sec",
            "range": "stddev: 0.006514352593635044",
            "extra": "mean: 17.08693034015596 msec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 62.56031353863635,
            "unit": "iter/sec",
            "range": "stddev: 0.003455454053507422",
            "extra": "mean: 15.984574619857275 msec\nrounds: 58"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 700.5187658064594,
            "unit": "iter/sec",
            "range": "stddev: 0.0001513500910634462",
            "extra": "mean: 1.4275135068634004 msec\nrounds: 444"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 658.1517328217934,
            "unit": "iter/sec",
            "range": "stddev: 0.00011189775985718923",
            "extra": "mean: 1.5194064683421085 msec\nrounds: 465"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 678.0398092208629,
            "unit": "iter/sec",
            "range": "stddev: 0.00012636639085874667",
            "extra": "mean: 1.4748396574960727 msec\nrounds: 475"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 61.730979459775284,
            "unit": "iter/sec",
            "range": "stddev: 0.002257488806598257",
            "extra": "mean: 16.199321778971825 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 52.14210584948132,
            "unit": "iter/sec",
            "range": "stddev: 0.0024734339768439874",
            "extra": "mean: 19.178358520591807 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 66.6837604014147,
            "unit": "iter/sec",
            "range": "stddev: 0.004502421523911806",
            "extra": "mean: 14.996154895589616 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 56.61960253184368,
            "unit": "iter/sec",
            "range": "stddev: 0.004264079703119422",
            "extra": "mean: 17.66172765761797 msec\nrounds: 61"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 64.88448647275412,
            "unit": "iter/sec",
            "range": "stddev: 0.005328628717840483",
            "extra": "mean: 15.412004538556586 msec\nrounds: 73"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 642.0641466119547,
            "unit": "iter/sec",
            "range": "stddev: 0.00013315295362659933",
            "extra": "mean: 1.5574767805939669 msec\nrounds: 417"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 735.0513663557066,
            "unit": "iter/sec",
            "range": "stddev: 0.00010049671648403875",
            "extra": "mean: 1.3604491410687063 msec\nrounds: 549"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 278.8812643126776,
            "unit": "iter/sec",
            "range": "stddev: 0.0021501401286524798",
            "extra": "mean: 3.585755401907582 msec\nrounds: 219"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 684.8661106310741,
            "unit": "iter/sec",
            "range": "stddev: 0.00013504866699004701",
            "extra": "mean: 1.4601394118896374 msec\nrounds: 450"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 726.9114601247601,
            "unit": "iter/sec",
            "range": "stddev: 0.00009917495428657458",
            "extra": "mean: 1.37568336015554 msec\nrounds: 566"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 85.24506712729001,
            "unit": "iter/sec",
            "range": "stddev: 0.003713480680977018",
            "extra": "mean: 11.7308840698873 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 101.96467253233847,
            "unit": "iter/sec",
            "range": "stddev: 0.000494311660406289",
            "extra": "mean: 9.807318310985075 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 115.50672157870034,
            "unit": "iter/sec",
            "range": "stddev: 0.0006073208075509914",
            "extra": "mean: 8.657504830302464 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 130.31596232953947,
            "unit": "iter/sec",
            "range": "stddev: 0.0003761018055801126",
            "extra": "mean: 7.673657026536988 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 114.90033060382545,
            "unit": "iter/sec",
            "range": "stddev: 0.0004278868490281132",
            "extra": "mean: 8.703195149611748 msec\nrounds: 111"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 112.85418226185945,
            "unit": "iter/sec",
            "range": "stddev: 0.00043583263827608735",
            "extra": "mean: 8.860991945160398 msec\nrounds: 96"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 116.90991611643008,
            "unit": "iter/sec",
            "range": "stddev: 0.0005360164400993114",
            "extra": "mean: 8.553594367513737 msec\nrounds: 122"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 118.67771451163222,
            "unit": "iter/sec",
            "range": "stddev: 0.000678990093397884",
            "extra": "mean: 8.426181816148683 msec\nrounds: 118"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 236.83004132821873,
            "unit": "iter/sec",
            "range": "stddev: 0.00043550516713409523",
            "extra": "mean: 4.222437298881847 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 6928.449202036973,
            "unit": "iter/sec",
            "range": "stddev: 0.000015303491808000092",
            "extra": "mean: 144.33244306763464 usec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 6891.995800183153,
            "unit": "iter/sec",
            "range": "stddev: 0.000021818906586453434",
            "extra": "mean: 145.09585162159055 usec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 46.33221015068936,
            "unit": "iter/sec",
            "range": "stddev: 0.0036182060843904986",
            "extra": "mean: 21.583257020280982 msec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 84.4440560737764,
            "unit": "iter/sec",
            "range": "stddev: 0.003291117716113543",
            "extra": "mean: 11.842159726746523 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 677.2927188503061,
            "unit": "iter/sec",
            "range": "stddev: 0.00017796622798834066",
            "extra": "mean: 1.4764664851225398 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 685.4363004310078,
            "unit": "iter/sec",
            "range": "stddev: 0.0002493557082244813",
            "extra": "mean: 1.4589247744410268 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 66.69204589183376,
            "unit": "iter/sec",
            "range": "stddev: 0.002383951974516474",
            "extra": "mean: 14.99429184736477 msec\nrounds: 27"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b591702f4d9240218a1400283e4672d39a7dbbc8",
          "message": "Merge pull request #135 from disnana/copilot/add-gh-pages-for-draft-content\n\nfeat: PR preview deployments on gh-pages",
          "timestamp": "2026-03-12T22:44:47+09:00",
          "tree_id": "a2a3aff23df6e6a6ae79141144ef61c7609c3473",
          "url": "https://github.com/disnana/NanaSQLite/commit/b591702f4d9240218a1400283e4672d39a7dbbc8"
        },
        "date": 1773323423288,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4307.753474939757,
            "unit": "iter/sec",
            "range": "stddev: 0.0040839934886751006",
            "extra": "mean: 232.139560867973 usec\nrounds: 4588"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4238.394358537447,
            "unit": "iter/sec",
            "range": "stddev: 0.004350223613202937",
            "extra": "mean: 235.93840388771008 usec\nrounds: 6544"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 662.0885981379025,
            "unit": "iter/sec",
            "range": "stddev: 0.011689169240670186",
            "extra": "mean: 1.5103718789486176 msec\nrounds: 1913"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2241757.3620146974,
            "unit": "iter/sec",
            "range": "stddev: 1.1996772067358744e-7",
            "extra": "mean: 446.07860642923754 nsec\nrounds: 106509"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 88076.28230464672,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021527534319308986",
            "extra": "mean: 11.353794390879305 usec\nrounds: 9885"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 489.56594038488464,
            "unit": "iter/sec",
            "range": "stddev: 0.00021428784761563097",
            "extra": "mean: 2.042625757857715 msec\nrounds: 295"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2790.124547016714,
            "unit": "iter/sec",
            "range": "stddev: 0.00001654104020832894",
            "extra": "mean: 358.4069396003237 usec\nrounds: 1466"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2286078.7553352606,
            "unit": "iter/sec",
            "range": "stddev: 1.0218968874716399e-7",
            "extra": "mean: 437.4302493587308 nsec\nrounds: 141364"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 118641.57603913256,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010038190576560306",
            "extra": "mean: 8.428748448774495 usec\nrounds: 9894"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 75989.47193743737,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029545915890163786",
            "extra": "mean: 13.15971771488696 usec\nrounds: 319"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 72781.3487630149,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010199577203551958",
            "extra": "mean: 13.73978384566799 usec\nrounds: 18809"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5801334.478335092,
            "unit": "iter/sec",
            "range": "stddev: 1.4334053210586084e-8",
            "extra": "mean: 172.37413283716154 nsec\nrounds: 142106"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1347691.5469730073,
            "unit": "iter/sec",
            "range": "stddev: 1.3974200582727537e-7",
            "extra": "mean: 742.0095512552983 nsec\nrounds: 3397"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 74367.63485992422,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013603167345493441",
            "extra": "mean: 13.446709739842586 usec\nrounds: 322"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 71243.51138060645,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011873077134579841",
            "extra": "mean: 14.036365987881602 usec\nrounds: 14290"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 4083.090895782408,
            "unit": "iter/sec",
            "range": "stddev: 0.004202626753080783",
            "extra": "mean: 244.91250024165296 usec\nrounds: 7080"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 5094.12548538809,
            "unit": "iter/sec",
            "range": "stddev: 0.0035181365246681816",
            "extra": "mean: 196.30454783031638 usec\nrounds: 7388"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51679.62086039087,
            "unit": "iter/sec",
            "range": "stddev: 0.000003210103768912143",
            "extra": "mean: 19.349987158408823 usec\nrounds: 9835"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9726.13568995574,
            "unit": "iter/sec",
            "range": "stddev: 0.0023319544174165846",
            "extra": "mean: 102.81575662497781 usec\nrounds: 9744"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7479.517915079582,
            "unit": "iter/sec",
            "range": "stddev: 0.000017210888591139935",
            "extra": "mean: 133.6984564184121 usec\nrounds: 1043"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12521.618266513753,
            "unit": "iter/sec",
            "range": "stddev: 0.000006923915652170644",
            "extra": "mean: 79.8618819641128 usec\nrounds: 3723"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 22042.510708025893,
            "unit": "iter/sec",
            "range": "stddev: 0.000004078589172647105",
            "extra": "mean: 45.366882804139465 usec\nrounds: 5927"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8317.786723252091,
            "unit": "iter/sec",
            "range": "stddev: 0.00000796212007859082",
            "extra": "mean: 120.22428961835891 usec\nrounds: 3846"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8156.851314654596,
            "unit": "iter/sec",
            "range": "stddev: 0.0026275274480279994",
            "extra": "mean: 122.59632564386706 usec\nrounds: 7135"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2090.3843137186395,
            "unit": "iter/sec",
            "range": "stddev: 0.005136938500609893",
            "extra": "mean: 478.3809338011505 usec\nrounds: 4250"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 741.895395723349,
            "unit": "iter/sec",
            "range": "stddev: 0.04072487923843733",
            "extra": "mean: 1.3478989164301238 msec\nrounds: 3216"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2235.1681588519973,
            "unit": "iter/sec",
            "range": "stddev: 0.004675504330568228",
            "extra": "mean: 447.39363167807886 usec\nrounds: 3516"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 178.55129460736947,
            "unit": "iter/sec",
            "range": "stddev: 0.11941794534759771",
            "extra": "mean: 5.600631472311521 msec\nrounds: 1330"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1298.4108747375121,
            "unit": "iter/sec",
            "range": "stddev: 0.00420121438618504",
            "extra": "mean: 770.1722308835106 usec\nrounds: 1030"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15750.99885608219,
            "unit": "iter/sec",
            "range": "stddev: 0.0000049069032606873765",
            "extra": "mean: 63.48803711669713 usec\nrounds: 2465"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28487.625092567654,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031307818156753927",
            "extra": "mean: 35.10296125951536 usec\nrounds: 6657"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2330.8496405626474,
            "unit": "iter/sec",
            "range": "stddev: 0.00003046585236954832",
            "extra": "mean: 429.02810314208364 usec\nrounds: 1097"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 113574.94146829388,
            "unit": "iter/sec",
            "range": "stddev: 0.000001045605498547642",
            "extra": "mean: 8.80475910506337 usec\nrounds: 18500"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44580.358941750965,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019110790236635525",
            "extra": "mean: 22.431403060406215 usec\nrounds: 12124"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 57415.924908506095,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018491526372926552",
            "extra": "mean: 17.416770723340754 usec\nrounds: 15607"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70646.46568782689,
            "unit": "iter/sec",
            "range": "stddev: 0.000002343119655852315",
            "extra": "mean: 14.154989782769988 usec\nrounds: 13558"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 97116.4158408618,
            "unit": "iter/sec",
            "range": "stddev: 0.000002250662992594519",
            "extra": "mean: 10.29692036451009 usec\nrounds: 12209"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1317.9711543349108,
            "unit": "iter/sec",
            "range": "stddev: 0.00486514655669173",
            "extra": "mean: 758.7419472049303 usec\nrounds: 307"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 1005.3707151547333,
            "unit": "iter/sec",
            "range": "stddev: 0.007013392531100865",
            "extra": "mean: 994.6579753380754 usec\nrounds: 2300"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 250816.89626021052,
            "unit": "iter/sec",
            "range": "stddev: 6.554145938101716e-7",
            "extra": "mean: 3.9869722291856604 usec\nrounds: 19766"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4982.955882058636,
            "unit": "iter/sec",
            "range": "stddev: 0.0035559175147170602",
            "extra": "mean: 200.6840966825627 usec\nrounds: 9606"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 156563.68755345262,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010416967353642335",
            "extra": "mean: 6.387177101066865 usec\nrounds: 17676"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 9195.053636177867,
            "unit": "iter/sec",
            "range": "stddev: 0.0026637874478306653",
            "extra": "mean: 108.75412363724642 usec\nrounds: 15114"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2681.30411750251,
            "unit": "iter/sec",
            "range": "stddev: 0.0044838338621126074",
            "extra": "mean: 372.95284539802446 usec\nrounds: 3520"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 2156.68702792825,
            "unit": "iter/sec",
            "range": "stddev: 0.004634692844507336",
            "extra": "mean: 463.67413864431546 usec\nrounds: 1982"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3877.8886632751073,
            "unit": "iter/sec",
            "range": "stddev: 0.004116672482357322",
            "extra": "mean: 257.8722822731688 usec\nrounds: 3636"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 359382.7493401547,
            "unit": "iter/sec",
            "range": "stddev: 4.1344015711920005e-7",
            "extra": "mean: 2.7825486944936886 usec\nrounds: 36217"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8637.164040632728,
            "unit": "iter/sec",
            "range": "stddev: 0.002495801375114007",
            "extra": "mean: 115.77874349677671 usec\nrounds: 8558"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37206.41423124715,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027392787150927884",
            "extra": "mean: 26.877086133179894 usec\nrounds: 6794"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 2690.046449490624,
            "unit": "iter/sec",
            "range": "stddev: 0.02271349839800549",
            "extra": "mean: 371.74079287343 usec\nrounds: 7279"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4441.6773352587825,
            "unit": "iter/sec",
            "range": "stddev: 0.003960971239515684",
            "extra": "mean: 225.14017217365873 usec\nrounds: 5677"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4069.1233379965147,
            "unit": "iter/sec",
            "range": "stddev: 0.00406433561520954",
            "extra": "mean: 245.75317996931568 usec\nrounds: 4917"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4015.1737575947645,
            "unit": "iter/sec",
            "range": "stddev: 0.00408048498387994",
            "extra": "mean: 249.05522410044753 usec\nrounds: 4993"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4370.777711036685,
            "unit": "iter/sec",
            "range": "stddev: 0.00353075163991201",
            "extra": "mean: 228.79223472630332 usec\nrounds: 1332"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1207648.8080383257,
            "unit": "iter/sec",
            "range": "stddev: 1.6311307534635907e-7",
            "extra": "mean: 828.0553032833898 nsec\nrounds: 101123"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1211313.3684531152,
            "unit": "iter/sec",
            "range": "stddev: 2.0426426128645585e-7",
            "extra": "mean: 825.5502052924843 nsec\nrounds: 126759"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1215129.7749923635,
            "unit": "iter/sec",
            "range": "stddev: 3.6067727574094105e-7",
            "extra": "mean: 822.9573668428004 nsec\nrounds: 136706"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1449934.631816117,
            "unit": "iter/sec",
            "range": "stddev: 2.8922921499449376e-8",
            "extra": "mean: 689.6862645093579 nsec\nrounds: 54216"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 84379.97106743374,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016485900158748426",
            "extra": "mean: 11.851153625080439 usec\nrounds: 11578"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 52089.758747992804,
            "unit": "iter/sec",
            "range": "stddev: 0.000002684892618380988",
            "extra": "mean: 19.197631627321243 usec\nrounds: 8430"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 33958.865769371965,
            "unit": "iter/sec",
            "range": "stddev: 0.0000053180589080261856",
            "extra": "mean: 29.447391052203983 usec\nrounds: 184"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17484.363278515455,
            "unit": "iter/sec",
            "range": "stddev: 0.0000070689927511564835",
            "extra": "mean: 57.193961488365225 usec\nrounds: 4125"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 24.301217563202957,
            "unit": "iter/sec",
            "range": "stddev: 0.2385527177070913",
            "extra": "mean: 41.15020152382018 msec\nrounds: 188"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 54.17213669655175,
            "unit": "iter/sec",
            "range": "stddev: 0.029522650568938883",
            "extra": "mean: 18.459674308243663 msec\nrounds: 195"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 53.79228398341841,
            "unit": "iter/sec",
            "range": "stddev: 0.02971062271518236",
            "extra": "mean: 18.59002678354859 msec\nrounds: 190"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 53.323721797251885,
            "unit": "iter/sec",
            "range": "stddev: 0.02988627413267559",
            "extra": "mean: 18.75337966472431 msec\nrounds: 186"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21945.555567435084,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021395165528601598",
            "extra": "mean: 45.56731302277422 usec\nrounds: 11529"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17017.88908922383,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016009740639198308",
            "extra": "mean: 58.761694517872144 usec\nrounds: 10963"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21843.349670005537,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016266689853214035",
            "extra": "mean: 45.78052428346932 usec\nrounds: 12709"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4377.760331462937,
            "unit": "iter/sec",
            "range": "stddev: 0.000007912598906906129",
            "extra": "mean: 228.42730626731804 usec\nrounds: 2482"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4291.986950738795,
            "unit": "iter/sec",
            "range": "stddev: 0.004132035268561304",
            "extra": "mean: 232.99232068444817 usec\nrounds: 11470"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 416706.80856750475,
            "unit": "iter/sec",
            "range": "stddev: 3.4908316244872654e-7",
            "extra": "mean: 2.399768804924636 usec\nrounds: 64906"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 4319.064853210998,
            "unit": "iter/sec",
            "range": "stddev: 0.003844071191462644",
            "extra": "mean: 231.53160093360316 usec\nrounds: 5737"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4157.414384249664,
            "unit": "iter/sec",
            "range": "stddev: 0.000028098019254011154",
            "extra": "mean: 240.5341175006497 usec\nrounds: 1061"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3641.055137454304,
            "unit": "iter/sec",
            "range": "stddev: 0.00002319253336990724",
            "extra": "mean: 274.64566238323005 usec\nrounds: 1267"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5176.028242250092,
            "unit": "iter/sec",
            "range": "stddev: 0.000014465978771023465",
            "extra": "mean: 193.19832759747192 usec\nrounds: 2826"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5153.721646066104,
            "unit": "iter/sec",
            "range": "stddev: 0.000012685674235482918",
            "extra": "mean: 194.0345382764922 usec\nrounds: 2823"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21798.518726795206,
            "unit": "iter/sec",
            "range": "stddev: 0.000004964889853915586",
            "extra": "mean: 45.87467673988226 usec\nrounds: 12146"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21741.25111048425,
            "unit": "iter/sec",
            "range": "stddev: 0.0000042405185601712",
            "extra": "mean: 45.99551308791846 usec\nrounds: 12008"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21178.77407598966,
            "unit": "iter/sec",
            "range": "stddev: 0.00005912705160662262",
            "extra": "mean: 47.21708614540152 usec\nrounds: 12901"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21358.07201204892,
            "unit": "iter/sec",
            "range": "stddev: 0.000004238540885656198",
            "extra": "mean: 46.820705512925564 usec\nrounds: 13380"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 211.32345002520216,
            "unit": "iter/sec",
            "range": "stddev: 0.010613144768614882",
            "extra": "mean: 4.732082501401246 msec\nrounds: 193"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3876.3222888924925,
            "unit": "iter/sec",
            "range": "stddev: 0.003490487927145981",
            "extra": "mean: 257.9764853055371 usec\nrounds: 4217"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 224391.09266451432,
            "unit": "iter/sec",
            "range": "stddev: 0.000017959714300249966",
            "extra": "mean: 4.456504882281997 usec\nrounds: 37087"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 918745.4487400934,
            "unit": "iter/sec",
            "range": "stddev: 9.74322081054339e-7",
            "extra": "mean: 1.0884407660155853 usec\nrounds: 66747"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 54.636470596699276,
            "unit": "iter/sec",
            "range": "stddev: 0.0025685451083482004",
            "extra": "mean: 18.30279278801754 msec\nrounds: 55"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 112.82914901208201,
            "unit": "iter/sec",
            "range": "stddev: 0.0017061612210312596",
            "extra": "mean: 8.862957921387121 msec\nrounds: 55"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 156541.79478712613,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013127908653347332",
            "extra": "mean: 6.38807036395522 usec\nrounds: 22379"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 119022.37400039787,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022798543383869794",
            "extra": "mean: 8.40178166834966 usec\nrounds: 4361"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 69632.38781541707,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024954185272791938",
            "extra": "mean: 14.361133250963908 usec\nrounds: 12279"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82146.63305214536,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019994842131033493",
            "extra": "mean: 12.173353463741064 usec\nrounds: 13275"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2418.299562631919,
            "unit": "iter/sec",
            "range": "stddev: 0.004569999306944633",
            "extra": "mean: 413.5137000610732 usec\nrounds: 2397"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 320.49748118541976,
            "unit": "iter/sec",
            "range": "stddev: 0.072310838055141",
            "extra": "mean: 3.1201493262952127 msec\nrounds: 1748"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4040.3766535632594,
            "unit": "iter/sec",
            "range": "stddev: 0.00004042500384329127",
            "extra": "mean: 247.50167762653692 usec\nrounds: 9"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4301.0838900373055,
            "unit": "iter/sec",
            "range": "stddev: 0.00003172460652302488",
            "extra": "mean: 232.49953397010503 usec\nrounds: 19"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1317.312618396338,
            "unit": "iter/sec",
            "range": "stddev: 0.00029982035725670085",
            "extra": "mean: 759.121248847805 usec\nrounds: 48"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 194.41832044910964,
            "unit": "iter/sec",
            "range": "stddev: 0.004751502224157901",
            "extra": "mean: 5.143548188719987 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10209.262572792517,
            "unit": "iter/sec",
            "range": "stddev: 0.0000144946368196898",
            "extra": "mean: 97.95026750168815 usec\nrounds: 4105"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7106.979429132834,
            "unit": "iter/sec",
            "range": "stddev: 0.000015376856271485205",
            "extra": "mean: 140.70675312507777 usec\nrounds: 2768"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 296.2822288460991,
            "unit": "iter/sec",
            "range": "stddev: 0.00030745565888443593",
            "extra": "mean: 3.375160244657941 msec\nrounds: 207"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7277.484509669306,
            "unit": "iter/sec",
            "range": "stddev: 0.000016545970753144066",
            "extra": "mean: 137.41011728315456 usec\nrounds: 2629"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1726.5251726136253,
            "unit": "iter/sec",
            "range": "stddev: 0.00003152180642619911",
            "extra": "mean: 579.1980423234684 usec\nrounds: 957"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 7033.894359906832,
            "unit": "iter/sec",
            "range": "stddev: 0.000011938591177393363",
            "extra": "mean: 142.1687544385079 usec\nrounds: 363"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 10086.789973948013,
            "unit": "iter/sec",
            "range": "stddev: 0.00001535540433723844",
            "extra": "mean: 99.1395679480571 usec\nrounds: 3949"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8495.88685790076,
            "unit": "iter/sec",
            "range": "stddev: 0.00003483969120763485",
            "extra": "mean: 117.70401568731448 usec\nrounds: 2779"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6676.878080841105,
            "unit": "iter/sec",
            "range": "stddev: 0.000015256380559160528",
            "extra": "mean: 149.77059456416302 usec\nrounds: 360"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2667.4387330137083,
            "unit": "iter/sec",
            "range": "stddev: 0.00011906979572273893",
            "extra": "mean: 374.891459595095 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 5103.091428801172,
            "unit": "iter/sec",
            "range": "stddev: 0.000020935489010997716",
            "extra": "mean: 195.95964798046384 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7313.281193338846,
            "unit": "iter/sec",
            "range": "stddev: 0.00001814240658747487",
            "extra": "mean: 136.73752910127806 usec\nrounds: 3731"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1215.035476377244,
            "unit": "iter/sec",
            "range": "stddev: 0.00010783558479580279",
            "extra": "mean: 823.0212363688386 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 271.211208999135,
            "unit": "iter/sec",
            "range": "stddev: 0.00021821098443298724",
            "extra": "mean: 3.687163239640252 msec\nrounds: 205"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 59.12129036617874,
            "unit": "iter/sec",
            "range": "stddev: 0.0047011434362017246",
            "extra": "mean: 16.914380484700413 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 48.87636562842424,
            "unit": "iter/sec",
            "range": "stddev: 0.0019229676189411753",
            "extra": "mean: 20.459786384330634 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.24052980704302,
            "unit": "iter/sec",
            "range": "stddev: 0.006958268823325714",
            "extra": "mean: 51.973620790522546 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 28.607461761827444,
            "unit": "iter/sec",
            "range": "stddev: 0.006545764567896581",
            "extra": "mean: 34.955914940148816 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 43.25184095923053,
            "unit": "iter/sec",
            "range": "stddev: 0.008643249140154038",
            "extra": "mean: 23.12040315099204 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 63.52547479998594,
            "unit": "iter/sec",
            "range": "stddev: 0.0017763924356984395",
            "extra": "mean: 15.741716266561793 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6797.039367280182,
            "unit": "iter/sec",
            "range": "stddev: 0.000017184360640976494",
            "extra": "mean: 147.122878942534 usec\nrounds: 3773"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1529.870045064359,
            "unit": "iter/sec",
            "range": "stddev: 0.00021066665617792607",
            "extra": "mean: 653.650290902932 usec\nrounds: 49"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4653.942634448761,
            "unit": "iter/sec",
            "range": "stddev: 0.000022065423357000186",
            "extra": "mean: 214.87157847583688 usec\nrounds: 940"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 663.9731039341701,
            "unit": "iter/sec",
            "range": "stddev: 0.00013133421691692603",
            "extra": "mean: 1.5060851020542925 msec\nrounds: 481"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 445.89736468285764,
            "unit": "iter/sec",
            "range": "stddev: 0.0004034949383918605",
            "extra": "mean: 2.242668558293107 msec\nrounds: 330"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 66.2163826730074,
            "unit": "iter/sec",
            "range": "stddev: 0.002213342355166167",
            "extra": "mean: 15.10200285234914 msec\nrounds: 81"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 62.4568376303784,
            "unit": "iter/sec",
            "range": "stddev: 0.00186787447944665",
            "extra": "mean: 16.01105720270425 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 24.499567262521623,
            "unit": "iter/sec",
            "range": "stddev: 0.006228409970341875",
            "extra": "mean: 40.81704747208971 msec\nrounds: 21"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 56.85298226919761,
            "unit": "iter/sec",
            "range": "stddev: 0.006526429277438055",
            "extra": "mean: 17.58922681074182 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 63.11414816973932,
            "unit": "iter/sec",
            "range": "stddev: 0.003510362774078815",
            "extra": "mean: 15.844307956285775 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 659.0654987142194,
            "unit": "iter/sec",
            "range": "stddev: 0.00012824929832791536",
            "extra": "mean: 1.5172998767966381 msec\nrounds: 482"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 64.45973816655201,
            "unit": "iter/sec",
            "range": "stddev: 0.0023647971634634933",
            "extra": "mean: 15.51355975750608 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 65.7187178332003,
            "unit": "iter/sec",
            "range": "stddev: 0.0023542477881271164",
            "extra": "mean: 15.216365032228492 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 647.2036751225243,
            "unit": "iter/sec",
            "range": "stddev: 0.0001367233187046291",
            "extra": "mean: 1.5451086550314885 msec\nrounds: 489"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 46.85996224481316,
            "unit": "iter/sec",
            "range": "stddev: 0.002306008685499967",
            "extra": "mean: 21.34017937905377 msec\nrounds: 21"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 21.502176530660627,
            "unit": "iter/sec",
            "range": "stddev: 0.0021727552759816114",
            "extra": "mean: 46.50691982618917 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 20.91140910163924,
            "unit": "iter/sec",
            "range": "stddev: 0.0035904518282311396",
            "extra": "mean: 47.8207850623328 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 21.078792547080337,
            "unit": "iter/sec",
            "range": "stddev: 0.0022663942136707522",
            "extra": "mean: 47.44104757264722 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 20.941527186194815,
            "unit": "iter/sec",
            "range": "stddev: 0.00235355103993567",
            "extra": "mean: 47.752009254569806 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.52299287147176,
            "unit": "iter/sec",
            "range": "stddev: 0.0006544912084327078",
            "extra": "mean: 12.117834862793744 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 83.38147838979435,
            "unit": "iter/sec",
            "range": "stddev: 0.0004447225206859071",
            "extra": "mean: 11.993071114968346 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.1681468701584,
            "unit": "iter/sec",
            "range": "stddev: 0.00036072288000097455",
            "extra": "mean: 12.170166154290833 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.3806790853116,
            "unit": "iter/sec",
            "range": "stddev: 0.0005100280749176195",
            "extra": "mean: 12.923122565227269 msec\nrounds: 67"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 68.6181247707343,
            "unit": "iter/sec",
            "range": "stddev: 0.002249371243247147",
            "extra": "mean: 14.57340904230745 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 581.3500620697398,
            "unit": "iter/sec",
            "range": "stddev: 0.00014477605555281162",
            "extra": "mean: 1.7201339868095487 msec\nrounds: 423"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 60.82325979077222,
            "unit": "iter/sec",
            "range": "stddev: 0.002338566653865768",
            "extra": "mean: 16.441078683384124 msec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 62.34873028438798,
            "unit": "iter/sec",
            "range": "stddev: 0.0018933943680010479",
            "extra": "mean: 16.03881900142557 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 57.908888013648294,
            "unit": "iter/sec",
            "range": "stddev: 0.006698189402070799",
            "extra": "mean: 17.268506343349475 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 62.35995558094469,
            "unit": "iter/sec",
            "range": "stddev: 0.0026275059077541588",
            "extra": "mean: 16.03593188423581 msec\nrounds: 68"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 691.8150930403343,
            "unit": "iter/sec",
            "range": "stddev: 0.00012286191231770146",
            "extra": "mean: 1.4454729450976258 msec\nrounds: 501"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 664.3989073282726,
            "unit": "iter/sec",
            "range": "stddev: 0.000109165036944138",
            "extra": "mean: 1.5051198744761187 msec\nrounds: 573"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 675.4674530290049,
            "unit": "iter/sec",
            "range": "stddev: 0.00011132570701509042",
            "extra": "mean: 1.4804562314819032 msec\nrounds: 457"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 63.42303509814915,
            "unit": "iter/sec",
            "range": "stddev: 0.0021531101385767262",
            "extra": "mean: 15.767141992691903 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 52.9767706936295,
            "unit": "iter/sec",
            "range": "stddev: 0.0025678308745122765",
            "extra": "mean: 18.876197754353697 msec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 68.94793595423741,
            "unit": "iter/sec",
            "range": "stddev: 0.0015421497466369565",
            "extra": "mean: 14.503697408196915 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 55.73735305237439,
            "unit": "iter/sec",
            "range": "stddev: 0.0045450272679308235",
            "extra": "mean: 17.941289731866814 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 64.58278642745786,
            "unit": "iter/sec",
            "range": "stddev: 0.0021025049909798423",
            "extra": "mean: 15.484002089678224 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 646.96113580861,
            "unit": "iter/sec",
            "range": "stddev: 0.00012172848684930844",
            "extra": "mean: 1.5456879009434488 msec\nrounds: 448"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 733.0918264825881,
            "unit": "iter/sec",
            "range": "stddev: 0.00012206285321680036",
            "extra": "mean: 1.3640855945673966 msec\nrounds: 582"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 267.9289999276413,
            "unit": "iter/sec",
            "range": "stddev: 0.0021757900480755365",
            "extra": "mean: 3.732332074057182 msec\nrounds: 231"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 679.4548444694464,
            "unit": "iter/sec",
            "range": "stddev: 0.00012436443194414854",
            "extra": "mean: 1.4717681508045644 msec\nrounds: 510"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 742.0392235889182,
            "unit": "iter/sec",
            "range": "stddev: 0.00010655290554707476",
            "extra": "mean: 1.3476376560843224 msec\nrounds: 385"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 87.69193007729776,
            "unit": "iter/sec",
            "range": "stddev: 0.0031929993773590418",
            "extra": "mean: 11.40355787720182 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 101.94644268311136,
            "unit": "iter/sec",
            "range": "stddev: 0.0005358998628210024",
            "extra": "mean: 9.809072035091832 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 119.1299019521717,
            "unit": "iter/sec",
            "range": "stddev: 0.0006913682873824561",
            "extra": "mean: 8.3941981283715 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 133.49154007661255,
            "unit": "iter/sec",
            "range": "stddev: 0.00027422638228755147",
            "extra": "mean: 7.4911114174432845 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 116.14691327070577,
            "unit": "iter/sec",
            "range": "stddev: 0.0004134110066384458",
            "extra": "mean: 8.609785416072844 msec\nrounds: 113"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 116.9111002109438,
            "unit": "iter/sec",
            "range": "stddev: 0.0004947844014041897",
            "extra": "mean: 8.553507735327873 msec\nrounds: 117"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 119.24296268202205,
            "unit": "iter/sec",
            "range": "stddev: 0.0005020157730263375",
            "extra": "mean: 8.38623913317752 msec\nrounds: 134"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 124.4062441564054,
            "unit": "iter/sec",
            "range": "stddev: 0.000641115302984507",
            "extra": "mean: 8.038181739035421 msec\nrounds: 130"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 252.46646932968432,
            "unit": "iter/sec",
            "range": "stddev: 0.0003783041010759533",
            "extra": "mean: 3.960922029190918 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 7000.132245239882,
            "unit": "iter/sec",
            "range": "stddev: 0.000012495129948805498",
            "extra": "mean: 142.8544440256831 usec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7250.560273308598,
            "unit": "iter/sec",
            "range": "stddev: 0.000020453105676983334",
            "extra": "mean: 137.9203761233857 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 45.26918976063463,
            "unit": "iter/sec",
            "range": "stddev: 0.003154389415972564",
            "extra": "mean: 22.090079484249664 msec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 85.37001129918966,
            "unit": "iter/sec",
            "range": "stddev: 0.0027307743835373287",
            "extra": "mean: 11.713715211953968 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 668.5939342879217,
            "unit": "iter/sec",
            "range": "stddev: 0.00012728036718962895",
            "extra": "mean: 1.4956761476830305 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 675.8462623057471,
            "unit": "iter/sec",
            "range": "stddev: 0.00018496985090235096",
            "extra": "mean: 1.4796264413571745 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 52.00566138303892,
            "unit": "iter/sec",
            "range": "stddev: 0.018804981328384502",
            "extra": "mean: 19.228675751946867 msec\nrounds: 28"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "36cff210c164dc758ae7b8c66d634b7a0c87e674",
          "message": "Merge pull request #134 from disnana/copilot/improve-documentation-structure\n\ndocs: restructure into finer categories, add missing EN/JP pages for encryption, cache, v2, exceptions",
          "timestamp": "2026-03-12T22:56:38+09:00",
          "tree_id": "f2dbfad96fc7319430318cf7782319ff4d000ff1",
          "url": "https://github.com/disnana/NanaSQLite/commit/36cff210c164dc758ae7b8c66d634b7a0c87e674"
        },
        "date": 1773324110408,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4259.716913578273,
            "unit": "iter/sec",
            "range": "stddev: 0.004147659491585832",
            "extra": "mean: 234.75738418494433 usec\nrounds: 5084"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 3913.217206127261,
            "unit": "iter/sec",
            "range": "stddev: 0.004532322869423138",
            "extra": "mean: 255.5442101282326 usec\nrounds: 7654"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 676.470108156918,
            "unit": "iter/sec",
            "range": "stddev: 0.010588381852864292",
            "extra": "mean: 1.4782619186597292 msec\nrounds: 1962"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2467980.9059796217,
            "unit": "iter/sec",
            "range": "stddev: 2.567325648989857e-8",
            "extra": "mean: 405.1895205416489 nsec\nrounds: 58442"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 88262.4532106308,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016590080378959277",
            "extra": "mean: 11.329845972143847 usec\nrounds: 7266"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 483.7659457165488,
            "unit": "iter/sec",
            "range": "stddev: 0.00017352895159287814",
            "extra": "mean: 2.067115324785441 msec\nrounds: 288"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2769.291624717713,
            "unit": "iter/sec",
            "range": "stddev: 0.000017554825721842997",
            "extra": "mean: 361.10317565486974 usec\nrounds: 1489"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2250462.434761203,
            "unit": "iter/sec",
            "range": "stddev: 1.0854400704122633e-7",
            "extra": "mean: 444.3531180764234 nsec\nrounds: 141364"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 116686.72487840921,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010846506663459176",
            "extra": "mean: 8.569955160212334 usec\nrounds: 9165"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 81311.94662731905,
            "unit": "iter/sec",
            "range": "stddev: 6.385775724781524e-7",
            "extra": "mean: 12.298315825389693 usec\nrounds: 361"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 72741.45928146591,
            "unit": "iter/sec",
            "range": "stddev: 0.000001618495656778844",
            "extra": "mean: 13.74731837768883 usec\nrounds: 15469"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5796677.481094616,
            "unit": "iter/sec",
            "range": "stddev: 1.496855265920789e-8",
            "extra": "mean: 172.51261662594774 nsec\nrounds: 138103"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1391865.2657190836,
            "unit": "iter/sec",
            "range": "stddev: 1.5488662117807126e-7",
            "extra": "mean: 718.460345716988 nsec\nrounds: 3324"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 84611.36792685794,
            "unit": "iter/sec",
            "range": "stddev: 7.820710441192489e-7",
            "extra": "mean: 11.818742853376948 usec\nrounds: 342"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 69195.35388428971,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014278773987441793",
            "extra": "mean: 14.451837354170141 usec\nrounds: 14548"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3349.340760479765,
            "unit": "iter/sec",
            "range": "stddev: 0.005326411422065095",
            "extra": "mean: 298.56621691032666 usec\nrounds: 7721"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4788.285227700297,
            "unit": "iter/sec",
            "range": "stddev: 0.0037443736516533915",
            "extra": "mean: 208.84303094873843 usec\nrounds: 6748"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 50932.71050318732,
            "unit": "iter/sec",
            "range": "stddev: 0.000003566225408022605",
            "extra": "mean: 19.6337479415595 usec\nrounds: 8602"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9314.946399863762,
            "unit": "iter/sec",
            "range": "stddev: 0.0024857271684467297",
            "extra": "mean: 107.35434827779854 usec\nrounds: 11897"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7352.904912459509,
            "unit": "iter/sec",
            "range": "stddev: 0.000016279864197177416",
            "extra": "mean: 136.00067074245698 usec\nrounds: 960"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12412.567167644804,
            "unit": "iter/sec",
            "range": "stddev: 0.000006505209737093865",
            "extra": "mean: 80.56351168085908 usec\nrounds: 3534"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21934.91729043504,
            "unit": "iter/sec",
            "range": "stddev: 0.000003923861527970043",
            "extra": "mean: 45.589412841600314 usec\nrounds: 5390"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8182.63200478758,
            "unit": "iter/sec",
            "range": "stddev: 0.000007779516282616474",
            "extra": "mean: 122.21006632278093 usec\nrounds: 3844"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8321.08355750849,
            "unit": "iter/sec",
            "range": "stddev: 0.0026164750838978757",
            "extra": "mean: 120.17665645211011 usec\nrounds: 7567"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2128.7959834131134,
            "unit": "iter/sec",
            "range": "stddev: 0.005114734996459501",
            "extra": "mean: 469.74910127211587 usec\nrounds: 4434"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2093.9701140248912,
            "unit": "iter/sec",
            "range": "stddev: 0.0052427368285098775",
            "extra": "mean: 477.561734669587 usec\nrounds: 2847"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2087.421468945967,
            "unit": "iter/sec",
            "range": "stddev: 0.005262137759919822",
            "extra": "mean: 479.05993824282416 usec\nrounds: 4139"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 432.05891216205214,
            "unit": "iter/sec",
            "range": "stddev: 0.007624341280251696",
            "extra": "mean: 2.3144991848355403 msec\nrounds: 1221"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 285.8050623274062,
            "unit": "iter/sec",
            "range": "stddev: 0.09207502232929907",
            "extra": "mean: 3.4988883396839285 msec\nrounds: 1063"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15255.009579532838,
            "unit": "iter/sec",
            "range": "stddev: 0.0000068709772046563386",
            "extra": "mean: 65.55223677746281 usec\nrounds: 2211"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28370.0110055745,
            "unit": "iter/sec",
            "range": "stddev: 0.000003257913688217766",
            "extra": "mean: 35.24848826472106 usec\nrounds: 6743"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2286.2156492978106,
            "unit": "iter/sec",
            "range": "stddev: 0.00003079680860351705",
            "extra": "mean: 437.40405692137597 usec\nrounds: 1091"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 112315.3075668676,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016469440772371042",
            "extra": "mean: 8.90350586810835 usec\nrounds: 17899"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44282.77944931623,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028752668911380766",
            "extra": "mean: 22.582141691095703 usec\nrounds: 11926"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 56727.33465541825,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027601205816208553",
            "extra": "mean: 17.62818588383098 usec\nrounds: 15531"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70518.28876772137,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021753826877222772",
            "extra": "mean: 14.1807184699827 usec\nrounds: 13727"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 96584.47481348626,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019195865177048605",
            "extra": "mean: 10.353630870086464 usec\nrounds: 14126"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1259.2574528281436,
            "unit": "iter/sec",
            "range": "stddev: 0.005263342322482483",
            "extra": "mean: 794.1187862371734 usec\nrounds: 287"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 897.4019578895412,
            "unit": "iter/sec",
            "range": "stddev: 0.00810963889383192",
            "extra": "mean: 1.114327856328443 msec\nrounds: 2103"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 243919.0584453619,
            "unit": "iter/sec",
            "range": "stddev: 5.843561077039115e-7",
            "extra": "mean: 4.099720646568504 usec\nrounds: 22196"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4457.731124666981,
            "unit": "iter/sec",
            "range": "stddev: 0.00409784744310506",
            "extra": "mean: 224.32936667410738 usec\nrounds: 12950"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 155464.83657091405,
            "unit": "iter/sec",
            "range": "stddev: 9.184343890111558e-7",
            "extra": "mean: 6.432322717194366 usec\nrounds: 23097"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 1765.1116361673733,
            "unit": "iter/sec",
            "range": "stddev: 0.03057546902803354",
            "extra": "mean: 566.5364045592735 usec\nrounds: 14370"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2497.2053502776944,
            "unit": "iter/sec",
            "range": "stddev: 0.004884280334811165",
            "extra": "mean: 400.44764435924264 usec\nrounds: 2825"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1441.6390876552325,
            "unit": "iter/sec",
            "range": "stddev: 0.01023081010947101",
            "extra": "mean: 693.6548880805246 usec\nrounds: 2135"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3702.5662554422674,
            "unit": "iter/sec",
            "range": "stddev: 0.004466180333111202",
            "extra": "mean: 270.08294545172186 usec\nrounds: 4645"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 352921.620084999,
            "unit": "iter/sec",
            "range": "stddev: 4.2387959335118676e-7",
            "extra": "mean: 2.8334903363504793 usec\nrounds: 48300"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8042.913866789333,
            "unit": "iter/sec",
            "range": "stddev: 0.0027474762185808205",
            "extra": "mean: 124.33304851481545 usec\nrounds: 9333"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37224.94435538364,
            "unit": "iter/sec",
            "range": "stddev: 0.00000222083874845695",
            "extra": "mean: 26.86370704689517 usec\nrounds: 10318"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 7776.557838684384,
            "unit": "iter/sec",
            "range": "stddev: 0.0029354056528008107",
            "extra": "mean: 128.59159807511665 usec\nrounds: 7597"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4010.455005595911,
            "unit": "iter/sec",
            "range": "stddev: 0.004478829656954558",
            "extra": "mean: 249.3482656218981 usec\nrounds: 4714"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 3135.5567404894955,
            "unit": "iter/sec",
            "range": "stddev: 0.005841824715215768",
            "extra": "mean: 318.92262930119665 usec\nrounds: 5116"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 1814.9829517125145,
            "unit": "iter/sec",
            "range": "stddev: 0.014965673151735335",
            "extra": "mean: 550.9693625807652 usec\nrounds: 4692"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 2075.454866187422,
            "unit": "iter/sec",
            "range": "stddev: 0.00885625416597104",
            "extra": "mean: 481.82208936057685 usec\nrounds: 1163"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1199603.6190141158,
            "unit": "iter/sec",
            "range": "stddev: 1.3831549087921618e-7",
            "extra": "mean: 833.6086888616104 nsec\nrounds: 95238"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1204859.3355612447,
            "unit": "iter/sec",
            "range": "stddev: 1.4562878165260706e-7",
            "extra": "mean: 829.972404649363 nsec\nrounds: 128883"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1210601.0257556117,
            "unit": "iter/sec",
            "range": "stddev: 1.636677718439563e-7",
            "extra": "mean: 826.0359761184222 nsec\nrounds: 129182"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1213546.3075949084,
            "unit": "iter/sec",
            "range": "stddev: 1.72713770064785e-7",
            "extra": "mean: 824.0311834345 nsec\nrounds: 175903"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 82782.15604397719,
            "unit": "iter/sec",
            "range": "stddev: 0.000002644675239802665",
            "extra": "mean: 12.079897985125685 usec\nrounds: 10411"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 52174.76746998793,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029975125389933143",
            "extra": "mean: 19.166352788734937 usec\nrounds: 8025"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 37633.22537805519,
            "unit": "iter/sec",
            "range": "stddev: 0.000004596401405250547",
            "extra": "mean: 26.57226400220065 usec\nrounds: 154"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17060.024378812755,
            "unit": "iter/sec",
            "range": "stddev: 0.00000966713344079102",
            "extra": "mean: 58.61656336446526 usec\nrounds: 3986"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 38.31537322894047,
            "unit": "iter/sec",
            "range": "stddev: 0.05671688134193791",
            "extra": "mean: 26.099184628186716 msec\nrounds: 183"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 49.303295295605466,
            "unit": "iter/sec",
            "range": "stddev: 0.03337198772713456",
            "extra": "mean: 20.28261993451648 msec\nrounds: 185"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 42.979600113291625,
            "unit": "iter/sec",
            "range": "stddev: 0.03692027290711238",
            "extra": "mean: 23.26685211970471 msec\nrounds: 200"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 44.10258808397756,
            "unit": "iter/sec",
            "range": "stddev: 0.03673514138242984",
            "extra": "mean: 22.674406275111537 msec\nrounds: 179"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21354.95702318346,
            "unit": "iter/sec",
            "range": "stddev: 0.000004016780079648927",
            "extra": "mean: 46.82753512050508 usec\nrounds: 12745"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 16881.115872191036,
            "unit": "iter/sec",
            "range": "stddev: 0.000002903249038448088",
            "extra": "mean: 59.23779017756412 usec\nrounds: 9607"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21709.34786703161,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019873686150041005",
            "extra": "mean: 46.06310636896774 usec\nrounds: 11502"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4230.816087990736,
            "unit": "iter/sec",
            "range": "stddev: 0.000011488832164650245",
            "extra": "mean: 236.36101858422109 usec\nrounds: 2319"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 3821.4049246675213,
            "unit": "iter/sec",
            "range": "stddev: 0.004856211817592629",
            "extra": "mean: 261.6838622740311 usec\nrounds: 15841"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 416640.75069196586,
            "unit": "iter/sec",
            "range": "stddev: 3.6874120516986376e-7",
            "extra": "mean: 2.4001492852995745 usec\nrounds: 71619"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 3841.2680330030894,
            "unit": "iter/sec",
            "range": "stddev: 0.004437496916722969",
            "extra": "mean: 260.33070106232697 usec\nrounds: 5640"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4115.322175348852,
            "unit": "iter/sec",
            "range": "stddev: 0.00002538439251861034",
            "extra": "mean: 242.99434099961584 usec\nrounds: 1090"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3619.9843155227363,
            "unit": "iter/sec",
            "range": "stddev: 0.000020811762107866934",
            "extra": "mean: 276.2442908141708 usec\nrounds: 1258"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5043.517525878588,
            "unit": "iter/sec",
            "range": "stddev: 0.00001729744545838911",
            "extra": "mean: 198.2743184432176 usec\nrounds: 2749"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5072.54609698268,
            "unit": "iter/sec",
            "range": "stddev: 0.000014309807071409935",
            "extra": "mean: 197.1396574581813 usec\nrounds: 2815"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21730.084841201577,
            "unit": "iter/sec",
            "range": "stddev: 0.000004718737788215039",
            "extra": "mean: 46.01914844363325 usec\nrounds: 12234"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21700.017560831875,
            "unit": "iter/sec",
            "range": "stddev: 0.00000430173294489826",
            "extra": "mean: 46.082912015932244 usec\nrounds: 11651"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21248.709629158213,
            "unit": "iter/sec",
            "range": "stddev: 0.00000870149618784446",
            "extra": "mean: 47.06168127158957 usec\nrounds: 12938"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21555.73010475082,
            "unit": "iter/sec",
            "range": "stddev: 0.000003886337876863575",
            "extra": "mean: 46.39137691650736 usec\nrounds: 14111"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 211.4582941639296,
            "unit": "iter/sec",
            "range": "stddev: 0.010965908286183114",
            "extra": "mean: 4.729064915395403 msec\nrounds: 197"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3767.351956813751,
            "unit": "iter/sec",
            "range": "stddev: 0.0037499914641773383",
            "extra": "mean: 265.43843300633716 usec\nrounds: 3309"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 217692.7189641138,
            "unit": "iter/sec",
            "range": "stddev: 0.00002235852334724753",
            "extra": "mean: 4.593630897526012 usec\nrounds: 33709"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 900433.4699446775,
            "unit": "iter/sec",
            "range": "stddev: 9.302712612351562e-7",
            "extra": "mean: 1.110576220652304 usec\nrounds: 64671"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 53.65432167931743,
            "unit": "iter/sec",
            "range": "stddev: 0.0037988903210405696",
            "extra": "mean: 18.63782764745078 msec\nrounds: 56"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 109.80796638134481,
            "unit": "iter/sec",
            "range": "stddev: 0.0021171669771782153",
            "extra": "mean: 9.106807392527116 msec\nrounds: 48"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 155670.29013452484,
            "unit": "iter/sec",
            "range": "stddev: 7.874721959726391e-7",
            "extra": "mean: 6.423833341197186 usec\nrounds: 22999"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 123469.79166141688,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027843476660075065",
            "extra": "mean: 8.09914705891976 usec\nrounds: 4422"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 69959.04067937806,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023374947907203956",
            "extra": "mean: 14.294078224757184 usec\nrounds: 12515"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82163.3464074599,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019737079679475546",
            "extra": "mean: 12.170877206496137 usec\nrounds: 13787"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2527.221335823682,
            "unit": "iter/sec",
            "range": "stddev: 0.004594140005227722",
            "extra": "mean: 395.6914995235572 usec\nrounds: 2281"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 769.5370921203353,
            "unit": "iter/sec",
            "range": "stddev: 0.009646537071006793",
            "extra": "mean: 1.2994825203872387 msec\nrounds: 1581"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4427.500000009429,
            "unit": "iter/sec",
            "range": "stddev: 0.00003302456398562167",
            "extra": "mean: 225.86109542583185 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4655.823024140575,
            "unit": "iter/sec",
            "range": "stddev: 0.000031476432658936416",
            "extra": "mean: 214.78479633245755 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1394.7479004408704,
            "unit": "iter/sec",
            "range": "stddev: 0.0002922699967476281",
            "extra": "mean: 716.9754474510461 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 191.11054914021824,
            "unit": "iter/sec",
            "range": "stddev: 0.005269922016539899",
            "extra": "mean: 5.232573526154738 msec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10324.932717734353,
            "unit": "iter/sec",
            "range": "stddev: 0.000011890516724088545",
            "extra": "mean: 96.85293137865935 usec\nrounds: 3523"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7476.576638963132,
            "unit": "iter/sec",
            "range": "stddev: 0.00001702348636320942",
            "extra": "mean: 133.75105322784228 usec\nrounds: 3271"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 290.4348634079534,
            "unit": "iter/sec",
            "range": "stddev: 0.00032849183383254623",
            "extra": "mean: 3.4431128145775336 msec\nrounds: 204"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7342.759719303866,
            "unit": "iter/sec",
            "range": "stddev: 0.0000175612979553993",
            "extra": "mean: 136.18857735069744 usec\nrounds: 2537"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1587.702683867024,
            "unit": "iter/sec",
            "range": "stddev: 0.00005621814932946321",
            "extra": "mean: 629.8408449901907 usec\nrounds: 1035"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6645.402903188054,
            "unit": "iter/sec",
            "range": "stddev: 0.000037833000648657555",
            "extra": "mean: 150.47996555938872 usec\nrounds: 333"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 10215.777237459277,
            "unit": "iter/sec",
            "range": "stddev: 0.000010736438590314425",
            "extra": "mean: 97.88780400704057 usec\nrounds: 4151"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8376.851017934865,
            "unit": "iter/sec",
            "range": "stddev: 0.000015496119975236945",
            "extra": "mean: 119.3766008084657 usec\nrounds: 2721"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6776.300463608189,
            "unit": "iter/sec",
            "range": "stddev: 0.000023097910879026573",
            "extra": "mean: 147.5731492973864 usec\nrounds: 275"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2580.534680042178,
            "unit": "iter/sec",
            "range": "stddev: 0.00010464205941348041",
            "extra": "mean: 387.5165901601661 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 5272.482250244566,
            "unit": "iter/sec",
            "range": "stddev: 0.00001358057613234834",
            "extra": "mean: 189.66398605772733 usec\nrounds: 49"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7783.667022083542,
            "unit": "iter/sec",
            "range": "stddev: 0.000011497773265246023",
            "extra": "mean: 128.47414941605746 usec\nrounds: 3404"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1176.4070786312466,
            "unit": "iter/sec",
            "range": "stddev: 0.0001329093332201452",
            "extra": "mean: 850.0458881661126 usec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 269.84245384148807,
            "unit": "iter/sec",
            "range": "stddev: 0.0002172414125481583",
            "extra": "mean: 3.705866092469734 msec\nrounds: 195"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.44298015693109,
            "unit": "iter/sec",
            "range": "stddev: 0.004829964194507658",
            "extra": "mean: 17.1106948570179 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 46.24534457158024,
            "unit": "iter/sec",
            "range": "stddev: 0.00468245938944123",
            "extra": "mean: 21.623798227995973 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.06885269570211,
            "unit": "iter/sec",
            "range": "stddev: 0.004808072526000005",
            "extra": "mean: 52.44153992680367 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.41436892319331,
            "unit": "iter/sec",
            "range": "stddev: 0.006394236860362976",
            "extra": "mean: 33.99698979132261 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 48.04781515992713,
            "unit": "iter/sec",
            "range": "stddev: 0.0022675052519072706",
            "extra": "mean: 20.8126008783438 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 66.5736868862547,
            "unit": "iter/sec",
            "range": "stddev: 0.0020723541226375817",
            "extra": "mean: 15.02094966902708 msec\nrounds: 63"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6667.964035404792,
            "unit": "iter/sec",
            "range": "stddev: 0.000019542169615716475",
            "extra": "mean: 149.97081488297096 usec\nrounds: 3811"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1603.8423836671595,
            "unit": "iter/sec",
            "range": "stddev: 0.00006228484408696591",
            "extra": "mean: 623.5026647154169 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4603.460150060506,
            "unit": "iter/sec",
            "range": "stddev: 0.000022792955327938974",
            "extra": "mean: 217.22790409880193 usec\nrounds: 940"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 656.7062859238162,
            "unit": "iter/sec",
            "range": "stddev: 0.00012866704197915936",
            "extra": "mean: 1.5227507661103903 msec\nrounds: 521"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 453.3898351182185,
            "unit": "iter/sec",
            "range": "stddev: 0.00019083111987476553",
            "extra": "mean: 2.2056074542104733 msec\nrounds: 318"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 66.39266451041482,
            "unit": "iter/sec",
            "range": "stddev: 0.0020802274759786498",
            "extra": "mean: 15.061904916365165 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 61.61210302104351,
            "unit": "iter/sec",
            "range": "stddev: 0.001987061433821608",
            "extra": "mean: 16.230577288661152 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.06306719032568,
            "unit": "iter/sec",
            "range": "stddev: 0.00554259916001473",
            "extra": "mean: 31.18853209095753 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 64.80151330727234,
            "unit": "iter/sec",
            "range": "stddev: 0.001981155029521853",
            "extra": "mean: 15.43173838021735 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 62.422185676721284,
            "unit": "iter/sec",
            "range": "stddev: 0.002645350624745603",
            "extra": "mean: 16.019945299238756 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 655.3579916000414,
            "unit": "iter/sec",
            "range": "stddev: 0.00012497134253223655",
            "extra": "mean: 1.5258835824348813 msec\nrounds: 458"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 59.67848763902738,
            "unit": "iter/sec",
            "range": "stddev: 0.008532408426745113",
            "extra": "mean: 16.75645679978725 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 27.992828378491414,
            "unit": "iter/sec",
            "range": "stddev: 0.062066428606469",
            "extra": "mean: 35.72343553423707 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 628.9287397621346,
            "unit": "iter/sec",
            "range": "stddev: 0.00017549568286140068",
            "extra": "mean: 1.5900052530247026 msec\nrounds: 430"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 13.308696121412497,
            "unit": "iter/sec",
            "range": "stddev: 0.010554407646369359",
            "extra": "mean: 75.13884086594251 msec\nrounds: 7"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 4.292999024206086,
            "unit": "iter/sec",
            "range": "stddev: 0.27284547851321345",
            "extra": "mean: 232.9373928019777 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 16.25177018149721,
            "unit": "iter/sec",
            "range": "stddev: 0.022781462446820562",
            "extra": "mean: 61.53175862273201 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 21.202003237010718,
            "unit": "iter/sec",
            "range": "stddev: 0.004027741683049805",
            "extra": "mean: 47.16535455736448 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 21.388846714074003,
            "unit": "iter/sec",
            "range": "stddev: 0.002115358368723051",
            "extra": "mean: 46.753338941925904 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 83.41147971719441,
            "unit": "iter/sec",
            "range": "stddev: 0.0003924691541824088",
            "extra": "mean: 11.988757463486893 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 82.06054743617572,
            "unit": "iter/sec",
            "range": "stddev: 0.00043896427134664044",
            "extra": "mean: 12.18612391999664 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.58665242241287,
            "unit": "iter/sec",
            "range": "stddev: 0.0005266786475924327",
            "extra": "mean: 12.108494177548405 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 76.0789161290134,
            "unit": "iter/sec",
            "range": "stddev: 0.0010773305408374588",
            "extra": "mean: 13.144246144414259 msec\nrounds: 60"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 66.47071506038914,
            "unit": "iter/sec",
            "range": "stddev: 0.0019553771178753344",
            "extra": "mean: 15.044219083418804 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 566.9844080150928,
            "unit": "iter/sec",
            "range": "stddev: 0.00014224275545127933",
            "extra": "mean: 1.7637169309484444 msec\nrounds: 423"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 57.86815463098775,
            "unit": "iter/sec",
            "range": "stddev: 0.005994776229445649",
            "extra": "mean: 17.28066164156738 msec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 62.230852864983774,
            "unit": "iter/sec",
            "range": "stddev: 0.0019864029056571512",
            "extra": "mean: 16.069199664828677 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 58.87885664203756,
            "unit": "iter/sec",
            "range": "stddev: 0.003784225896328173",
            "extra": "mean: 16.984025455515265 msec\nrounds: 46"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 63.02839038865673,
            "unit": "iter/sec",
            "range": "stddev: 0.0020364847816520767",
            "extra": "mean: 15.865866061843311 msec\nrounds: 60"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 681.2512777167318,
            "unit": "iter/sec",
            "range": "stddev: 0.00015710257269717807",
            "extra": "mean: 1.4678871551648023 msec\nrounds: 499"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 657.3639200359986,
            "unit": "iter/sec",
            "range": "stddev: 0.00013594695672447933",
            "extra": "mean: 1.5212273894576356 msec\nrounds: 460"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 669.0644574021397,
            "unit": "iter/sec",
            "range": "stddev: 0.0001664140527055695",
            "extra": "mean: 1.494624305530778 msec\nrounds: 456"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 62.31260084390928,
            "unit": "iter/sec",
            "range": "stddev: 0.0018737602507346517",
            "extra": "mean: 16.04811846170508 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 53.24736419385685,
            "unit": "iter/sec",
            "range": "stddev: 0.0017569456434027575",
            "extra": "mean: 18.78027232220013 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 58.252158094969595,
            "unit": "iter/sec",
            "range": "stddev: 0.010476952792942683",
            "extra": "mean: 17.166745966212634 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 53.98384802576621,
            "unit": "iter/sec",
            "range": "stddev: 0.0066309927288759184",
            "extra": "mean: 18.52405926162776 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 66.46762757759882,
            "unit": "iter/sec",
            "range": "stddev: 0.002068975785717471",
            "extra": "mean: 15.044917901312667 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 642.9717672596997,
            "unit": "iter/sec",
            "range": "stddev: 0.00012097115890994047",
            "extra": "mean: 1.5552782422499347 msec\nrounds: 438"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 630.0764795923078,
            "unit": "iter/sec",
            "range": "stddev: 0.00035599618508329556",
            "extra": "mean: 1.587108918344408 msec\nrounds: 480"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 262.09644911672126,
            "unit": "iter/sec",
            "range": "stddev: 0.0027168689731882495",
            "extra": "mean: 3.8153893475857923 msec\nrounds: 147"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 652.9206567926951,
            "unit": "iter/sec",
            "range": "stddev: 0.0001350515449254589",
            "extra": "mean: 1.5315796637714647 msec\nrounds: 555"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 718.8794876130988,
            "unit": "iter/sec",
            "range": "stddev: 0.00011243010383820287",
            "extra": "mean: 1.3910537402038106 msec\nrounds: 520"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 88.36252852659835,
            "unit": "iter/sec",
            "range": "stddev: 0.003105425731542928",
            "extra": "mean: 11.317014312226092 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 100.32018082026525,
            "unit": "iter/sec",
            "range": "stddev: 0.0005343861621980601",
            "extra": "mean: 9.96808410654294 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 130.5519386627111,
            "unit": "iter/sec",
            "range": "stddev: 0.00042591878197021006",
            "extra": "mean: 7.6597866737433975 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 115.79083633324055,
            "unit": "iter/sec",
            "range": "stddev: 0.0007284505912058296",
            "extra": "mean: 8.636262001960564 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 115.7873983192296,
            "unit": "iter/sec",
            "range": "stddev: 0.000558044147760237",
            "extra": "mean: 8.636518433922902 msec\nrounds: 110"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 115.97062209317208,
            "unit": "iter/sec",
            "range": "stddev: 0.0004483510330351331",
            "extra": "mean: 8.622873465286656 msec\nrounds: 105"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 115.81348060111151,
            "unit": "iter/sec",
            "range": "stddev: 0.0005683077830871344",
            "extra": "mean: 8.634573408981915 msec\nrounds: 131"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 120.65075174987814,
            "unit": "iter/sec",
            "range": "stddev: 0.0006365637435370658",
            "extra": "mean: 8.288385985966391 msec\nrounds: 137"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 255.7169356889225,
            "unit": "iter/sec",
            "range": "stddev: 0.0002732235561757131",
            "extra": "mean: 3.9105739997467026 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 7143.940127020359,
            "unit": "iter/sec",
            "range": "stddev: 0.000008659113683921583",
            "extra": "mean: 139.9787767282264 usec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7273.338201010509,
            "unit": "iter/sec",
            "range": "stddev: 0.000011172896783775697",
            "extra": "mean: 137.48845060732455 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 45.695883098550524,
            "unit": "iter/sec",
            "range": "stddev: 0.0032992937257042133",
            "extra": "mean: 21.88380948549214 msec\nrounds: 48"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 90.53423312918765,
            "unit": "iter/sec",
            "range": "stddev: 0.0019132382071681635",
            "extra": "mean: 11.045545595698059 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 677.4053229149126,
            "unit": "iter/sec",
            "range": "stddev: 0.00018495860620453057",
            "extra": "mean: 1.4762210543267429 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 662.6768962072709,
            "unit": "iter/sec",
            "range": "stddev: 0.0002422621813126932",
            "extra": "mean: 1.5090310311455641 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 67.34979478591829,
            "unit": "iter/sec",
            "range": "stddev: 0.002128375588961569",
            "extra": "mean: 14.847855189145776 msec\nrounds: 32"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "support@disnana.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "support@disnana.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "distinct": true,
          "id": "d6ed46646b71987c22948956a272e27a4721ff1c",
          "message": "no message",
          "timestamp": "2026-03-13T01:55:03+09:00",
          "tree_id": "c7dd9881c4e7551f0135763865d551c8538f9c09",
          "url": "https://github.com/disnana/NanaSQLite/commit/d6ed46646b71987c22948956a272e27a4721ff1c"
        },
        "date": 1773335446240,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 3742.8921751954626,
            "unit": "iter/sec",
            "range": "stddev: 0.0049924289841298325",
            "extra": "mean: 267.1730718365612 usec\nrounds: 5127"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4371.3621186896935,
            "unit": "iter/sec",
            "range": "stddev: 0.004013679091354036",
            "extra": "mean: 228.76164747928684 usec\nrounds: 6876"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 729.5205954694205,
            "unit": "iter/sec",
            "range": "stddev: 0.009571421119947817",
            "extra": "mean: 1.3707632193119037 msec\nrounds: 1743"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2196764.4447445637,
            "unit": "iter/sec",
            "range": "stddev: 6.549196296639358e-8",
            "extra": "mean: 455.2149423177133 nsec\nrounds: 121081"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 88184.0095514737,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018916467774053235",
            "extra": "mean: 11.339924381826753 usec\nrounds: 9096"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 490.6059874338363,
            "unit": "iter/sec",
            "range": "stddev: 0.00020458250107421958",
            "extra": "mean: 2.0382955479826084 msec\nrounds: 322"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2791.802514220175,
            "unit": "iter/sec",
            "range": "stddev: 0.000017414417265871957",
            "extra": "mean: 358.19152497587265 usec\nrounds: 1587"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2244922.522429108,
            "unit": "iter/sec",
            "range": "stddev: 8.614244172566807e-8",
            "extra": "mean: 445.4496714291746 nsec\nrounds: 137401"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 117438.02699217382,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014746058947892848",
            "extra": "mean: 8.515129431343741 usec\nrounds: 9449"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 88724.57120770673,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018150035177890092",
            "extra": "mean: 11.270834971509434 usec\nrounds: 321"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 73461.21467649641,
            "unit": "iter/sec",
            "range": "stddev: 0.000001186532817552408",
            "extra": "mean: 13.612625443286408 usec\nrounds: 18349"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5820230.361470748,
            "unit": "iter/sec",
            "range": "stddev: 1.5630957553911878e-8",
            "extra": "mean: 171.8145052505606 nsec\nrounds: 135337"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1397548.969892245,
            "unit": "iter/sec",
            "range": "stddev: 2.1060232459623192e-7",
            "extra": "mean: 715.5384330304382 nsec\nrounds: 3363"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 79438.32485332263,
            "unit": "iter/sec",
            "range": "stddev: 7.424071976418906e-7",
            "extra": "mean: 12.588382268211607 usec\nrounds: 330"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70653.64327669465,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012352413376502714",
            "extra": "mean: 14.153551800347902 usec\nrounds: 9987"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3715.37140642639,
            "unit": "iter/sec",
            "range": "stddev: 0.004699696604083508",
            "extra": "mean: 269.15209560754107 usec\nrounds: 8218"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4827.044739357392,
            "unit": "iter/sec",
            "range": "stddev: 0.003761902598141769",
            "extra": "mean: 207.16609312660455 usec\nrounds: 8888"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51187.466617766375,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029672021675814755",
            "extra": "mean: 19.53603227655958 usec\nrounds: 9046"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9862.897586044686,
            "unit": "iter/sec",
            "range": "stddev: 0.002302008353398556",
            "extra": "mean: 101.39008250627386 usec\nrounds: 9881"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7425.40024542532,
            "unit": "iter/sec",
            "range": "stddev: 0.000016273112764434897",
            "extra": "mean: 134.67287512428513 usec\nrounds: 1047"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12441.914505720106,
            "unit": "iter/sec",
            "range": "stddev: 0.000007259602269541056",
            "extra": "mean: 80.37348267746536 usec\nrounds: 3658"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21882.443298961596,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036390058407605558",
            "extra": "mean: 45.69873602951156 usec\nrounds: 5553"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8343.526470377343,
            "unit": "iter/sec",
            "range": "stddev: 0.000007828330715277567",
            "extra": "mean: 119.8533981465003 usec\nrounds: 4029"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 8387.572109402281,
            "unit": "iter/sec",
            "range": "stddev: 0.002625144427647544",
            "extra": "mean: 119.22401225964096 usec\nrounds: 7661"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2251.784491754539,
            "unit": "iter/sec",
            "range": "stddev: 0.004711075163346481",
            "extra": "mean: 444.0922315886557 usec\nrounds: 3682"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2269.4258130346775,
            "unit": "iter/sec",
            "range": "stddev: 0.004871001260958879",
            "extra": "mean: 440.6400924217917 usec\nrounds: 2496"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2163.484766679828,
            "unit": "iter/sec",
            "range": "stddev: 0.0050387173217083005",
            "extra": "mean: 462.2172595810049 usec\nrounds: 3414"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 422.423931205239,
            "unit": "iter/sec",
            "range": "stddev: 0.008443677988885371",
            "extra": "mean: 2.36729012285561 msec\nrounds: 1223"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1328.6361138515551,
            "unit": "iter/sec",
            "range": "stddev: 0.0037734853151638937",
            "extra": "mean: 752.651527061929 usec\nrounds: 1036"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15562.839863924373,
            "unit": "iter/sec",
            "range": "stddev: 0.000004866601090736094",
            "extra": "mean: 64.25562485662157 usec\nrounds: 2424"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28214.143154501642,
            "unit": "iter/sec",
            "range": "stddev: 0.0000041830105336823126",
            "extra": "mean: 35.44321706046378 usec\nrounds: 6241"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2306.323564947649,
            "unit": "iter/sec",
            "range": "stddev: 0.00002434302937338468",
            "extra": "mean: 433.5905053386118 usec\nrounds: 1086"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 112518.81804686863,
            "unit": "iter/sec",
            "range": "stddev: 9.336038320167262e-7",
            "extra": "mean: 8.887402279532118 usec\nrounds: 18250"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44462.995640699664,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019064509190408342",
            "extra": "mean: 22.490612375308327 usec\nrounds: 12256"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 58215.07425321055,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020638977781772425",
            "extra": "mean: 17.17768143093711 usec\nrounds: 19383"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70747.56983515661,
            "unit": "iter/sec",
            "range": "stddev: 0.000002362833479314972",
            "extra": "mean: 14.134761127909014 usec\nrounds: 13511"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 97396.54454713307,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018364276473698617",
            "extra": "mean: 10.267304704183529 usec\nrounds: 14200"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1258.7786433630063,
            "unit": "iter/sec",
            "range": "stddev: 0.0050960057548851785",
            "extra": "mean: 794.4208501411796 usec\nrounds: 308"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 940.3649387720968,
            "unit": "iter/sec",
            "range": "stddev: 0.007606204775643771",
            "extra": "mean: 1.0634169339679689 msec\nrounds: 1674"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 256059.53209881348,
            "unit": "iter/sec",
            "range": "stddev: 6.485363177167595e-7",
            "extra": "mean: 3.9053418234557253 usec\nrounds: 20501"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4800.438897306707,
            "unit": "iter/sec",
            "range": "stddev: 0.003740529413665115",
            "extra": "mean: 208.31428571271923 usec\nrounds: 9499"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 158257.48665892135,
            "unit": "iter/sec",
            "range": "stddev: 7.595290958430077e-7",
            "extra": "mean: 6.318816386584056 usec\nrounds: 20874"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 4766.024527082123,
            "unit": "iter/sec",
            "range": "stddev: 0.013859913936147085",
            "extra": "mean: 209.81847540180922 usec\nrounds: 15195"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2569.3969129510588,
            "unit": "iter/sec",
            "range": "stddev: 0.004783403928475879",
            "extra": "mean: 389.1963888333074 usec\nrounds: 3380"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 2140.513726686642,
            "unit": "iter/sec",
            "range": "stddev: 0.004795231878399143",
            "extra": "mean: 467.1775693529079 usec\nrounds: 2005"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3752.4964163641334,
            "unit": "iter/sec",
            "range": "stddev: 0.004363755627303021",
            "extra": "mean: 266.48926182557676 usec\nrounds: 4427"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 365358.5249821453,
            "unit": "iter/sec",
            "range": "stddev: 3.7186567823389115e-7",
            "extra": "mean: 2.737037544283027 usec\nrounds: 44082"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 8179.10280911876,
            "unit": "iter/sec",
            "range": "stddev: 0.00272232511384388",
            "extra": "mean: 122.26279866357895 usec\nrounds: 7308"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37002.76647236771,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023580422597265537",
            "extra": "mean: 27.025006380178702 usec\nrounds: 12179"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 6080.485858204721,
            "unit": "iter/sec",
            "range": "stddev: 0.0032886427163153183",
            "extra": "mean: 164.46054202241868 usec\nrounds: 6682"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 3624.7821099136727,
            "unit": "iter/sec",
            "range": "stddev: 0.004567956624906578",
            "extra": "mean: 275.8786513719071 usec\nrounds: 4822"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4004.3431350809487,
            "unit": "iter/sec",
            "range": "stddev: 0.0043869724531185785",
            "extra": "mean: 249.7288484693719 usec\nrounds: 5287"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4081.1189891099466,
            "unit": "iter/sec",
            "range": "stddev: 0.004151538132233048",
            "extra": "mean: 245.03083655938457 usec\nrounds: 5194"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 6725.71979740345,
            "unit": "iter/sec",
            "range": "stddev: 0.0005148475045100895",
            "extra": "mean: 148.68297076337655 usec\nrounds: 242"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1196884.1311115655,
            "unit": "iter/sec",
            "range": "stddev: 2.369342117091659e-7",
            "extra": "mean: 835.5027642243731 nsec\nrounds: 97126"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1207410.0846394536,
            "unit": "iter/sec",
            "range": "stddev: 4.543533075828163e-7",
            "extra": "mean: 828.2190224530148 nsec\nrounds: 132363"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1212791.2991676203,
            "unit": "iter/sec",
            "range": "stddev: 1.9906920483173987e-7",
            "extra": "mean: 824.5441739945973 nsec\nrounds: 129182"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1241407.9163792955,
            "unit": "iter/sec",
            "range": "stddev: 1.4770642192366278e-7",
            "extra": "mean: 805.5369929624836 nsec\nrounds: 172503"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 83722.80343411563,
            "unit": "iter/sec",
            "range": "stddev: 0.000001654777639106104",
            "extra": "mean: 11.944177201220151 usec\nrounds: 9193"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 51724.67184032268,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024896998028168138",
            "extra": "mean: 19.333133771965976 usec\nrounds: 9014"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 34158.9939457999,
            "unit": "iter/sec",
            "range": "stddev: 0.00000800764368578693",
            "extra": "mean: 29.274866864835094 usec\nrounds: 154"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 17654.190674424215,
            "unit": "iter/sec",
            "range": "stddev: 0.000007976417317475347",
            "extra": "mean: 56.643774752512954 usec\nrounds: 4165"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 52.80531130310762,
            "unit": "iter/sec",
            "range": "stddev: 0.030633505269847868",
            "extra": "mean: 18.937488963182183 msec\nrounds: 197"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 51.74555273557328,
            "unit": "iter/sec",
            "range": "stddev: 0.03159584827475946",
            "extra": "mean: 19.32533226787883 msec\nrounds: 197"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 50.17594831595673,
            "unit": "iter/sec",
            "range": "stddev: 0.032351269991961126",
            "extra": "mean: 19.92986746763657 msec\nrounds: 194"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 18.43916589142727,
            "unit": "iter/sec",
            "range": "stddev: 0.3219607027919197",
            "extra": "mean: 54.2323880531342 msec\nrounds: 187"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 22045.08081897288,
            "unit": "iter/sec",
            "range": "stddev: 0.000002103100695602515",
            "extra": "mean: 45.361593736565474 usec\nrounds: 11921"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17142.178554250102,
            "unit": "iter/sec",
            "range": "stddev: 0.000003019694352690039",
            "extra": "mean: 58.33564251097289 usec\nrounds: 10601"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21894.932648285827,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030373455120688964",
            "extra": "mean: 45.672668469171604 usec\nrounds: 13480"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4321.088016747192,
            "unit": "iter/sec",
            "range": "stddev: 0.000009703161979363607",
            "extra": "mean: 231.42319622380086 usec\nrounds: 2533"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4453.61888545616,
            "unit": "iter/sec",
            "range": "stddev: 0.0039849338445322015",
            "extra": "mean: 224.53650070185012 usec\nrounds: 12265"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 419393.8561784891,
            "unit": "iter/sec",
            "range": "stddev: 5.960593238191702e-7",
            "extra": "mean: 2.384393536691228 usec\nrounds: 73374"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 2295.98952834794,
            "unit": "iter/sec",
            "range": "stddev: 0.013041991519354746",
            "extra": "mean: 435.54205611710336 usec\nrounds: 4500"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4163.906752881732,
            "unit": "iter/sec",
            "range": "stddev: 0.000024247050009827476",
            "extra": "mean: 240.15907640292994 usec\nrounds: 1097"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3619.470610364697,
            "unit": "iter/sec",
            "range": "stddev: 0.000021610246575758805",
            "extra": "mean: 276.28349768510486 usec\nrounds: 1279"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5161.166410067605,
            "unit": "iter/sec",
            "range": "stddev: 0.00001809391510207703",
            "extra": "mean: 193.7546516712491 usec\nrounds: 2820"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5221.963358279916,
            "unit": "iter/sec",
            "range": "stddev: 0.000013134435179153125",
            "extra": "mean: 191.49885424117457 usec\nrounds: 2712"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21883.692432656302,
            "unit": "iter/sec",
            "range": "stddev: 0.000005084263657552272",
            "extra": "mean: 45.696127519491796 usec\nrounds: 11929"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21804.74174195008,
            "unit": "iter/sec",
            "range": "stddev: 0.000004439443100855925",
            "extra": "mean: 45.861584229456966 usec\nrounds: 12193"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21817.62139479235,
            "unit": "iter/sec",
            "range": "stddev: 0.000007526949002544289",
            "extra": "mean: 45.83451064187456 usec\nrounds: 13497"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21905.371757454148,
            "unit": "iter/sec",
            "range": "stddev: 0.000003965198091126438",
            "extra": "mean: 45.65090294163629 usec\nrounds: 13487"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 212.03299158081734,
            "unit": "iter/sec",
            "range": "stddev: 0.010697049282059596",
            "extra": "mean: 4.716247186555615 msec\nrounds: 203"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3728.3562981217033,
            "unit": "iter/sec",
            "range": "stddev: 0.003809613566825671",
            "extra": "mean: 268.2147091209568 usec\nrounds: 4861"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 223352.3128112694,
            "unit": "iter/sec",
            "range": "stddev: 0.0000176232210630452",
            "extra": "mean: 4.477231452915334 usec\nrounds: 35202"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 923405.2704787649,
            "unit": "iter/sec",
            "range": "stddev: 9.778197261137016e-7",
            "extra": "mean: 1.0829481181989815 usec\nrounds: 67250"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 55.17968864179219,
            "unit": "iter/sec",
            "range": "stddev: 0.0025800357035427133",
            "extra": "mean: 18.12261041361905 msec\nrounds: 56"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 110.55888652373383,
            "unit": "iter/sec",
            "range": "stddev: 0.0016813370758756298",
            "extra": "mean: 9.044953611986031 msec\nrounds: 41"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 156428.46534582565,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012367906380327513",
            "extra": "mean: 6.392698399164377 usec\nrounds: 20355"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 122446.69477806466,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018326244307022908",
            "extra": "mean: 8.166819053895296 usec\nrounds: 4487"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 71548.4705094613,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012522443097537883",
            "extra": "mean: 13.976539161207699 usec\nrounds: 9595"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 83080.88650069192,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014253873236941096",
            "extra": "mean: 12.03646280292967 usec\nrounds: 14658"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2191.916277844146,
            "unit": "iter/sec",
            "range": "stddev: 0.0054737259588101125",
            "extra": "mean: 456.221804686604 usec\nrounds: 2350"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 786.4033820306336,
            "unit": "iter/sec",
            "range": "stddev: 0.009348038689304429",
            "extra": "mean: 1.2716120286993449 msec\nrounds: 1759"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4435.310889465455,
            "unit": "iter/sec",
            "range": "stddev: 0.000038824995722586204",
            "extra": "mean: 225.46333840433905 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4718.883504146902,
            "unit": "iter/sec",
            "range": "stddev: 0.000024568224980878487",
            "extra": "mean: 211.91453425820137 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1297.2781945294037,
            "unit": "iter/sec",
            "range": "stddev: 0.000269697947668793",
            "extra": "mean: 770.8446840600421 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 227.3641723933904,
            "unit": "iter/sec",
            "range": "stddev: 0.0006843086752165631",
            "extra": "mean: 4.398230334503971 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10210.485220688679,
            "unit": "iter/sec",
            "range": "stddev: 0.00001126433198107485",
            "extra": "mean: 97.93853851076352 usec\nrounds: 3579"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7778.656288864723,
            "unit": "iter/sec",
            "range": "stddev: 0.000027078007103043",
            "extra": "mean: 128.5569078854296 usec\nrounds: 2453"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 278.1434109583176,
            "unit": "iter/sec",
            "range": "stddev: 0.0018508561965046876",
            "extra": "mean: 3.5952676231106526 msec\nrounds: 215"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7293.262059356325,
            "unit": "iter/sec",
            "range": "stddev: 0.00001721762324400544",
            "extra": "mean: 137.11285730054462 usec\nrounds: 2784"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1766.6051261301154,
            "unit": "iter/sec",
            "range": "stddev: 0.000030333096560726946",
            "extra": "mean: 566.0574540449664 usec\nrounds: 1169"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6834.121294180524,
            "unit": "iter/sec",
            "range": "stddev: 0.000014978816800016869",
            "extra": "mean: 146.32459052951438 usec\nrounds: 346"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 8972.559177740608,
            "unit": "iter/sec",
            "range": "stddev: 0.00002742730591895017",
            "extra": "mean: 111.45092277360843 usec\nrounds: 4264"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8623.70480263004,
            "unit": "iter/sec",
            "range": "stddev: 0.000014077007837193252",
            "extra": "mean: 115.95944236113255 usec\nrounds: 2658"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6665.833360892679,
            "unit": "iter/sec",
            "range": "stddev: 0.000010273487099572364",
            "extra": "mean: 150.0187517238027 usec\nrounds: 336"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2766.8561979242836,
            "unit": "iter/sec",
            "range": "stddev: 0.000037487702245242726",
            "extra": "mean: 361.42102388631815 usec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 4843.617679527829,
            "unit": "iter/sec",
            "range": "stddev: 0.00003737978103395157",
            "extra": "mean: 206.4572528559858 usec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7602.682043041997,
            "unit": "iter/sec",
            "range": "stddev: 0.00004285986988119684",
            "extra": "mean: 131.53252948611782 usec\nrounds: 4123"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1128.541387000615,
            "unit": "iter/sec",
            "range": "stddev: 0.00012096011113190679",
            "extra": "mean: 886.0995365511171 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 262.4743436410283,
            "unit": "iter/sec",
            "range": "stddev: 0.000686193810605",
            "extra": "mean: 3.809896183101404 msec\nrounds: 198"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.700624198992735,
            "unit": "iter/sec",
            "range": "stddev: 0.0048132273031411075",
            "extra": "mean: 17.035593976139683 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 45.60517817503784,
            "unit": "iter/sec",
            "range": "stddev: 0.0031500669321899424",
            "extra": "mean: 21.92733457069034 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 18.6045085116594,
            "unit": "iter/sec",
            "range": "stddev: 0.006539439276527451",
            "extra": "mean: 53.750412131194025 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.468057999669735,
            "unit": "iter/sec",
            "range": "stddev: 0.005796957431804833",
            "extra": "mean: 33.9350492662668 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 46.79280675984429,
            "unit": "iter/sec",
            "range": "stddev: 0.002922748337123216",
            "extra": "mean: 21.370806097020875 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 64.52802611617841,
            "unit": "iter/sec",
            "range": "stddev: 0.0031435569590490065",
            "extra": "mean: 15.497142252570484 msec\nrounds: 64"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6736.57558175751,
            "unit": "iter/sec",
            "range": "stddev: 0.0000206312341293208",
            "extra": "mean: 148.44337272901333 usec\nrounds: 3876"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1642.5258859799694,
            "unit": "iter/sec",
            "range": "stddev: 0.00005850642618478004",
            "extra": "mean: 608.8184110434136 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4690.329975708826,
            "unit": "iter/sec",
            "range": "stddev: 0.000018424174455025596",
            "extra": "mean: 213.20461570486304 usec\nrounds: 857"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 659.7393686577853,
            "unit": "iter/sec",
            "range": "stddev: 0.00011752832643783834",
            "extra": "mean: 1.515750078753769 msec\nrounds: 510"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 440.3270665378643,
            "unit": "iter/sec",
            "range": "stddev: 0.0002693964291644358",
            "extra": "mean: 2.2710391343022485 msec\nrounds: 297"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 68.09877702451924,
            "unit": "iter/sec",
            "range": "stddev: 0.0024184149250506114",
            "extra": "mean: 14.684551524911322 msec\nrounds: 76"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 58.57021822655705,
            "unit": "iter/sec",
            "range": "stddev: 0.00242849433084274",
            "extra": "mean: 17.073523546247905 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 23.802280003726253,
            "unit": "iter/sec",
            "range": "stddev: 0.020487899245840702",
            "extra": "mean: 42.01278196220907 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 23.36871501777824,
            "unit": "iter/sec",
            "range": "stddev: 0.07215740471602435",
            "extra": "mean: 42.79225448379293 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 15.244560755097522,
            "unit": "iter/sec",
            "range": "stddev: 0.00913247999617346",
            "extra": "mean: 65.59716715128161 msec\nrounds: 6"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 647.1374260165708,
            "unit": "iter/sec",
            "range": "stddev: 0.00010944579785652153",
            "extra": "mean: 1.5452668317384473 msec\nrounds: 423"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 14.527074295000244,
            "unit": "iter/sec",
            "range": "stddev: 0.01356510350084919",
            "extra": "mean: 68.83698532086176 msec\nrounds: 6"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 10.638361701521047,
            "unit": "iter/sec",
            "range": "stddev: 0.030185729526238558",
            "extra": "mean: 93.99943600874394 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 635.5065495488731,
            "unit": "iter/sec",
            "range": "stddev: 0.00014908222420936563",
            "extra": "mean: 1.5735479055406585 msec\nrounds: 442"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 10.654164190510702,
            "unit": "iter/sec",
            "range": "stddev: 0.024383374742702555",
            "extra": "mean: 93.86001399252564 msec\nrounds: 7"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 7.6875110272547245,
            "unit": "iter/sec",
            "range": "stddev: 0.005569158031215516",
            "extra": "mean: 130.08111421950161 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 6.366418283155977,
            "unit": "iter/sec",
            "range": "stddev: 0.03619258540020796",
            "extra": "mean: 157.0741907809861 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 5.900175350425416,
            "unit": "iter/sec",
            "range": "stddev: 0.05144072838865659",
            "extra": "mean: 169.4864882156253 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 7.378762330743515,
            "unit": "iter/sec",
            "range": "stddev: 0.030214856204568822",
            "extra": "mean: 135.5240831966512 msec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 81.02756237557097,
            "unit": "iter/sec",
            "range": "stddev: 0.0005133306772574421",
            "extra": "mean: 12.341479500085397 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 80.76851631312091,
            "unit": "iter/sec",
            "range": "stddev: 0.00035357946334503175",
            "extra": "mean: 12.38106189945635 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 80.61648298403004,
            "unit": "iter/sec",
            "range": "stddev: 0.000503340809652619",
            "extra": "mean: 12.404411145027227 msec\nrounds: 67"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 75.49213131037682,
            "unit": "iter/sec",
            "range": "stddev: 0.0005021429450167657",
            "extra": "mean: 13.24641366778506 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 12.15190913494579,
            "unit": "iter/sec",
            "range": "stddev: 0.020121880658171287",
            "extra": "mean: 82.29159623357084 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 563.1277658949274,
            "unit": "iter/sec",
            "range": "stddev: 0.0001623850264289788",
            "extra": "mean: 1.7757959393296678 msec\nrounds: 401"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 18.043367908423168,
            "unit": "iter/sec",
            "range": "stddev: 0.07817978502414062",
            "extra": "mean: 55.422025703592226 msec\nrounds: 10"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 56.037337610807775,
            "unit": "iter/sec",
            "range": "stddev: 0.006752494554897081",
            "extra": "mean: 17.84524466428492 msec\nrounds: 18"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 62.93498857299785,
            "unit": "iter/sec",
            "range": "stddev: 0.002069944368193776",
            "extra": "mean: 15.889412593443266 msec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 62.220768647039854,
            "unit": "iter/sec",
            "range": "stddev: 0.0027575689569100947",
            "extra": "mean: 16.07180402532001 msec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 681.078381953248,
            "unit": "iter/sec",
            "range": "stddev: 0.00013559165610400135",
            "extra": "mean: 1.468259786975068 msec\nrounds: 512"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 664.4048209898107,
            "unit": "iter/sec",
            "range": "stddev: 0.00013105805037674472",
            "extra": "mean: 1.505106477870268 msec\nrounds: 455"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 666.295309950533,
            "unit": "iter/sec",
            "range": "stddev: 0.0001237621448873324",
            "extra": "mean: 1.500836018302818 msec\nrounds: 501"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 60.93621778330521,
            "unit": "iter/sec",
            "range": "stddev: 0.0020246192090596694",
            "extra": "mean: 16.41060171401008 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 50.5807703889536,
            "unit": "iter/sec",
            "range": "stddev: 0.0037936336103494396",
            "extra": "mean: 19.770359215770092 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 67.33816904780379,
            "unit": "iter/sec",
            "range": "stddev: 0.0023398658524058785",
            "extra": "mean: 14.850418627956662 msec\nrounds: 59"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 56.21144470307684,
            "unit": "iter/sec",
            "range": "stddev: 0.0044448334613920535",
            "extra": "mean: 17.789971513492574 msec\nrounds: 72"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 67.46154512445857,
            "unit": "iter/sec",
            "range": "stddev: 0.0015524849210808722",
            "extra": "mean: 14.823259653408744 msec\nrounds: 73"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 639.6337910183607,
            "unit": "iter/sec",
            "range": "stddev: 0.00011761963956570984",
            "extra": "mean: 1.5633945767747828 msec\nrounds: 468"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 722.587308086746,
            "unit": "iter/sec",
            "range": "stddev: 0.00010673303336813526",
            "extra": "mean: 1.3839158103230216 msec\nrounds: 530"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 273.5089744989707,
            "unit": "iter/sec",
            "range": "stddev: 0.002169566326255761",
            "extra": "mean: 3.65618715741177 msec\nrounds: 209"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 668.8568852189353,
            "unit": "iter/sec",
            "range": "stddev: 0.00012954357404991863",
            "extra": "mean: 1.4950881453102967 msec\nrounds: 502"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 726.1410197364393,
            "unit": "iter/sec",
            "range": "stddev: 0.00012290509125422716",
            "extra": "mean: 1.3771429692306334 msec\nrounds: 525"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 81.29842085703751,
            "unit": "iter/sec",
            "range": "stddev: 0.0034421875741302353",
            "extra": "mean: 12.300361919187708 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 99.94685996920205,
            "unit": "iter/sec",
            "range": "stddev: 0.00037372373344748456",
            "extra": "mean: 10.00531682844407 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 112.6593826313592,
            "unit": "iter/sec",
            "range": "stddev: 0.0007587425776895881",
            "extra": "mean: 8.876313509298834 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 119.9176281015663,
            "unit": "iter/sec",
            "range": "stddev: 0.0006943042264698263",
            "extra": "mean: 8.33905753333474 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 118.99719017401043,
            "unit": "iter/sec",
            "range": "stddev: 0.000589209230655227",
            "extra": "mean: 8.403559769249114 msec\nrounds: 128"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 131.16745148593424,
            "unit": "iter/sec",
            "range": "stddev: 0.0004918114608764694",
            "extra": "mean: 7.623842566669332 msec\nrounds: 119"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 132.5879676163137,
            "unit": "iter/sec",
            "range": "stddev: 0.00043068431463930856",
            "extra": "mean: 7.542162520311228 msec\nrounds: 123"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 121.09074209122487,
            "unit": "iter/sec",
            "range": "stddev: 0.00063215114490684",
            "extra": "mean: 8.258269647456949 msec\nrounds: 122"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 251.2160578042614,
            "unit": "iter/sec",
            "range": "stddev: 0.00044966689309589356",
            "extra": "mean: 3.9806372599762883 msec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 6736.8463353285815,
            "unit": "iter/sec",
            "range": "stddev: 0.000013667109835837443",
            "extra": "mean: 148.43740679610235 usec\nrounds: 39"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 6653.4404627320355,
            "unit": "iter/sec",
            "range": "stddev: 0.000025922640931093795",
            "extra": "mean: 150.29818115925247 usec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 46.53954338710365,
            "unit": "iter/sec",
            "range": "stddev: 0.003150561437252912",
            "extra": "mean: 21.487103809383424 msec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 91.95176355731171,
            "unit": "iter/sec",
            "range": "stddev: 0.0011023324641256233",
            "extra": "mean: 10.875267219608244 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 661.8228071348706,
            "unit": "iter/sec",
            "range": "stddev: 0.0002311927495033342",
            "extra": "mean: 1.5109784510587492 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 654.2735906296218,
            "unit": "iter/sec",
            "range": "stddev: 0.00018560894527699438",
            "extra": "mean: 1.5284126003583274 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 66.27315599987809,
            "unit": "iter/sec",
            "range": "stddev: 0.0018820065120750938",
            "extra": "mean: 15.089065624124487 msec\nrounds: 32"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "harumaki4649",
            "username": "harumaki4649",
            "email": "83683593+harumaki4649@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "08a317bd8d2c05918f36aa89e9da13cc0d15bd06",
          "message": "Update Dockerfile to specify uv version and optimize installs",
          "timestamp": "2026-03-12T17:32:39Z",
          "url": "https://github.com/disnana/NanaSQLite/commit/08a317bd8d2c05918f36aa89e9da13cc0d15bd06"
        },
        "date": 1773337016397,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 3929.6672817798717,
            "unit": "iter/sec",
            "range": "stddev: 0.004630330154533323",
            "extra": "mean: 254.47447030351844 usec\nrounds: 5123"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 3821.1150439725457,
            "unit": "iter/sec",
            "range": "stddev: 0.004719079215480791",
            "extra": "mean: 261.703714358825 usec\nrounds: 6336"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 687.9796529503589,
            "unit": "iter/sec",
            "range": "stddev: 0.010556889340724313",
            "extra": "mean: 1.4535313591202312 msec\nrounds: 2253"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2477641.9308842462,
            "unit": "iter/sec",
            "range": "stddev: 2.7558247818387197e-8",
            "extra": "mean: 403.6095722851365 nsec\nrounds: 54163"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 89423.60421088441,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025206636798512337",
            "extra": "mean: 11.182729759379153 usec\nrounds: 7282"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 492.8474357990322,
            "unit": "iter/sec",
            "range": "stddev: 0.00017756931382349083",
            "extra": "mean: 2.0290254698773937 msec\nrounds: 223"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2757.9856776406255,
            "unit": "iter/sec",
            "range": "stddev: 0.000011368738574275822",
            "extra": "mean: 362.5834637602144 usec\nrounds: 1686"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2265118.250418519,
            "unit": "iter/sec",
            "range": "stddev: 1.7880228607188326e-7",
            "extra": "mean: 441.4780552031811 nsec\nrounds: 125298"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 118883.55904949551,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012086385672284856",
            "extra": "mean: 8.411592048515843 usec\nrounds: 8996"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 86157.07485039825,
            "unit": "iter/sec",
            "range": "stddev: 9.952730693393166e-7",
            "extra": "mean: 11.606707884829932 usec\nrounds: 372"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 71094.44561236486,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013058504067750453",
            "extra": "mean: 14.065796440025668 usec\nrounds: 17590"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5798915.539597982,
            "unit": "iter/sec",
            "range": "stddev: 1.758067902544088e-8",
            "extra": "mean: 172.4460363617156 nsec\nrounds: 133673"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1406727.6998393713,
            "unit": "iter/sec",
            "range": "stddev: 1.7188131096726998e-7",
            "extra": "mean: 710.8696303585875 nsec\nrounds: 3572"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 75182.08633016548,
            "unit": "iter/sec",
            "range": "stddev: 7.451577529450261e-7",
            "extra": "mean: 13.301040830503897 usec\nrounds: 311"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70818.23803614412,
            "unit": "iter/sec",
            "range": "stddev: 0.000001202865757672258",
            "extra": "mean: 14.120656312991313 usec\nrounds: 13664"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3467.904080292178,
            "unit": "iter/sec",
            "range": "stddev: 0.005160372482289815",
            "extra": "mean: 288.3586099404883 usec\nrounds: 6492"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 3603.8207037006287,
            "unit": "iter/sec",
            "range": "stddev: 0.007424617003034134",
            "extra": "mean: 277.4832829427772 usec\nrounds: 8804"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51472.96351833578,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032937152434185235",
            "extra": "mean: 19.4276748733105 usec\nrounds: 9423"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 8299.248670481074,
            "unit": "iter/sec",
            "range": "stddev: 0.0028570053642741158",
            "extra": "mean: 120.49283491851727 usec\nrounds: 11236"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7431.584960302647,
            "unit": "iter/sec",
            "range": "stddev: 0.000014007125423078022",
            "extra": "mean: 134.56079764164812 usec\nrounds: 1028"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12427.203589101815,
            "unit": "iter/sec",
            "range": "stddev: 0.000006835129312105614",
            "extra": "mean: 80.46862617403016 usec\nrounds: 3545"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21877.283788123685,
            "unit": "iter/sec",
            "range": "stddev: 0.000004300777176925742",
            "extra": "mean: 45.7095135614075 usec\nrounds: 5636"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8272.044279645119,
            "unit": "iter/sec",
            "range": "stddev: 0.000009438282903268418",
            "extra": "mean: 120.8891014353832 usec\nrounds: 3219"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 7916.81351424675,
            "unit": "iter/sec",
            "range": "stddev: 0.002856083965236906",
            "extra": "mean: 126.31344646434376 usec\nrounds: 7742"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2123.818753341987,
            "unit": "iter/sec",
            "range": "stddev: 0.005145339205476509",
            "extra": "mean: 470.8499717437873 usec\nrounds: 3693"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2048.190459480815,
            "unit": "iter/sec",
            "range": "stddev: 0.005608266087084338",
            "extra": "mean: 488.23584514375904 usec\nrounds: 2748"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2048.91146168086,
            "unit": "iter/sec",
            "range": "stddev: 0.005341343408236449",
            "extra": "mean: 488.0640372715924 usec\nrounds: 3828"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 410.63477239389914,
            "unit": "iter/sec",
            "range": "stddev: 0.008155764891312828",
            "extra": "mean: 2.4352540681595167 msec\nrounds: 1275"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1324.1026887400367,
            "unit": "iter/sec",
            "range": "stddev: 0.0038788525428948206",
            "extra": "mean: 755.2284339453763 usec\nrounds: 1024"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15155.024563900732,
            "unit": "iter/sec",
            "range": "stddev: 0.000009497231431221",
            "extra": "mean: 65.98471653962213 usec\nrounds: 1993"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28575.416837166686,
            "unit": "iter/sec",
            "range": "stddev: 0.000003112077014796947",
            "extra": "mean: 34.99511505635668 usec\nrounds: 6785"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2297.3119023330178,
            "unit": "iter/sec",
            "range": "stddev: 0.000027677555448799442",
            "extra": "mean: 435.2913502883337 usec\nrounds: 1086"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 112947.08600116498,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011429607212407285",
            "extra": "mean: 8.853703405767243 usec\nrounds: 17881"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44439.46285177026,
            "unit": "iter/sec",
            "range": "stddev: 0.000002194988313294763",
            "extra": "mean: 22.50252221399577 usec\nrounds: 12262"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 58069.21829046297,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011955293021330304",
            "extra": "mean: 17.220827650856037 usec\nrounds: 17154"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 70407.29082411857,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017627717680337972",
            "extra": "mean: 14.203074543772138 usec\nrounds: 11225"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 98086.67792738552,
            "unit": "iter/sec",
            "range": "stddev: 0.000001251564231558887",
            "extra": "mean: 10.195064417823483 usec\nrounds: 13262"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1260.9191002058108,
            "unit": "iter/sec",
            "range": "stddev: 0.00508932091438121",
            "extra": "mean: 793.0722913442878 usec\nrounds: 320"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 884.0329824020855,
            "unit": "iter/sec",
            "range": "stddev: 0.00837353176023457",
            "extra": "mean: 1.1311795146859907 msec\nrounds: 2025"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 258445.55235012752,
            "unit": "iter/sec",
            "range": "stddev: 6.4960529388778e-7",
            "extra": "mean: 3.86928693841578 usec\nrounds: 21889"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 887.5569856349233,
            "unit": "iter/sec",
            "range": "stddev: 0.038084776846816396",
            "extra": "mean: 1.1266882196692298 msec\nrounds: 8073"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 157024.2291717448,
            "unit": "iter/sec",
            "range": "stddev: 9.379861269190324e-7",
            "extra": "mean: 6.368443935529548 usec\nrounds: 17676"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 2848.323997291941,
            "unit": "iter/sec",
            "range": "stddev: 0.01331822267522259",
            "extra": "mean: 351.0836551427279 usec\nrounds: 13575"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 1221.4904955281218,
            "unit": "iter/sec",
            "range": "stddev: 0.015127124476481875",
            "extra": "mean: 818.6719451858212 usec\nrounds: 3100"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1181.169329056072,
            "unit": "iter/sec",
            "range": "stddev: 0.013040116695013865",
            "extra": "mean: 846.6186645729678 usec\nrounds: 2034"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3122.891614765152,
            "unit": "iter/sec",
            "range": "stddev: 0.005754498417531329",
            "extra": "mean: 320.2160444095983 usec\nrounds: 4196"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 367657.28850664565,
            "unit": "iter/sec",
            "range": "stddev: 3.707721888919981e-7",
            "extra": "mean: 2.719924318818242 usec\nrounds: 48043"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 7794.088488663975,
            "unit": "iter/sec",
            "range": "stddev: 0.0028077592362838574",
            "extra": "mean: 128.30236678149586 usec\nrounds: 9984"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37192.69405410153,
            "unit": "iter/sec",
            "range": "stddev: 0.000002727154645484376",
            "extra": "mean: 26.88700094016777 usec\nrounds: 9874"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 7946.073064960823,
            "unit": "iter/sec",
            "range": "stddev: 0.0027343111693444366",
            "extra": "mean: 125.84832681813887 usec\nrounds: 6190"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4090.0610430533393,
            "unit": "iter/sec",
            "range": "stddev: 0.004341440051643409",
            "extra": "mean: 244.49512842807684 usec\nrounds: 6874"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 3853.352144726374,
            "unit": "iter/sec",
            "range": "stddev: 0.00445238964469557",
            "extra": "mean: 259.51430402450535 usec\nrounds: 4998"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 3773.7708910341853,
            "unit": "iter/sec",
            "range": "stddev: 0.00452442559489371",
            "extra": "mean: 264.98693982081 usec\nrounds: 4478"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 3502.881982898478,
            "unit": "iter/sec",
            "range": "stddev: 0.004902934877554098",
            "extra": "mean: 285.47921536669776 usec\nrounds: 1204"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1219445.9535248,
            "unit": "iter/sec",
            "range": "stddev: 3.680337585211343e-7",
            "extra": "mean: 820.0445432694307 nsec\nrounds: 114653"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1228357.450105128,
            "unit": "iter/sec",
            "range": "stddev: 3.539704171889933e-7",
            "extra": "mean: 814.0952781410782 nsec\nrounds: 142492"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1229633.932108863,
            "unit": "iter/sec",
            "range": "stddev: 4.4511856669771617e-7",
            "extra": "mean: 813.250166482448 nsec\nrounds: 115635"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1236252.1168253454,
            "unit": "iter/sec",
            "range": "stddev: 2.9678738331058224e-7",
            "extra": "mean: 808.8964915732295 nsec\nrounds: 188147"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 84787.58258714211,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020731074583714543",
            "extra": "mean: 11.794179872650929 usec\nrounds: 11897"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 62494.34392643836,
            "unit": "iter/sec",
            "range": "stddev: 0.000002606236443270675",
            "extra": "mean: 16.00144808587946 usec\nrounds: 8883"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 43408.49536846547,
            "unit": "iter/sec",
            "range": "stddev: 0.000005743116065771692",
            "extra": "mean: 23.036965264786854 usec\nrounds: 141"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 19064.33981823846,
            "unit": "iter/sec",
            "range": "stddev: 0.000008061405749024356",
            "extra": "mean: 52.45395379719997 usec\nrounds: 4005"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 48.94463634895598,
            "unit": "iter/sec",
            "range": "stddev: 0.03332373557183342",
            "extra": "mean: 20.431247928177335 msec\nrounds: 189"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 21.086687745725673,
            "unit": "iter/sec",
            "range": "stddev: 0.22349715829465572",
            "extra": "mean: 47.42328487330604 msec\nrounds: 193"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 48.83205436869863,
            "unit": "iter/sec",
            "range": "stddev: 0.033918670040866565",
            "extra": "mean: 20.478352035932378 msec\nrounds: 197"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 23.720982753018706,
            "unit": "iter/sec",
            "range": "stddev: 0.305029588364769",
            "extra": "mean: 42.15676940588564 msec\nrounds: 243"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21620.538840549438,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020727045362857635",
            "extra": "mean: 46.25231625238195 usec\nrounds: 11942"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 16745.89250142403,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031118258743469096",
            "extra": "mean: 59.71613635492777 usec\nrounds: 9580"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21616.790324131456,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031034528361948587",
            "extra": "mean: 46.260336757010165 usec\nrounds: 11669"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4296.29230778443,
            "unit": "iter/sec",
            "range": "stddev: 0.000010045815434621776",
            "extra": "mean: 232.75883677377007 usec\nrounds: 2658"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 1688.3279146351701,
            "unit": "iter/sec",
            "range": "stddev: 0.02756395779161705",
            "extra": "mean: 592.3019997072603 usec\nrounds: 16394"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 424654.8814603389,
            "unit": "iter/sec",
            "range": "stddev: 3.3660960752335524e-7",
            "extra": "mean: 2.3548534201729083 usec\nrounds: 74173"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 3749.113014003463,
            "unit": "iter/sec",
            "range": "stddev: 0.0045063921087802414",
            "extra": "mean: 266.72975614895034 usec\nrounds: 5806"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4235.24333827658,
            "unit": "iter/sec",
            "range": "stddev: 0.000015783279370260152",
            "extra": "mean: 236.11394201659343 usec\nrounds: 1265"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3623.6323842774486,
            "unit": "iter/sec",
            "range": "stddev: 0.0000237101496041822",
            "extra": "mean: 275.96618363907237 usec\nrounds: 1260"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5129.836729079796,
            "unit": "iter/sec",
            "range": "stddev: 0.000016818958466777588",
            "extra": "mean: 194.93797810976 usec\nrounds: 2535"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5085.123180338996,
            "unit": "iter/sec",
            "range": "stddev: 0.000013211928348242314",
            "extra": "mean: 196.65207007499393 usec\nrounds: 2758"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21425.833217725543,
            "unit": "iter/sec",
            "range": "stddev: 0.000005184859149769421",
            "extra": "mean: 46.672630643493584 usec\nrounds: 12383"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21629.804964239065,
            "unit": "iter/sec",
            "range": "stddev: 0.0000042410638853453736",
            "extra": "mean: 46.23250194134055 usec\nrounds: 12573"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21561.20588854032,
            "unit": "iter/sec",
            "range": "stddev: 0.000007575506990020015",
            "extra": "mean: 46.37959514738901 usec\nrounds: 13120"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21600.302099300803,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033849285877227313",
            "extra": "mean: 46.2956488017068 usec\nrounds: 19432"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 212.26082013088222,
            "unit": "iter/sec",
            "range": "stddev: 0.010516133024855708",
            "extra": "mean: 4.711185038215671 msec\nrounds: 196"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3612.9498554717934,
            "unit": "iter/sec",
            "range": "stddev: 0.0038786271189311227",
            "extra": "mean: 276.7821420176938 usec\nrounds: 4564"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 222013.76397206026,
            "unit": "iter/sec",
            "range": "stddev: 0.000019569212489468422",
            "extra": "mean: 4.504225243106309 usec\nrounds: 35411"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 929993.360855749,
            "unit": "iter/sec",
            "range": "stddev: 2.574132335730285e-7",
            "extra": "mean: 1.0752764934577954 usec\nrounds: 66177"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 48.35712274100067,
            "unit": "iter/sec",
            "range": "stddev: 0.007643988432084822",
            "extra": "mean: 20.679476844724004 msec\nrounds: 71"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 110.27438367039996,
            "unit": "iter/sec",
            "range": "stddev: 0.002686219522923589",
            "extra": "mean: 9.06828917755649 msec\nrounds: 58"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 156594.35658770043,
            "unit": "iter/sec",
            "range": "stddev: 7.72130453711043e-7",
            "extra": "mean: 6.385926171227962 usec\nrounds: 21566"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 134296.7156041689,
            "unit": "iter/sec",
            "range": "stddev: 7.189792935619658e-7",
            "extra": "mean: 7.446198482972861 usec\nrounds: 5096"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 70715.75174307861,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016313699238741217",
            "extra": "mean: 14.141120971649377 usec\nrounds: 13606"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82817.83272763909,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014424223705707856",
            "extra": "mean: 12.074694145748474 usec\nrounds: 14063"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2332.3393155338044,
            "unit": "iter/sec",
            "range": "stddev: 0.004932501915099978",
            "extra": "mean: 428.75408108066347 usec\nrounds: 2433"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 545.1616140871487,
            "unit": "iter/sec",
            "range": "stddev: 0.027222792985318937",
            "extra": "mean: 1.8343184372481176 msec\nrounds: 2007"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4789.91519672167,
            "unit": "iter/sec",
            "range": "stddev: 0.00003429233512590197",
            "extra": "mean: 208.77196337096393 usec\nrounds: 50"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 5435.666146310108,
            "unit": "iter/sec",
            "range": "stddev: 0.000027006758176982363",
            "extra": "mean: 183.9700918127265 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1352.4773459500434,
            "unit": "iter/sec",
            "range": "stddev: 0.00028167482877111623",
            "extra": "mean: 739.3839186988771 usec\nrounds: 49"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 197.47013784198737,
            "unit": "iter/sec",
            "range": "stddev: 0.004473879869067871",
            "extra": "mean: 5.064056828684572 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10195.397649855244,
            "unit": "iter/sec",
            "range": "stddev: 0.000016324810153865467",
            "extra": "mean: 98.08347200799943 usec\nrounds: 3877"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7403.8750187724445,
            "unit": "iter/sec",
            "range": "stddev: 0.00003438156301804068",
            "extra": "mean: 135.0644084975112 usec\nrounds: 2657"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 294.7112778856844,
            "unit": "iter/sec",
            "range": "stddev: 0.0003040120711329875",
            "extra": "mean: 3.3931514503760867 msec\nrounds: 231"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7131.528181116188,
            "unit": "iter/sec",
            "range": "stddev: 0.00005486980650272311",
            "extra": "mean: 140.22240038929294 usec\nrounds: 2045"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1737.5610734169904,
            "unit": "iter/sec",
            "range": "stddev: 0.00003233238764400894",
            "extra": "mean: 575.5193387438497 usec\nrounds: 947"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 7252.951329685191,
            "unit": "iter/sec",
            "range": "stddev: 0.000014706313349187792",
            "extra": "mean: 137.8749083710457 usec\nrounds: 326"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 9204.906080410223,
            "unit": "iter/sec",
            "range": "stddev: 0.000022342139079757474",
            "extra": "mean: 108.63771897990232 usec\nrounds: 3825"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 7836.701325145509,
            "unit": "iter/sec",
            "range": "stddev: 0.00001593330510502761",
            "extra": "mean: 127.60471000614949 usec\nrounds: 2829"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 5784.833160524503,
            "unit": "iter/sec",
            "range": "stddev: 0.00008787821865853299",
            "extra": "mean: 172.86583247101484 usec\nrounds: 340"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2739.2699200778125,
            "unit": "iter/sec",
            "range": "stddev: 0.00004998397366865273",
            "extra": "mean: 365.06077501540767 usec\nrounds: 39"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 5558.593961875087,
            "unit": "iter/sec",
            "range": "stddev: 0.000020966622772765644",
            "extra": "mean: 179.9016094463336 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7543.392197111201,
            "unit": "iter/sec",
            "range": "stddev: 0.00004092794624601821",
            "extra": "mean: 132.56635395186763 usec\nrounds: 3153"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1228.340128342658,
            "unit": "iter/sec",
            "range": "stddev: 0.00011113176101283309",
            "extra": "mean: 814.106758320477 usec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 270.9682698111446,
            "unit": "iter/sec",
            "range": "stddev: 0.00023373362737186187",
            "extra": "mean: 3.690469001027187 msec\nrounds: 236"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 59.19247936909849,
            "unit": "iter/sec",
            "range": "stddev: 0.004483593996170732",
            "extra": "mean: 16.894038071364374 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 43.96999426243604,
            "unit": "iter/sec",
            "range": "stddev: 0.004711422775595845",
            "extra": "mean: 22.742782135277853 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 19.372110972896024,
            "unit": "iter/sec",
            "range": "stddev: 0.003927679391313831",
            "extra": "mean: 51.62060042909746 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.406053234113728,
            "unit": "iter/sec",
            "range": "stddev: 0.006891591856064445",
            "extra": "mean: 34.0066037437458 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 46.54694750516069,
            "unit": "iter/sec",
            "range": "stddev: 0.005109500283219516",
            "extra": "mean: 21.483685904196605 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 64.84363162429388,
            "unit": "iter/sec",
            "range": "stddev: 0.0023796046343822095",
            "extra": "mean: 15.42171490014675 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6731.818421006428,
            "unit": "iter/sec",
            "range": "stddev: 0.000022767579738984345",
            "extra": "mean: 148.54827291234287 usec\nrounds: 3967"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1670.680602330649,
            "unit": "iter/sec",
            "range": "stddev: 0.00006629922207725612",
            "extra": "mean: 598.5584549224851 usec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4614.537290521583,
            "unit": "iter/sec",
            "range": "stddev: 0.000022139859486129765",
            "extra": "mean: 216.70645116554465 usec\nrounds: 850"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 664.5950904134476,
            "unit": "iter/sec",
            "range": "stddev: 0.00013635805725423564",
            "extra": "mean: 1.5046755752858416 msec\nrounds: 471"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 458.7126599392512,
            "unit": "iter/sec",
            "range": "stddev: 0.00016014017751250217",
            "extra": "mean: 2.1800139549940334 msec\nrounds: 348"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 62.85332970813654,
            "unit": "iter/sec",
            "range": "stddev: 0.00607269131613014",
            "extra": "mean: 15.91005607250346 msec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 40.22289150967018,
            "unit": "iter/sec",
            "range": "stddev: 0.017998607885102567",
            "extra": "mean: 24.861464764649885 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 31.444095320407612,
            "unit": "iter/sec",
            "range": "stddev: 0.0063356520251337395",
            "extra": "mean: 31.80247324053198 msec\nrounds: 21"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 63.16331785721033,
            "unit": "iter/sec",
            "range": "stddev: 0.0025711909281220984",
            "extra": "mean: 15.831973903914331 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 64.55025857400213,
            "unit": "iter/sec",
            "range": "stddev: 0.0025948746824664888",
            "extra": "mean: 15.491804712967548 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 663.3046016271866,
            "unit": "iter/sec",
            "range": "stddev: 0.00012071419713530833",
            "extra": "mean: 1.5076029889538662 msec\nrounds: 471"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 62.282223336960804,
            "unit": "iter/sec",
            "range": "stddev: 0.0030774446826333816",
            "extra": "mean: 16.055945764649017 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 64.57538381208603,
            "unit": "iter/sec",
            "range": "stddev: 0.002631461573399945",
            "extra": "mean: 15.485777102153877 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 659.4484315482345,
            "unit": "iter/sec",
            "range": "stddev: 0.0001214173064878302",
            "extra": "mean: 1.5164188011672546 msec\nrounds: 416"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 41.905366353196435,
            "unit": "iter/sec",
            "range": "stddev: 0.004977429526661008",
            "extra": "mean: 23.863292151453116 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 21.589983716516763,
            "unit": "iter/sec",
            "range": "stddev: 0.003163193740669685",
            "extra": "mean: 46.31777462782338 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 21.442893871329105,
            "unit": "iter/sec",
            "range": "stddev: 0.003500662743407964",
            "extra": "mean: 46.63549640270717 msec\nrounds: 17"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 21.31197370869008,
            "unit": "iter/sec",
            "range": "stddev: 0.004570247910455532",
            "extra": "mean: 46.92197980669637 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 21.35680788545032,
            "unit": "iter/sec",
            "range": "stddev: 0.0036767321409582766",
            "extra": "mean: 46.82347686806073 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 83.22118808145747,
            "unit": "iter/sec",
            "range": "stddev: 0.0003852173896366814",
            "extra": "mean: 12.016170677847006 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 83.32200476909009,
            "unit": "iter/sec",
            "range": "stddev: 0.0004246342744002099",
            "extra": "mean: 12.001631535046425 msec\nrounds: 90"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.78786103048579,
            "unit": "iter/sec",
            "range": "stddev: 0.0003071528540616485",
            "extra": "mean: 12.079065548411261 msec\nrounds: 75"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.55760073095851,
            "unit": "iter/sec",
            "range": "stddev: 0.0004148976886495938",
            "extra": "mean: 12.893642796776616 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 66.49434101103598,
            "unit": "iter/sec",
            "range": "stddev: 0.002531266308472905",
            "extra": "mean: 15.038873756701058 msec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 576.8893025484986,
            "unit": "iter/sec",
            "range": "stddev: 0.00014437270652890914",
            "extra": "mean: 1.7334348125062191 msec\nrounds: 409"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 55.88059769525339,
            "unit": "iter/sec",
            "range": "stddev: 0.0074727403796813465",
            "extra": "mean: 17.895298927429725 msec\nrounds: 55"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 62.03602806007779,
            "unit": "iter/sec",
            "range": "stddev: 0.0023556649345653617",
            "extra": "mean: 16.11966515702079 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 58.845939685083884,
            "unit": "iter/sec",
            "range": "stddev: 0.005292169768743496",
            "extra": "mean: 16.993525897479675 msec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 62.16472062412653,
            "unit": "iter/sec",
            "range": "stddev: 0.0024392716525878963",
            "extra": "mean: 16.086294444181792 msec\nrounds: 63"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 690.6779570961595,
            "unit": "iter/sec",
            "range": "stddev: 0.00015464693575683214",
            "extra": "mean: 1.4478527796142988 msec\nrounds: 478"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 668.1234365217184,
            "unit": "iter/sec",
            "range": "stddev: 0.0001274529099550217",
            "extra": "mean: 1.4967294145615464 msec\nrounds: 489"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 677.6733956893908,
            "unit": "iter/sec",
            "range": "stddev: 0.00014261892083428275",
            "extra": "mean: 1.4756370935629093 msec\nrounds: 512"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 61.870176829332415,
            "unit": "iter/sec",
            "range": "stddev: 0.002858039374001913",
            "extra": "mean: 16.162876061571296 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 12.447307740675292,
            "unit": "iter/sec",
            "range": "stddev: 0.25152548822953147",
            "extra": "mean: 80.33865803222665 msec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 67.1416400023098,
            "unit": "iter/sec",
            "range": "stddev: 0.0019477320521404373",
            "extra": "mean: 14.893887012077723 msec\nrounds: 57"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 57.17998920893171,
            "unit": "iter/sec",
            "range": "stddev: 0.00392142903802475",
            "extra": "mean: 17.48863568942046 msec\nrounds: 57"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 62.86678859000204,
            "unit": "iter/sec",
            "range": "stddev: 0.005951231971304288",
            "extra": "mean: 15.906649956651899 msec\nrounds: 73"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 647.8523983274164,
            "unit": "iter/sec",
            "range": "stddev: 0.00013579908974750934",
            "extra": "mean: 1.5435614695287625 msec\nrounds: 484"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 734.3481189805383,
            "unit": "iter/sec",
            "range": "stddev: 0.0000980201075503927",
            "extra": "mean: 1.3617519731489938 msec\nrounds: 487"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 277.01710065371526,
            "unit": "iter/sec",
            "range": "stddev: 0.0019973948391323517",
            "extra": "mean: 3.6098854462058942 msec\nrounds: 234"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 683.2828652015594,
            "unit": "iter/sec",
            "range": "stddev: 0.00011515343765219637",
            "extra": "mean: 1.4635227237917245 msec\nrounds: 470"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 734.6558348851794,
            "unit": "iter/sec",
            "range": "stddev: 0.0001326539310768157",
            "extra": "mean: 1.3611815934958056 msec\nrounds: 545"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 88.30584633595164,
            "unit": "iter/sec",
            "range": "stddev: 0.003070060185103432",
            "extra": "mean: 11.324278532993048 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 101.00174867260743,
            "unit": "iter/sec",
            "range": "stddev: 0.00044534153832977456",
            "extra": "mean: 9.900818680292897 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 128.37773273553418,
            "unit": "iter/sec",
            "range": "stddev: 0.0004153779410134479",
            "extra": "mean: 7.789512859368375 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 130.11122299266356,
            "unit": "iter/sec",
            "range": "stddev: 0.0003384219787910307",
            "extra": "mean: 7.685732075982299 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 117.72744823728037,
            "unit": "iter/sec",
            "range": "stddev: 0.0004639932957161971",
            "extra": "mean: 8.494195830903378 msec\nrounds: 111"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 119.0797304164936,
            "unit": "iter/sec",
            "range": "stddev: 0.0004542252934793263",
            "extra": "mean: 8.397734832808213 msec\nrounds: 115"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 118.34906960833806,
            "unit": "iter/sec",
            "range": "stddev: 0.0005693324070245718",
            "extra": "mean: 8.449580578109986 msec\nrounds: 119"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 118.93627136495712,
            "unit": "iter/sec",
            "range": "stddev: 0.0004514816994132616",
            "extra": "mean: 8.407864047894105 msec\nrounds: 124"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 241.87872899431937,
            "unit": "iter/sec",
            "range": "stddev: 0.00039813147889168426",
            "extra": "mean: 4.1343031863851305 msec\nrounds: 11"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 7121.534263132158,
            "unit": "iter/sec",
            "range": "stddev: 0.000016770039637264974",
            "extra": "mean: 140.41917977941245 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7204.619327907327,
            "unit": "iter/sec",
            "range": "stddev: 0.000013431148671043217",
            "extra": "mean: 138.7998386155487 usec\nrounds: 57"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 44.798751695130655,
            "unit": "iter/sec",
            "range": "stddev: 0.008218966872919713",
            "extra": "mean: 22.322050551883876 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 88.59629732699989,
            "unit": "iter/sec",
            "range": "stddev: 0.00245846748662098",
            "extra": "mean: 11.287153415781047 msec\nrounds: 21"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 678.6298431255408,
            "unit": "iter/sec",
            "range": "stddev: 0.0002054716457801587",
            "extra": "mean: 1.47355735992148 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 677.9373308877074,
            "unit": "iter/sec",
            "range": "stddev: 0.0002132176688296769",
            "extra": "mean: 1.475062597143863 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 66.2222118856684,
            "unit": "iter/sec",
            "range": "stddev: 0.002097608125777206",
            "extra": "mean: 15.100673497987113 msec\nrounds: 28"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f73bcaa1446090e053ce187a34fa27742b347497",
          "message": "Add SonarQube workflow for CI analysis",
          "timestamp": "2026-03-13T16:02:25+09:00",
          "tree_id": "ba77a12c98e9007b8f3310abec579fd443d75b59",
          "url": "https://github.com/disnana/NanaSQLite/commit/f73bcaa1446090e053ce187a34fa27742b347497"
        },
        "date": 1773385650823,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 4206.343702730365,
            "unit": "iter/sec",
            "range": "stddev: 0.004303074902765319",
            "extra": "mean: 237.73616011237826 usec\nrounds: 5197"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 4352.362301959476,
            "unit": "iter/sec",
            "range": "stddev: 0.004018766354777711",
            "extra": "mean: 229.7602843287633 usec\nrounds: 6419"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 726.0684132467917,
            "unit": "iter/sec",
            "range": "stddev: 0.009908518261671738",
            "extra": "mean: 1.3772806828605262 msec\nrounds: 1675"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2292102.598343426,
            "unit": "iter/sec",
            "range": "stddev: 4.507802038203094e-8",
            "extra": "mean: 436.2806449950064 nsec\nrounds: 133015"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 87484.91847266223,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016465440285983664",
            "extra": "mean: 11.430541600292917 usec\nrounds: 8004"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 501.31103979095286,
            "unit": "iter/sec",
            "range": "stddev: 0.0001387467137264567",
            "extra": "mean: 1.9947695554779739 msec\nrounds: 326"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2744.793692423813,
            "unit": "iter/sec",
            "range": "stddev: 0.00001669679877928555",
            "extra": "mean: 364.3261068255158 usec\nrounds: 1461"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2281458.5244013285,
            "unit": "iter/sec",
            "range": "stddev: 1.8739732848077926e-7",
            "extra": "mean: 438.31609880456074 nsec\nrounds: 105675"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 117510.42835053644,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012025319504307963",
            "extra": "mean: 8.509883029419107 usec\nrounds: 9226"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 91868.34970257666,
            "unit": "iter/sec",
            "range": "stddev: 4.898351534538082e-7",
            "extra": "mean: 10.885141653654335 usec\nrounds: 352"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 72455.11385030458,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011818145218156018",
            "extra": "mean: 13.80164831520441 usec\nrounds: 18563"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 5817203.3159753345,
            "unit": "iter/sec",
            "range": "stddev: 1.4495128543086311e-8",
            "extra": "mean: 171.90391081134874 nsec\nrounds: 153398"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1386709.3799849034,
            "unit": "iter/sec",
            "range": "stddev: 9.226362789773968e-8",
            "extra": "mean: 721.1316332272063 nsec\nrounds: 3650"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 90470.21896177347,
            "unit": "iter/sec",
            "range": "stddev: 8.851005028291489e-7",
            "extra": "mean: 11.053361111268357 usec\nrounds: 339"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 70336.90817279568,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023697730244758793",
            "extra": "mean: 14.217286855192928 usec\nrounds: 14066"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 3636.1348030240442,
            "unit": "iter/sec",
            "range": "stddev: 0.005019414890687852",
            "extra": "mean: 275.0173066103972 usec\nrounds: 6204"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4931.964262626195,
            "unit": "iter/sec",
            "range": "stddev: 0.003941753825214706",
            "extra": "mean: 202.75897122326583 usec\nrounds: 9345"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 51676.1504109412,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033959732851443447",
            "extra": "mean: 19.351286658308698 usec\nrounds: 8857"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 5051.825239836895,
            "unit": "iter/sec",
            "range": "stddev: 0.009975131617722722",
            "extra": "mean: 197.94825682297085 usec\nrounds: 10742"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7391.9859129374545,
            "unit": "iter/sec",
            "range": "stddev: 0.000018951306851150326",
            "extra": "mean: 135.28164308995773 usec\nrounds: 975"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12440.051595788265,
            "unit": "iter/sec",
            "range": "stddev: 0.000005810929621605342",
            "extra": "mean: 80.38551868535356 usec\nrounds: 3853"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21899.62872029582,
            "unit": "iter/sec",
            "range": "stddev: 0.000004621595581979915",
            "extra": "mean: 45.66287459810835 usec\nrounds: 5345"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8342.075036773684,
            "unit": "iter/sec",
            "range": "stddev: 0.000006636802602519098",
            "extra": "mean: 119.87425138131488 usec\nrounds: 4235"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 9431.064955003723,
            "unit": "iter/sec",
            "range": "stddev: 0.0022212484753865243",
            "extra": "mean: 106.03256416651466 usec\nrounds: 7804"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2337.281770064714,
            "unit": "iter/sec",
            "range": "stddev: 0.004379328351280344",
            "extra": "mean: 427.8474306383318 usec\nrounds: 3543"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 833.9935606665134,
            "unit": "iter/sec",
            "range": "stddev: 0.03146701663602758",
            "extra": "mean: 1.1990500252793523 msec\nrounds: 2608"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2379.1529335886826,
            "unit": "iter/sec",
            "range": "stddev: 0.004301250018433062",
            "extra": "mean: 420.3176625941458 usec\nrounds: 3899"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 437.126268651598,
            "unit": "iter/sec",
            "range": "stddev: 0.0072406613681385784",
            "extra": "mean: 2.2876685107136128 msec\nrounds: 1202"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1389.1389166345905,
            "unit": "iter/sec",
            "range": "stddev: 0.0030853639512332534",
            "extra": "mean: 719.870408945607 usec\nrounds: 1270"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 14587.009876740685,
            "unit": "iter/sec",
            "range": "stddev: 0.000012960930468593058",
            "extra": "mean: 68.55414567138413 usec\nrounds: 1987"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28261.257935541413,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037067539420472206",
            "extra": "mean: 35.38412912407547 usec\nrounds: 5691"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2273.2347307239534,
            "unit": "iter/sec",
            "range": "stddev: 0.000033805039045624636",
            "extra": "mean: 439.9017780629859 usec\nrounds: 1074"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 114804.95249116368,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010205806101086851",
            "extra": "mean: 8.710425624512741 usec\nrounds: 19204"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 44811.45018123965,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018769850487133425",
            "extra": "mean: 22.315725020179123 usec\nrounds: 11822"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 57728.32553863373,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017352582741074813",
            "extra": "mean: 17.322518723165917 usec\nrounds: 15639"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 71173.96931218148,
            "unit": "iter/sec",
            "range": "stddev: 0.000001389026092218032",
            "extra": "mean: 14.05008052331359 usec\nrounds: 13861"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 97919.00251932883,
            "unit": "iter/sec",
            "range": "stddev: 0.000001950627936259077",
            "extra": "mean: 10.212522332451291 usec\nrounds: 14237"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1319.6400267518077,
            "unit": "iter/sec",
            "range": "stddev: 0.004366045937752781",
            "extra": "mean: 757.782410148185 usec\nrounds: 312"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 897.1593383719056,
            "unit": "iter/sec",
            "range": "stddev: 0.007483580603586509",
            "extra": "mean: 1.114629204902132 msec\nrounds: 2053"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 254582.96604998727,
            "unit": "iter/sec",
            "range": "stddev: 5.561889463692388e-7",
            "extra": "mean: 3.927992573563034 usec\nrounds: 18875"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4525.162177294481,
            "unit": "iter/sec",
            "range": "stddev: 0.003876998339847349",
            "extra": "mean: 220.98655491677502 usec\nrounds: 10096"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 158309.4820598162,
            "unit": "iter/sec",
            "range": "stddev: 7.767893295413364e-7",
            "extra": "mean: 6.316741025165863 usec\nrounds: 21497"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 9696.740215531314,
            "unit": "iter/sec",
            "range": "stddev: 0.0025197416678428837",
            "extra": "mean: 103.12744053906852 usec\nrounds: 15500"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2498.082178765901,
            "unit": "iter/sec",
            "range": "stddev: 0.004847501834188373",
            "extra": "mean: 400.3070869726225 usec\nrounds: 3715"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1935.191754500091,
            "unit": "iter/sec",
            "range": "stddev: 0.00542998554370037",
            "extra": "mean: 516.7446573057176 usec\nrounds: 2179"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 4248.295239551654,
            "unit": "iter/sec",
            "range": "stddev: 0.0038244496755900615",
            "extra": "mean: 235.38853672174054 usec\nrounds: 3895"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 355720.7012738068,
            "unit": "iter/sec",
            "range": "stddev: 6.345161239356979e-7",
            "extra": "mean: 2.81119427803634 usec\nrounds: 29509"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 7120.851944911552,
            "unit": "iter/sec",
            "range": "stddev: 0.0028191936667656954",
            "extra": "mean: 140.43263470947238 usec\nrounds: 8580"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 37336.692466402324,
            "unit": "iter/sec",
            "range": "stddev: 0.00000268214008877415",
            "extra": "mean: 26.783304410262286 usec\nrounds: 9718"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 8458.760889664261,
            "unit": "iter/sec",
            "range": "stddev: 0.002581744604097079",
            "extra": "mean: 118.22062510620172 usec\nrounds: 8639"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 4301.14670029941,
            "unit": "iter/sec",
            "range": "stddev: 0.004058173326527732",
            "extra": "mean: 232.496138746067 usec\nrounds: 6727"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 4473.528688242506,
            "unit": "iter/sec",
            "range": "stddev: 0.0037946788331497047",
            "extra": "mean: 223.53718276765207 usec\nrounds: 4852"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 4280.324356861524,
            "unit": "iter/sec",
            "range": "stddev: 0.003902220499678991",
            "extra": "mean: 233.6271545395763 usec\nrounds: 4663"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4404.0933558659735,
            "unit": "iter/sec",
            "range": "stddev: 0.0033274327423157097",
            "extra": "mean: 227.06149011761147 usec\nrounds: 1211"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1241834.763440151,
            "unit": "iter/sec",
            "range": "stddev: 1.5194862327403632e-7",
            "extra": "mean: 805.2601114417055 nsec\nrounds: 114890"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1236438.3563149087,
            "unit": "iter/sec",
            "range": "stddev: 1.608097716267741e-7",
            "extra": "mean: 808.7746509097376 nsec\nrounds: 128884"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1212556.4573134736,
            "unit": "iter/sec",
            "range": "stddev: 2.3878280213191445e-7",
            "extra": "mean: 824.7038675754436 nsec\nrounds: 145160"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1241921.8307321905,
            "unit": "iter/sec",
            "range": "stddev: 2.0100734391433267e-7",
            "extra": "mean: 805.2036571500136 nsec\nrounds: 179406"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 85085.62667620949,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020018598966326566",
            "extra": "mean: 11.752866366083975 usec\nrounds: 11422"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 59956.93574218139,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026296683648612195",
            "extra": "mean: 16.678637552460373 usec\nrounds: 8835"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 39615.53387009015,
            "unit": "iter/sec",
            "range": "stddev: 0.00000735727159703586",
            "extra": "mean: 25.24262334263285 usec\nrounds: 151"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 16050.589746989534,
            "unit": "iter/sec",
            "range": "stddev: 0.000010583255593730239",
            "extra": "mean: 62.303006666004976 usec\nrounds: 466"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 53.45366403730112,
            "unit": "iter/sec",
            "range": "stddev: 0.03012813248370519",
            "extra": "mean: 18.70779146780618 msec\nrounds: 195"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 26.804276946573356,
            "unit": "iter/sec",
            "range": "stddev: 0.21175851808005508",
            "extra": "mean: 37.30747902632156 msec\nrounds: 249"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 53.207321944983136,
            "unit": "iter/sec",
            "range": "stddev: 0.030304294111056375",
            "extra": "mean: 18.79440579689407 msec\nrounds: 218"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 52.008667042306826,
            "unit": "iter/sec",
            "range": "stddev: 0.030778935636144134",
            "extra": "mean: 19.22756449778924 msec\nrounds: 189"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21809.4251959392,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018185371504965488",
            "extra": "mean: 45.85173570673449 usec\nrounds: 12882"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17018.179025981182,
            "unit": "iter/sec",
            "range": "stddev: 0.000002299123961799885",
            "extra": "mean: 58.76069340164583 usec\nrounds: 8953"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21773.870204941202,
            "unit": "iter/sec",
            "range": "stddev: 0.000001556779077072774",
            "extra": "mean: 45.92660792903356 usec\nrounds: 14129"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4342.45336882359,
            "unit": "iter/sec",
            "range": "stddev: 0.000010818073173464182",
            "extra": "mean: 230.2845684376132 usec\nrounds: 2488"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4304.770837660514,
            "unit": "iter/sec",
            "range": "stddev: 0.004125695206481559",
            "extra": "mean: 232.30040290448156 usec\nrounds: 19766"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 422091.5228345648,
            "unit": "iter/sec",
            "range": "stddev: 6.110612644535878e-7",
            "extra": "mean: 2.3691544271831813 usec\nrounds: 78260"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 4176.463306154955,
            "unit": "iter/sec",
            "range": "stddev: 0.004010124419250905",
            "extra": "mean: 239.437037199938 usec\nrounds: 5541"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4188.260166564576,
            "unit": "iter/sec",
            "range": "stddev: 0.000026418757902781635",
            "extra": "mean: 238.76262701709163 usec\nrounds: 1100"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3642.0403838183997,
            "unit": "iter/sec",
            "range": "stddev: 0.000020078169251266166",
            "extra": "mean: 274.57136511802673 usec\nrounds: 1250"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5165.277719574587,
            "unit": "iter/sec",
            "range": "stddev: 0.00001489996158068249",
            "extra": "mean: 193.60043240469946 usec\nrounds: 2688"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5249.390346242426,
            "unit": "iter/sec",
            "range": "stddev: 0.00001240600888796715",
            "extra": "mean: 190.4983120022331 usec\nrounds: 2776"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21316.3442582925,
            "unit": "iter/sec",
            "range": "stddev: 0.000005321758467608507",
            "extra": "mean: 46.91235926211781 usec\nrounds: 11335"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21475.608055558005,
            "unit": "iter/sec",
            "range": "stddev: 0.0000037984804770644964",
            "extra": "mean: 46.564455703092165 usec\nrounds: 12659"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21138.06224427534,
            "unit": "iter/sec",
            "range": "stddev: 0.00006871376650362287",
            "extra": "mean: 47.30802608317716 usec\nrounds: 13203"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21337.960795608004,
            "unit": "iter/sec",
            "range": "stddev: 0.000003556320733785806",
            "extra": "mean: 46.864834441247545 usec\nrounds: 13136"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 216.91142432600236,
            "unit": "iter/sec",
            "range": "stddev: 0.009860917732351484",
            "extra": "mean: 4.610176725855949 msec\nrounds: 199"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3856.479611728394,
            "unit": "iter/sec",
            "range": "stddev: 0.0036589434407961596",
            "extra": "mean: 259.30384720789976 usec\nrounds: 4904"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 226034.68313799446,
            "unit": "iter/sec",
            "range": "stddev: 0.00001903606563433181",
            "extra": "mean: 4.424099815644215 usec\nrounds: 36734"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 975877.0397573377,
            "unit": "iter/sec",
            "range": "stddev: 4.273018992425683e-7",
            "extra": "mean: 1.0247192620175394 usec\nrounds: 72192"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 54.70063908827396,
            "unit": "iter/sec",
            "range": "stddev: 0.003294306948027077",
            "extra": "mean: 18.28132205889286 msec\nrounds: 85"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 83.58318975736152,
            "unit": "iter/sec",
            "range": "stddev: 0.0035228873033318142",
            "extra": "mean: 11.964128228450695 msec\nrounds: 52"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 157978.8774991748,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011182245486540387",
            "extra": "mean: 6.329960155624119 usec\nrounds: 25305"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 121467.14443394082,
            "unit": "iter/sec",
            "range": "stddev: 0.000001973433366900786",
            "extra": "mean: 8.232678924495866 usec\nrounds: 4551"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 70881.03202364,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020917376415350676",
            "extra": "mean: 14.108146727695548 usec\nrounds: 14799"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 82195.96358928893,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023333471653978718",
            "extra": "mean: 12.166047532415709 usec\nrounds: 12389"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 2344.563291891192,
            "unit": "iter/sec",
            "range": "stddev: 0.004948255382024564",
            "extra": "mean: 426.51866275419303 usec\nrounds: 2486"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 806.2993806172738,
            "unit": "iter/sec",
            "range": "stddev: 0.009334379590385463",
            "extra": "mean: 1.240234116556602 msec\nrounds: 1683"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4201.270266427403,
            "unit": "iter/sec",
            "range": "stddev: 0.00004553138989448182",
            "extra": "mean: 238.02324929939851 usec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4770.367220915059,
            "unit": "iter/sec",
            "range": "stddev: 0.000025917436633730843",
            "extra": "mean: 209.62746759109638 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1417.2187157447875,
            "unit": "iter/sec",
            "range": "stddev: 0.00030778629723039237",
            "extra": "mean: 705.6073906521002 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 193.10942896270814,
            "unit": "iter/sec",
            "range": "stddev: 0.004636826674318851",
            "extra": "mean: 5.17841104585894 msec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 10228.843674295691,
            "unit": "iter/sec",
            "range": "stddev: 0.000018611388722370805",
            "extra": "mean: 97.76276105508624 usec\nrounds: 3731"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7793.593748994295,
            "unit": "iter/sec",
            "range": "stddev: 0.000017060232310473703",
            "extra": "mean: 128.3105114542367 usec\nrounds: 3147"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 299.18923879782415,
            "unit": "iter/sec",
            "range": "stddev: 0.0002942145370172765",
            "extra": "mean: 3.34236620280232 msec\nrounds: 240"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7533.2334275646745,
            "unit": "iter/sec",
            "range": "stddev: 0.000018897662092365412",
            "extra": "mean: 132.74512327481105 usec\nrounds: 2654"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1737.9680475966402,
            "unit": "iter/sec",
            "range": "stddev: 0.00005621593875769461",
            "extra": "mean: 575.3845713002929 usec\nrounds: 1079"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 6954.993586791899,
            "unit": "iter/sec",
            "range": "stddev: 0.000026125739837998022",
            "extra": "mean: 143.78158477372023 usec\nrounds: 389"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 10371.326025214117,
            "unit": "iter/sec",
            "range": "stddev: 0.000012390322360488638",
            "extra": "mean: 96.41968612006438 usec\nrounds: 3547"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 8765.982933398996,
            "unit": "iter/sec",
            "range": "stddev: 0.000012363237807628729",
            "extra": "mean: 114.0773382286579 usec\nrounds: 2318"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6696.204781127257,
            "unit": "iter/sec",
            "range": "stddev: 0.000015463467030851883",
            "extra": "mean: 149.33832412330398 usec\nrounds: 416"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2773.02244646894,
            "unit": "iter/sec",
            "range": "stddev: 0.000044568935629877425",
            "extra": "mean: 360.6173477871993 usec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 5277.771772303964,
            "unit": "iter/sec",
            "range": "stddev: 0.000023095878040710467",
            "extra": "mean: 189.47389980894513 usec\nrounds: 48"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7796.336740238011,
            "unit": "iter/sec",
            "range": "stddev: 0.000017824564588106146",
            "extra": "mean: 128.26536786679017 usec\nrounds: 3447"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1199.1083686135269,
            "unit": "iter/sec",
            "range": "stddev: 0.0001176960832691087",
            "extra": "mean: 833.9529822114855 usec\nrounds: 50"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 268.6226766535486,
            "unit": "iter/sec",
            "range": "stddev: 0.00020049973761939477",
            "extra": "mean: 3.7226939008195963 msec\nrounds: 206"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.27597155155281,
            "unit": "iter/sec",
            "range": "stddev: 0.00467733162604938",
            "extra": "mean: 17.159731075703604 msec\nrounds: 53"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 46.78003097588413,
            "unit": "iter/sec",
            "range": "stddev: 0.003478180757842223",
            "extra": "mean: 21.37664253611795 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 18.901517919793715,
            "unit": "iter/sec",
            "range": "stddev: 0.0038150959427383237",
            "extra": "mean: 52.90580387476699 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 29.891340168964863,
            "unit": "iter/sec",
            "range": "stddev: 0.0060532759918920445",
            "extra": "mean: 33.45450536333815 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 45.8697880544765,
            "unit": "iter/sec",
            "range": "stddev: 0.0032654089824464033",
            "extra": "mean: 21.800841957507334 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 65.83816575605508,
            "unit": "iter/sec",
            "range": "stddev: 0.002224659157250878",
            "extra": "mean: 15.188758503771512 msec\nrounds: 74"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 7209.388919537798,
            "unit": "iter/sec",
            "range": "stddev: 0.00002190427268824841",
            "extra": "mean: 138.7080113392067 usec\nrounds: 3503"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1625.3772174573432,
            "unit": "iter/sec",
            "range": "stddev: 0.000059333383770343055",
            "extra": "mean: 615.2417969561237 usec\nrounds: 51"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4291.9966097644465,
            "unit": "iter/sec",
            "range": "stddev: 0.000022196383343402142",
            "extra": "mean: 232.99179634134939 usec\nrounds: 938"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 661.2437771493225,
            "unit": "iter/sec",
            "range": "stddev: 0.0001254880577138135",
            "extra": "mean: 1.5123015664677921 msec\nrounds: 483"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 455.3784625224889,
            "unit": "iter/sec",
            "range": "stddev: 0.00015950804114481454",
            "extra": "mean: 2.1959756165468955 msec\nrounds: 306"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 68.35764211440785,
            "unit": "iter/sec",
            "range": "stddev: 0.0022042243530930265",
            "extra": "mean: 14.628942267001165 msec\nrounds: 76"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 63.05017306966425,
            "unit": "iter/sec",
            "range": "stddev: 0.001720926067488522",
            "extra": "mean: 15.860384695456718 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.31127558732144,
            "unit": "iter/sec",
            "range": "stddev: 0.007034311611819857",
            "extra": "mean: 30.94894837244953 msec\nrounds: 19"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 57.91084925615528,
            "unit": "iter/sec",
            "range": "stddev: 0.005471307070806298",
            "extra": "mean: 17.26792151806876 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 62.86319262479387,
            "unit": "iter/sec",
            "range": "stddev: 0.0031646065008474585",
            "extra": "mean: 15.907559865255557 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 659.3663107971316,
            "unit": "iter/sec",
            "range": "stddev: 0.00016871723950489896",
            "extra": "mean: 1.5166076634868775 msec\nrounds: 473"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 65.2029227830672,
            "unit": "iter/sec",
            "range": "stddev: 0.002237509258751893",
            "extra": "mean: 15.336735798286853 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 66.51203560184602,
            "unit": "iter/sec",
            "range": "stddev: 0.002085718608628829",
            "extra": "mean: 15.034872876033964 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 645.5264156024139,
            "unit": "iter/sec",
            "range": "stddev: 0.00013457343200745246",
            "extra": "mean: 1.5491232826882642 msec\nrounds: 482"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 44.80041908560826,
            "unit": "iter/sec",
            "range": "stddev: 0.0036714104800004807",
            "extra": "mean: 22.32121976558119 msec\nrounds: 25"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 16.84153648589765,
            "unit": "iter/sec",
            "range": "stddev: 0.012366918077114455",
            "extra": "mean: 59.37700522973991 msec\nrounds: 13"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 18.088287850579572,
            "unit": "iter/sec",
            "range": "stddev: 0.003532834229929755",
            "extra": "mean: 55.28439221338236 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 18.24487124893884,
            "unit": "iter/sec",
            "range": "stddev: 0.0040920966677577275",
            "extra": "mean: 54.80992364131713 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 18.038263753278812,
            "unit": "iter/sec",
            "range": "stddev: 0.00378663540062842",
            "extra": "mean: 55.43770806756444 msec\nrounds: 13"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.64934838689183,
            "unit": "iter/sec",
            "range": "stddev: 0.0004217080408064887",
            "extra": "mean: 12.099308942145269 msec\nrounds: 70"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 82.93898830305842,
            "unit": "iter/sec",
            "range": "stddev: 0.0003677563098119342",
            "extra": "mean: 12.057055679845138 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.39972300838019,
            "unit": "iter/sec",
            "range": "stddev: 0.00044804465073312714",
            "extra": "mean: 12.135963125729177 msec\nrounds: 64"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 76.14219941409289,
            "unit": "iter/sec",
            "range": "stddev: 0.0005832229129633213",
            "extra": "mean: 13.133321701959053 msec\nrounds: 67"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 66.52857610506041,
            "unit": "iter/sec",
            "range": "stddev: 0.0024292387202875824",
            "extra": "mean: 15.031134867832176 msec\nrounds: 67"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 576.2234932263052,
            "unit": "iter/sec",
            "range": "stddev: 0.0001471828144867978",
            "extra": "mean: 1.735437745519448 msec\nrounds: 400"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 58.21745346617241,
            "unit": "iter/sec",
            "range": "stddev: 0.002549323940760883",
            "extra": "mean: 17.176979418741766 msec\nrounds: 41"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 60.15081235069356,
            "unit": "iter/sec",
            "range": "stddev: 0.002374269219358565",
            "extra": "mean: 16.624879381009215 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 60.03642982547051,
            "unit": "iter/sec",
            "range": "stddev: 0.002192725143332442",
            "extra": "mean: 16.656553411104888 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 38.05401156161809,
            "unit": "iter/sec",
            "range": "stddev: 0.046460180949983734",
            "extra": "mean: 26.27843843429681 msec\nrounds: 59"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 699.5723128814685,
            "unit": "iter/sec",
            "range": "stddev: 0.00014515380230570627",
            "extra": "mean: 1.4294447930351901 msec\nrounds: 529"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 648.0464377582188,
            "unit": "iter/sec",
            "range": "stddev: 0.00020204174439447626",
            "extra": "mean: 1.5430992930989498 msec\nrounds: 452"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 672.7617223416331,
            "unit": "iter/sec",
            "range": "stddev: 0.00017289189741951465",
            "extra": "mean: 1.4864103690670336 msec\nrounds: 422"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 58.813183227400074,
            "unit": "iter/sec",
            "range": "stddev: 0.004131762913932623",
            "extra": "mean: 17.002990573278762 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 50.30963200323432,
            "unit": "iter/sec",
            "range": "stddev: 0.007412646869289701",
            "extra": "mean: 19.87690945415207 msec\nrounds: 44"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 67.69956134673149,
            "unit": "iter/sec",
            "range": "stddev: 0.001936707602723798",
            "extra": "mean: 14.771144452153525 msec\nrounds: 57"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 57.73680151017731,
            "unit": "iter/sec",
            "range": "stddev: 0.004049391639666996",
            "extra": "mean: 17.319975714687438 msec\nrounds: 62"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 65.38110263112745,
            "unit": "iter/sec",
            "range": "stddev: 0.0025180396625917216",
            "extra": "mean: 15.294939359494796 msec\nrounds: 75"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 641.281543045682,
            "unit": "iter/sec",
            "range": "stddev: 0.00013294441818684336",
            "extra": "mean: 1.5593774853563256 msec\nrounds: 464"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 731.1740812848805,
            "unit": "iter/sec",
            "range": "stddev: 0.00009957826960461416",
            "extra": "mean: 1.367663358967424 msec\nrounds: 501"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 276.31681129888295,
            "unit": "iter/sec",
            "range": "stddev: 0.002010451221737854",
            "extra": "mean: 3.6190342357357776 msec\nrounds: 229"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 681.5599077337707,
            "unit": "iter/sec",
            "range": "stddev: 0.00011171122399737572",
            "extra": "mean: 1.4672224534524962 msec\nrounds: 495"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 729.4348286604135,
            "unit": "iter/sec",
            "range": "stddev: 0.0001223337306858604",
            "extra": "mean: 1.3709243933916233 msec\nrounds: 530"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 89.4019745049223,
            "unit": "iter/sec",
            "range": "stddev: 0.002751589169425997",
            "extra": "mean: 11.18543528303105 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 98.1910212338066,
            "unit": "iter/sec",
            "range": "stddev: 0.0013129268516952769",
            "extra": "mean: 10.184230568484054 msec\nrounds: 32"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 117.13467272009166,
            "unit": "iter/sec",
            "range": "stddev: 0.0008292696199465324",
            "extra": "mean: 8.537181833338353 msec\nrounds: 31"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 118.33872222999844,
            "unit": "iter/sec",
            "range": "stddev: 0.0006882897399750285",
            "extra": "mean: 8.450319398044874 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 116.22927550918311,
            "unit": "iter/sec",
            "range": "stddev: 0.0004014436795581839",
            "extra": "mean: 8.603684361097057 msec\nrounds: 108"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 117.56826665907505,
            "unit": "iter/sec",
            "range": "stddev: 0.00042206712328536546",
            "extra": "mean: 8.50569654905098 msec\nrounds: 127"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 116.01935129723431,
            "unit": "iter/sec",
            "range": "stddev: 0.0006182479548837217",
            "extra": "mean: 8.619251778421539 msec\nrounds: 116"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 125.25563092373446,
            "unit": "iter/sec",
            "range": "stddev: 0.0007428425754610906",
            "extra": "mean: 7.983673010348566 msec\nrounds: 121"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 259.25570622737445,
            "unit": "iter/sec",
            "range": "stddev: 0.000165735159019653",
            "extra": "mean: 3.857195718280439 msec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 6902.454484554215,
            "unit": "iter/sec",
            "range": "stddev: 0.000022717317737305924",
            "extra": "mean: 144.87600059337203 usec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7728.816513889555,
            "unit": "iter/sec",
            "range": "stddev: 0.000013434779315795758",
            "extra": "mean: 129.38591545068866 usec\nrounds: 59"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 47.636845854504536,
            "unit": "iter/sec",
            "range": "stddev: 0.0029439232911594427",
            "extra": "mean: 20.992153910740925 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 92.39438455386293,
            "unit": "iter/sec",
            "range": "stddev: 0.0018141698869488126",
            "extra": "mean: 10.823168581387458 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 688.2681645271989,
            "unit": "iter/sec",
            "range": "stddev: 0.0001946571140808544",
            "extra": "mean: 1.4529220608175928 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 677.5319728426035,
            "unit": "iter/sec",
            "range": "stddev: 0.00012448331941470125",
            "extra": "mean: 1.4759451067740363 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 65.70019995113105,
            "unit": "iter/sec",
            "range": "stddev: 0.004494785292899277",
            "extra": "mean: 15.220653829726809 msec\nrounds: 29"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "83683593+harumaki4649@users.noreply.github.com",
            "name": "harumaki4649",
            "username": "harumaki4649"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9aa4f7faa3e4a3bc66951a465c345241cde0027a",
          "message": "Merge pull request #138 from disnana/dev\n\nno message",
          "timestamp": "2026-03-13T18:09:57+09:00",
          "tree_id": "3a3e4e153b5b9d51c7fec7492142f68632419dad",
          "url": "https://github.com/disnana/NanaSQLite/commit/9aa4f7faa3e4a3bc66951a465c345241cde0027a"
        },
        "date": 1773394418011,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_single_write",
            "value": 1797.8028282069824,
            "unit": "iter/sec",
            "range": "stddev: 0.017877110489815277",
            "extra": "mean: 556.2345237810857 usec\nrounds: 4924"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_nested_write",
            "value": 515.952454853203,
            "unit": "iter/sec",
            "range": "stddev: 0.06836799408364418",
            "extra": "mean: 1.9381630818764426 msec\nrounds: 7239"
          },
          {
            "name": "tests/test_benchmark.py::TestWriteBenchmarks::test_batch_write_100",
            "value": 699.3820964904451,
            "unit": "iter/sec",
            "range": "stddev: 0.010344234826422568",
            "extra": "mean: 1.4298335702587748 msec\nrounds: 1662"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_cached",
            "value": 2460564.9154524985,
            "unit": "iter/sec",
            "range": "stddev: 2.5465196226036165e-8",
            "extra": "mean: 406.41073670519955 nsec\nrounds: 54272"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_single_read_uncached",
            "value": 87032.69373561583,
            "unit": "iter/sec",
            "range": "stddev: 0.000001681652066469558",
            "extra": "mean: 11.489935070121545 usec\nrounds: 8307"
          },
          {
            "name": "tests/test_benchmark.py::TestReadBenchmarks::test_bulk_load_1000",
            "value": 484.24263457566104,
            "unit": "iter/sec",
            "range": "stddev: 0.00015915280213081004",
            "extra": "mean: 2.0650804547110853 msec\nrounds: 226"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_keys_1000",
            "value": 2652.34024356816,
            "unit": "iter/sec",
            "range": "stddev: 0.00001766797731144136",
            "extra": "mean: 377.0255352513569 usec\nrounds: 1412"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_contains_check",
            "value": 2292840.395685215,
            "unit": "iter/sec",
            "range": "stddev: 1.2952376747577617e-7",
            "extra": "mean: 436.1402572467981 nsec\nrounds: 150399"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_len",
            "value": 116332.24902922055,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011311760294649741",
            "extra": "mean: 8.596068659764482 usec\nrounds: 9589"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_to_dict_1000",
            "value": 100876.28102527391,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010117622157388194",
            "extra": "mean: 9.913133095672473 usec\nrounds: 376"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_batch_get",
            "value": 71962.3167552062,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016532591220787701",
            "extra": "mean: 13.896161839837568 usec\nrounds: 17694"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_is_cached",
            "value": 3266835.2254921757,
            "unit": "iter/sec",
            "range": "stddev: 2.6448478314067686e-7",
            "extra": "mean: 306.1066539863031 nsec\nrounds: 198531"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_refresh",
            "value": 1444151.918692081,
            "unit": "iter/sec",
            "range": "stddev: 4.052894209004471e-7",
            "extra": "mean: 692.4479253579262 nsec\nrounds: 3435"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_copy",
            "value": 110445.98884569184,
            "unit": "iter/sec",
            "range": "stddev: 0.000002084513382464359",
            "extra": "mean: 9.05419934622648 usec\nrounds: 479"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_read_deep",
            "value": 69988.41094568153,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012326299055993309",
            "extra": "mean: 14.288079790468547 usec\nrounds: 11048"
          },
          {
            "name": "tests/test_benchmark.py::TestDictOperationsBenchmarks::test_nested_write_deep",
            "value": 4035.377655066042,
            "unit": "iter/sec",
            "range": "stddev: 0.004241508705343125",
            "extra": "mean: 247.80828102782223 usec\nrounds: 6949"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_insert_single",
            "value": 4844.222283446094,
            "unit": "iter/sec",
            "range": "stddev: 0.0036987532942157632",
            "extra": "mean: 206.4314850739297 usec\nrounds: 8805"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_sql_update_single",
            "value": 50530.791776805614,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032687869763746653",
            "extra": "mean: 19.789913532663363 usec\nrounds: 8412"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_upsert",
            "value": 9098.746674710355,
            "unit": "iter/sec",
            "range": "stddev: 0.0024684500379093324",
            "extra": "mean: 109.90524692587218 usec\nrounds: 9142"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_query_with_pagination",
            "value": 7373.994468209514,
            "unit": "iter/sec",
            "range": "stddev: 0.0000191312864141327",
            "extra": "mean: 135.61171008619033 usec\nrounds: 977"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_count_operation",
            "value": 12481.73542921487,
            "unit": "iter/sec",
            "range": "stddev: 0.000006614193286456338",
            "extra": "mean: 80.11706430336525 usec\nrounds: 3625"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_exists_check",
            "value": 21914.89054795993,
            "unit": "iter/sec",
            "range": "stddev: 0.000003810825489748327",
            "extra": "mean: 45.631074351548186 usec\nrounds: 6496"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_export_import_roundtrip",
            "value": 8125.48782072245,
            "unit": "iter/sec",
            "range": "stddev: 0.000010646633525078552",
            "extra": "mean: 123.06953404689104 usec\nrounds: 3966"
          },
          {
            "name": "tests/test_benchmark.py::TestWrapperFunctionsBenchmarks::test_transaction_context",
            "value": 7826.087115269473,
            "unit": "iter/sec",
            "range": "stddev: 0.0027681615745267472",
            "extra": "mean: 127.77777518587811 usec\nrounds: 8014"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_create_index",
            "value": 2074.1460784591577,
            "unit": "iter/sec",
            "range": "stddev: 0.005157661955224056",
            "extra": "mean: 482.1261194596671 usec\nrounds: 3766"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_table",
            "value": 2054.465491758509,
            "unit": "iter/sec",
            "range": "stddev: 0.005292044535867298",
            "extra": "mean: 486.7446077880117 usec\nrounds: 2774"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_drop_index",
            "value": 2201.7633171424627,
            "unit": "iter/sec",
            "range": "stddev: 0.004846246967549239",
            "extra": "mean: 454.1814245946473 usec\nrounds: 3719"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_alter_table_add_column",
            "value": 435.1496154594617,
            "unit": "iter/sec",
            "range": "stddev: 0.007229292702932565",
            "extra": "mean: 2.2980601716587277 msec\nrounds: 1182"
          },
          {
            "name": "tests/test_benchmark.py::TestDDLOperationsBenchmarks::test_sql_delete",
            "value": 1333.777591943659,
            "unit": "iter/sec",
            "range": "stddev: 0.00376864238637069",
            "extra": "mean: 749.7501877676182 usec\nrounds: 1051"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_query_simple",
            "value": 15329.411331897496,
            "unit": "iter/sec",
            "range": "stddev: 0.000007272563676680442",
            "extra": "mean: 65.23407705286088 usec\nrounds: 2147"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_one",
            "value": 28490.727175376458,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035656367432828237",
            "extra": "mean: 35.099139233773755 usec\nrounds: 6427"
          },
          {
            "name": "tests/test_benchmark.py::TestQueryOperationsBenchmarks::test_fetch_all_1000",
            "value": 2192.4656582125126,
            "unit": "iter/sec",
            "range": "stddev: 0.000029747360583358634",
            "extra": "mean: 456.10748622411097 usec\nrounds: 1079"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_table_exists",
            "value": 112141.42078243174,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014917511174616532",
            "extra": "mean: 8.91731166791728 usec\nrounds: 18941"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_tables",
            "value": 43498.20343104496,
            "unit": "iter/sec",
            "range": "stddev: 0.0000025987580629657",
            "extra": "mean: 22.9894552216447 usec\nrounds: 11861"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_get_table_schema",
            "value": 55840.244575101955,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024937979858354904",
            "extra": "mean: 17.9082310188498 usec\nrounds: 14799"
          },
          {
            "name": "tests/test_benchmark.py::TestSchemaOperationsBenchmarks::test_list_indexes",
            "value": 69958.06316383513,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020216365003142747",
            "extra": "mean: 14.294277954180851 usec\nrounds: 13832"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_fresh",
            "value": 96188.70751501902,
            "unit": "iter/sec",
            "range": "stddev: 0.000001970585546645738",
            "extra": "mean: 10.396230761743615 usec\nrounds: 13246"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_batch_delete",
            "value": 1297.8263361578922,
            "unit": "iter/sec",
            "range": "stddev: 0.004604868838740967",
            "extra": "mean: 770.5191150307655 usec\nrounds: 335"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_vacuum",
            "value": 947.8120503975761,
            "unit": "iter/sec",
            "range": "stddev: 0.007472101147871144",
            "extra": "mean: 1.055061496190656 msec\nrounds: 2053"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_db_size",
            "value": 259951.45723001764,
            "unit": "iter/sec",
            "range": "stddev: 9.237984484872042e-7",
            "extra": "mean: 3.8468720685614453 usec\nrounds: 28213"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_get_last_insert_rowid",
            "value": 4645.631892718795,
            "unit": "iter/sec",
            "range": "stddev: 0.003923866923955929",
            "extra": "mean: 215.25597014419563 usec\nrounds: 9298"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_pragma",
            "value": 159993.45868083762,
            "unit": "iter/sec",
            "range": "stddev: 5.230662832441803e-7",
            "extra": "mean: 6.250255530726705 usec\nrounds: 20923"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_raw",
            "value": 7756.9130928388295,
            "unit": "iter/sec",
            "range": "stddev: 0.0033427215833438167",
            "extra": "mean: 128.91726232219855 usec\nrounds: 14059"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_execute_many",
            "value": 2541.6977781966934,
            "unit": "iter/sec",
            "range": "stddev: 0.004774144664380783",
            "extra": "mean: 393.4378070352207 usec\nrounds: 2882"
          },
          {
            "name": "tests/test_benchmark.py::TestUtilityOperationsBenchmarks::test_import_from_dict_list",
            "value": 1893.8271828128995,
            "unit": "iter/sec",
            "range": "stddev: 0.0054010333494928725",
            "extra": "mean: 528.0312845202175 usec\nrounds: 2063"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_set_model",
            "value": 3924.5985037495175,
            "unit": "iter/sec",
            "range": "stddev: 0.004143018793735894",
            "extra": "mean: 254.80313439568693 usec\nrounds: 4189"
          },
          {
            "name": "tests/test_benchmark.py::TestPydanticOperationsBenchmarks::test_get_model",
            "value": 365205.94573643676,
            "unit": "iter/sec",
            "range": "stddev: 2.755473746501149e-7",
            "extra": "mean: 2.7381810501017525 usec\nrounds: 44372"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_commit",
            "value": 1727.7967550077078,
            "unit": "iter/sec",
            "range": "stddev: 0.03710125473633291",
            "extra": "mean: 578.7717780472037 usec\nrounds: 8767"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_begin_rollback",
            "value": 36883.451195717,
            "unit": "iter/sec",
            "range": "stddev: 0.000002444710642240788",
            "extra": "mean: 27.11243030630828 usec\nrounds: 9624"
          },
          {
            "name": "tests/test_benchmark.py::TestTransactionOperationsBenchmarks::test_context_manager_transaction",
            "value": 8712.596124973235,
            "unit": "iter/sec",
            "range": "stddev: 0.002499481216792466",
            "extra": "mean: 114.77635203744417 usec\nrounds: 7921"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[plaintext]",
            "value": 3645.1775568103385,
            "unit": "iter/sec",
            "range": "stddev: 0.005247847004927132",
            "extra": "mean: 274.33505896898913 usec\nrounds: 5765"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[aes-gcm]",
            "value": 1601.5728084107798,
            "unit": "iter/sec",
            "range": "stddev: 0.028575601007956954",
            "extra": "mean: 624.3862250585331 usec\nrounds: 5108"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[chacha20]",
            "value": 3923.541208719389,
            "unit": "iter/sec",
            "range": "stddev: 0.004314909747182479",
            "extra": "mean: 254.87179738998884 usec\nrounds: 4737"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_write_encryption[fernet]",
            "value": 4344.130013871413,
            "unit": "iter/sec",
            "range": "stddev: 0.0035202047957512963",
            "extra": "mean: 230.1956886204742 usec\nrounds: 1324"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[plaintext]",
            "value": 1222519.3268025655,
            "unit": "iter/sec",
            "range": "stddev: 1.4978054441166944e-7",
            "extra": "mean: 817.9829783267696 nsec\nrounds: 114653"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[aes-gcm]",
            "value": 1219138.913707085,
            "unit": "iter/sec",
            "range": "stddev: 5.371481017404959e-7",
            "extra": "mean: 820.2510712739532 nsec\nrounds: 159770"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[chacha20]",
            "value": 1216469.1540869218,
            "unit": "iter/sec",
            "range": "stddev: 6.172293092749708e-7",
            "extra": "mean: 822.0512592862226 nsec\nrounds: 146735"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption[fernet]",
            "value": 1233844.5956484014,
            "unit": "iter/sec",
            "range": "stddev: 3.304233811263795e-7",
            "extra": "mean: 810.4748389925775 nsec\nrounds: 198531"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[plaintext]",
            "value": 82088.44654828204,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017825134711833298",
            "extra": "mean: 12.181982264846845 usec\nrounds: 10912"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[aes-gcm]",
            "value": 45380.84238930549,
            "unit": "iter/sec",
            "range": "stddev: 0.000007028571087146742",
            "extra": "mean: 22.035730218962644 usec\nrounds: 8755"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[chacha20]",
            "value": 35953.11261162569,
            "unit": "iter/sec",
            "range": "stddev: 0.000006117409939338445",
            "extra": "mean: 27.81400349956468 usec\nrounds: 137"
          },
          {
            "name": "tests/test_benchmark.py::TestEncryptionBenchmarks::test_read_encryption_uncached[fernet]",
            "value": 16368.140858097237,
            "unit": "iter/sec",
            "range": "stddev: 0.000010453859013794648",
            "extra": "mean: 61.09429340017592 usec\nrounds: 3302"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[unbounded]",
            "value": 43.79212743739859,
            "unit": "iter/sec",
            "range": "stddev: 0.03781687656012919",
            "extra": "mean: 22.835154593243107 msec\nrounds: 192"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[lru]",
            "value": 48.26135688709509,
            "unit": "iter/sec",
            "range": "stddev: 0.03417566674147126",
            "extra": "mean: 20.720511492029694 msec\nrounds: 191"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[fifo]",
            "value": 49.3138883674584,
            "unit": "iter/sec",
            "range": "stddev: 0.03381929703723777",
            "extra": "mean: 20.278263043234027 msec\nrounds: 213"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_write_1000[ttl]",
            "value": 46.242515220499556,
            "unit": "iter/sec",
            "range": "stddev: 0.036138985403380106",
            "extra": "mean: 21.625121281393767 msec\nrounds: 242"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[unbounded]",
            "value": 21725.735658460875,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026407785250155673",
            "extra": "mean: 46.02836082149236 usec\nrounds: 14026"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[lru]",
            "value": 17126.255370973347,
            "unit": "iter/sec",
            "range": "stddev: 0.0000035104407245860018",
            "extra": "mean: 58.38988023586655 usec\nrounds: 9341"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[fifo]",
            "value": 21793.79586692072,
            "unit": "iter/sec",
            "range": "stddev: 0.000002631674293608351",
            "extra": "mean: 45.884618086096246 usec\nrounds: 14155"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_cache_read_hit[ttl]",
            "value": 4364.677767780604,
            "unit": "iter/sec",
            "range": "stddev: 0.000009504818856029843",
            "extra": "mean: 229.11198791852397 usec\nrounds: 2569"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_lru_eviction",
            "value": 4128.01541731281,
            "unit": "iter/sec",
            "range": "stddev: 0.004289574662894384",
            "extra": "mean: 242.24715726739316 usec\nrounds: 15939"
          },
          {
            "name": "tests/test_benchmark.py::TestCacheStrategyBenchmarks::test_ttl_expiry_check",
            "value": 423414.14459559845,
            "unit": "iter/sec",
            "range": "stddev: 3.270569582219617e-7",
            "extra": "mean: 2.361753882726561 usec\nrounds: 80835"
          },
          {
            "name": "tests/test_benchmark.py::TestMixedBenchmarks::test_aes_lru_write",
            "value": 3738.9113601784716,
            "unit": "iter/sec",
            "range": "stddev: 0.004500140618625694",
            "extra": "mean: 267.4575307268762 usec\nrounds: 6059"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[immediate]",
            "value": 4183.256800237132,
            "unit": "iter/sec",
            "range": "stddev: 0.00002482025633753907",
            "extra": "mean: 239.0481980315705 usec\nrounds: 1043"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[count]",
            "value": 3663.8711928828557,
            "unit": "iter/sec",
            "range": "stddev: 0.000023458687025459714",
            "extra": "mean: 272.93535917488595 usec\nrounds: 1318"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[time]",
            "value": 5130.1878649543905,
            "unit": "iter/sec",
            "range": "stddev: 0.00001719512234577941",
            "extra": "mean: 194.92463557353378 usec\nrounds: 2226"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_write_1000[manual]",
            "value": 5112.864028198991,
            "unit": "iter/sec",
            "range": "stddev: 0.000011876790653991772",
            "extra": "mean: 195.58509564985448 usec\nrounds: 2939"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[immediate]",
            "value": 21562.50287387794,
            "unit": "iter/sec",
            "range": "stddev: 0.000004176287956907673",
            "extra": "mean: 46.37680541304217 usec\nrounds: 13104"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[count]",
            "value": 21412.28834460427,
            "unit": "iter/sec",
            "range": "stddev: 0.000004691643207026616",
            "extra": "mean: 46.70215457153566 usec\nrounds: 12179"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[time]",
            "value": 21475.426842229084,
            "unit": "iter/sec",
            "range": "stddev: 0.00000835218473933806",
            "extra": "mean: 46.564848621942595 usec\nrounds: 12282"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_read_hit[manual]",
            "value": 21695.93530408706,
            "unit": "iter/sec",
            "range": "stddev: 0.000003440200655118414",
            "extra": "mean: 46.09158286951663 usec\nrounds: 13334"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_batch_write_1000",
            "value": 203.32830943582948,
            "unit": "iter/sec",
            "range": "stddev: 0.012421815261513298",
            "extra": "mean: 4.918154303130133 msec\nrounds: 211"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_sql_insert",
            "value": 3846.3312979808547,
            "unit": "iter/sec",
            "range": "stddev: 0.003539168266041554",
            "extra": "mean: 259.988004809922 usec\nrounds: 4218"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_upsert",
            "value": 224768.74697629825,
            "unit": "iter/sec",
            "range": "stddev: 0.000019023014284333093",
            "extra": "mean: 4.44901710514696 usec\nrounds: 37064"
          },
          {
            "name": "tests/test_benchmark.py::TestV2ArchitectureBenchmarks::test_v2_dlq_operations",
            "value": 928709.5667257034,
            "unit": "iter/sec",
            "range": "stddev: 6.050396322604542e-7",
            "extra": "mean: 1.0767628931891389 usec\nrounds: 60880"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_backup_1000",
            "value": 53.16249375419145,
            "unit": "iter/sec",
            "range": "stddev: 0.003883144498828693",
            "extra": "mean: 18.810253797041973 msec\nrounds: 49"
          },
          {
            "name": "tests/test_benchmark.py::TestBackupRestoreBenchmarks::test_restore_1000",
            "value": 98.69193704816126,
            "unit": "iter/sec",
            "range": "stddev: 0.002951137053586619",
            "extra": "mean: 10.132540001844365 msec\nrounds: 45"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_read",
            "value": 154433.6096953463,
            "unit": "iter/sec",
            "range": "stddev: 9.210981786583766e-7",
            "extra": "mean: 6.475274404145032 usec\nrounds: 20112"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_pragma_write",
            "value": 120862.14970696109,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015647001927099746",
            "extra": "mean: 8.273888909179352 usec\nrounds: 4491"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_get_table_schema",
            "value": 69048.00249005125,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016588394312989201",
            "extra": "mean: 14.48267819397215 usec\nrounds: 13477"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_list_indexes",
            "value": 80597.94777281077,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015581433543827603",
            "extra": "mean: 12.40726380302879 usec\nrounds: 12149"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_import_from_dict_list",
            "value": 670.3462669393508,
            "unit": "iter/sec",
            "range": "stddev: 0.05552546826237967",
            "extra": "mean: 1.4917663442294884 msec\nrounds: 2300"
          },
          {
            "name": "tests/test_benchmark.py::TestExtendedBenchmarks::test_batch_update_partial_100",
            "value": 451.83675929299585,
            "unit": "iter/sec",
            "range": "stddev: 0.023539284080146522",
            "extra": "mean: 2.213188678063143 msec\nrounds: 1626"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_single_write",
            "value": 4537.086577021346,
            "unit": "iter/sec",
            "range": "stddev: 0.00003406933308098544",
            "extra": "mean: 220.40575665111345 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_nested_write",
            "value": 4941.617949427707,
            "unit": "iter/sec",
            "range": "stddev: 0.00002215004321638703",
            "extra": "mean: 202.3628718840579 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_100",
            "value": 1377.3182250166237,
            "unit": "iter/sec",
            "range": "stddev: 0.0003390452402854682",
            "extra": "mean: 726.0486224873198 usec\nrounds: 45"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncWriteBenchmarks::test_async_batch_write_1000",
            "value": 192.70646811578052,
            "unit": "iter/sec",
            "range": "stddev: 0.004545969230878907",
            "extra": "mean: 5.189239415665006 msec\nrounds: 43"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_single_read",
            "value": 8974.339152528082,
            "unit": "iter/sec",
            "range": "stddev: 0.000015248085239459148",
            "extra": "mean: 111.42881754343982 usec\nrounds: 3668"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_batch_get",
            "value": 7041.532038704244,
            "unit": "iter/sec",
            "range": "stddev: 0.00001722991075893781",
            "extra": "mean: 142.01454946216737 usec\nrounds: 3275"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_bulk_load_1000",
            "value": 301.7829348925088,
            "unit": "iter/sec",
            "range": "stddev: 0.0003034126167294633",
            "extra": "mean: 3.313639985495492 msec\nrounds: 190"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncReadBenchmarks::test_async_get_fresh",
            "value": 7739.377906447746,
            "unit": "iter/sec",
            "range": "stddev: 0.00001483527135018766",
            "extra": "mean: 129.20935146052125 usec\nrounds: 2527"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_keys_1000",
            "value": 1679.763653260296,
            "unit": "iter/sec",
            "range": "stddev: 0.00004682755638534914",
            "extra": "mean: 595.3218466532923 usec\nrounds: 873"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_values_1000",
            "value": 7054.621172891462,
            "unit": "iter/sec",
            "range": "stddev: 0.00001593579344023623",
            "extra": "mean: 141.75105586713343 usec\nrounds: 399"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_contains_check",
            "value": 10379.688918412618,
            "unit": "iter/sec",
            "range": "stddev: 0.000013043268547493381",
            "extra": "mean: 96.34200098483603 usec\nrounds: 3288"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_len",
            "value": 7842.284325488052,
            "unit": "iter/sec",
            "range": "stddev: 0.000017867751257413046",
            "extra": "mean: 127.51386694179398 usec\nrounds: 2932"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_to_dict_1000",
            "value": 6534.888129507824,
            "unit": "iter/sec",
            "range": "stddev: 0.00001552978654724509",
            "extra": "mean: 153.02480779809696 usec\nrounds: 328"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_pop",
            "value": 2710.590021999177,
            "unit": "iter/sec",
            "range": "stddev: 0.00003140932504611683",
            "extra": "mean: 368.92336793243885 usec\nrounds: 5"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_setdefault",
            "value": 5059.850433101266,
            "unit": "iter/sec",
            "range": "stddev: 0.0000320300033398",
            "extra": "mean: 197.63430030620162 usec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_get_100",
            "value": 7129.002003919447,
            "unit": "iter/sec",
            "range": "stddev: 0.00001990660757797462",
            "extra": "mean: 140.27208849853193 usec\nrounds: 3186"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDictOperationsBenchmarks::test_async_batch_delete_100",
            "value": 1153.8561961344801,
            "unit": "iter/sec",
            "range": "stddev: 0.0001118106453228716",
            "extra": "mean: 866.6591238579713 usec\nrounds: 40"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_10",
            "value": 266.4331813432368,
            "unit": "iter/sec",
            "range": "stddev: 0.00033423544066666245",
            "extra": "mean: 3.7532862647154075 msec\nrounds: 211"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_reads_100",
            "value": 58.70812099842364,
            "unit": "iter/sec",
            "range": "stddev: 0.004595161144845105",
            "extra": "mean: 17.0334185968386 msec\nrounds: 52"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_10",
            "value": 48.28052368842646,
            "unit": "iter/sec",
            "range": "stddev: 0.0030670190286260224",
            "extra": "mean: 20.712285692122983 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_writes_100",
            "value": 18.980593981017115,
            "unit": "iter/sec",
            "range": "stddev: 0.00538598625012342",
            "extra": "mean: 52.68539019380114 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncConcurrencyBenchmarks::test_async_concurrent_mixed_50",
            "value": 30.055234132950147,
            "unit": "iter/sec",
            "range": "stddev: 0.005663052631472205",
            "extra": "mean: 33.27207485978891 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_create_table",
            "value": 45.56198842181864,
            "unit": "iter/sec",
            "range": "stddev: 0.00867210040833903",
            "extra": "mean: 21.948120234390863 msec\nrounds: 26"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_insert",
            "value": 60.01200052659604,
            "unit": "iter/sec",
            "range": "stddev: 0.010501753797205485",
            "extra": "mean: 16.66333385364851 msec\nrounds: 80"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_update",
            "value": 6629.614675466028,
            "unit": "iter/sec",
            "range": "stddev: 0.000021974612233521672",
            "extra": "mean: 150.83832906619196 usec\nrounds: 3720"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_sql_delete",
            "value": 1607.2099182356305,
            "unit": "iter/sec",
            "range": "stddev: 0.00008621703630204896",
            "extra": "mean: 622.1962598997549 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_query_simple",
            "value": 4211.043581806038,
            "unit": "iter/sec",
            "range": "stddev: 0.00002340335027273287",
            "extra": "mean: 237.47082654773158 usec\nrounds: 940"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_one",
            "value": 669.5091478988934,
            "unit": "iter/sec",
            "range": "stddev: 0.0001229479666962024",
            "extra": "mean: 1.4936315704397456 msec\nrounds: 465"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_fetch_all_1000",
            "value": 457.87808180625046,
            "unit": "iter/sec",
            "range": "stddev: 0.00017412262996582186",
            "extra": "mean: 2.1839874842996885 msec\nrounds: 336"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSQLOperationsBenchmarks::test_async_execute_raw",
            "value": 65.72108636930628,
            "unit": "iter/sec",
            "range": "stddev: 0.0032894943360707073",
            "extra": "mean: 15.215816646436783 msec\nrounds: 74"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_batch_delete_100",
            "value": 62.313299467863835,
            "unit": "iter/sec",
            "range": "stddev: 0.0024811245219778745",
            "extra": "mean: 16.04793853863763 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_update_dict",
            "value": 32.93301519542818,
            "unit": "iter/sec",
            "range": "stddev: 0.00399633705743438",
            "extra": "mean: 30.36466579406375 msec\nrounds: 19"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBatchOperationsBenchmarks::test_async_clear",
            "value": 63.809226137458985,
            "unit": "iter/sec",
            "range": "stddev: 0.00153320608471866",
            "extra": "mean: 15.671714899751048 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_set_model",
            "value": 66.70789929040977,
            "unit": "iter/sec",
            "range": "stddev: 0.0025602940559161457",
            "extra": "mean: 14.990728394047396 msec\nrounds: 23"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncPydanticOperationsBenchmarks::test_async_get_model",
            "value": 664.9386945808267,
            "unit": "iter/sec",
            "range": "stddev: 0.00011883798558979805",
            "extra": "mean: 1.503898040751552 msec\nrounds: 485"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[aes-gcm]",
            "value": 66.90701674077866,
            "unit": "iter/sec",
            "range": "stddev: 0.00275489290539901",
            "extra": "mean: 14.94611550047661 msec\nrounds: 28"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_write_encryption[chacha20]",
            "value": 64.66755591517447,
            "unit": "iter/sec",
            "range": "stddev: 0.002598657323932831",
            "extra": "mean: 15.463704880260464 msec\nrounds: 35"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncEncryptionBenchmarks::test_async_read_encryption_uncached",
            "value": 650.4212344851035,
            "unit": "iter/sec",
            "range": "stddev: 0.0001641710720435728",
            "extra": "mean: 1.5374651794565648 msec\nrounds: 424"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncMixedBenchmarks::test_async_aes_concurrent_writes",
            "value": 47.24363610038863,
            "unit": "iter/sec",
            "range": "stddev: 0.0026462438377638136",
            "extra": "mean: 21.166872039126854 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[unbounded]",
            "value": 22.575140177247945,
            "unit": "iter/sec",
            "range": "stddev: 0.0019459550866468007",
            "extra": "mean: 44.296513427980244 msec\nrounds: 14"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[lru]",
            "value": 21.122907837496673,
            "unit": "iter/sec",
            "range": "stddev: 0.011123781785659589",
            "extra": "mean: 47.341966726041086 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[fifo]",
            "value": 21.67658907483601,
            "unit": "iter/sec",
            "range": "stddev: 0.004846930101648006",
            "extra": "mean: 46.13271933825066 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_write_100[ttl]",
            "value": 21.704757303762708,
            "unit": "iter/sec",
            "range": "stddev: 0.002468287371431776",
            "extra": "mean: 46.07284873103102 msec\nrounds: 15"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[unbounded]",
            "value": 82.04521076804238,
            "unit": "iter/sec",
            "range": "stddev: 0.00046708519430916783",
            "extra": "mean: 12.188401865737083 msec\nrounds: 65"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[lru]",
            "value": 83.59763341519181,
            "unit": "iter/sec",
            "range": "stddev: 0.0005524054255562598",
            "extra": "mean: 11.962061115216626 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[fifo]",
            "value": 82.0401117720201,
            "unit": "iter/sec",
            "range": "stddev: 0.0003727488219187864",
            "extra": "mean: 12.18915940508325 msec\nrounds: 71"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_cache_read_hit[ttl]",
            "value": 77.3155419391389,
            "unit": "iter/sec",
            "range": "stddev: 0.00047742198334537063",
            "extra": "mean: 12.934010095760282 msec\nrounds: 66"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_lru_eviction",
            "value": 68.84780481316118,
            "unit": "iter/sec",
            "range": "stddev: 0.001967104842441529",
            "extra": "mean: 14.524791352662513 msec\nrounds: 77"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncCacheStrategyBenchmarks::test_async_ttl_expiry_check",
            "value": 576.1296915296867,
            "unit": "iter/sec",
            "range": "stddev: 0.0001426446047828698",
            "extra": "mean: 1.73572029822815 msec\nrounds: 431"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_create_index",
            "value": 59.26558249864502,
            "unit": "iter/sec",
            "range": "stddev: 0.004594071057291403",
            "extra": "mean: 16.87319955090061 msec\nrounds: 47"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_table",
            "value": 61.93612168320863,
            "unit": "iter/sec",
            "range": "stddev: 0.0021926832999391477",
            "extra": "mean: 16.14566706509019 msec\nrounds: 30"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_drop_index",
            "value": 58.19641446303068,
            "unit": "iter/sec",
            "range": "stddev: 0.0049471135949149024",
            "extra": "mean: 17.18318919175426 msec\nrounds: 46"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncDDLOperationsBenchmarks::test_async_sql_delete",
            "value": 32.38545390495508,
            "unit": "iter/sec",
            "range": "stddev: 0.01160740994719423",
            "extra": "mean: 30.878060345697264 msec\nrounds: 38"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_table_exists",
            "value": 406.47353558921526,
            "unit": "iter/sec",
            "range": "stddev: 0.0017134332518556046",
            "extra": "mean: 2.4601847659046774 msec\nrounds: 441"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncSchemaOperationsBenchmarks::test_async_list_tables",
            "value": 651.9365761748257,
            "unit": "iter/sec",
            "range": "stddev: 0.00010707786038275498",
            "extra": "mean: 1.5338915418235965 msec\nrounds: 452"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_get_fresh",
            "value": 685.029663379603,
            "unit": "iter/sec",
            "range": "stddev: 0.00013737108097350932",
            "extra": "mean: 1.4597907995202524 msec\nrounds: 425"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_batch_delete",
            "value": 63.69252589441975,
            "unit": "iter/sec",
            "range": "stddev: 0.0026332388285819383",
            "extra": "mean: 15.700429304023132 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_vacuum",
            "value": 32.31824970160204,
            "unit": "iter/sec",
            "range": "stddev: 0.015777449383073034",
            "extra": "mean: 30.942269746446982 msec\nrounds: 36"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_raw",
            "value": 60.31205759933476,
            "unit": "iter/sec",
            "range": "stddev: 0.008270282639514537",
            "extra": "mean: 16.580432500632014 msec\nrounds: 24"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_execute_many",
            "value": 56.04127164079715,
            "unit": "iter/sec",
            "range": "stddev: 0.006046473858890485",
            "extra": "mean: 17.843991949533425 msec\nrounds: 75"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_transaction_context",
            "value": 66.30365448521343,
            "unit": "iter/sec",
            "range": "stddev: 0.0039801664946206355",
            "extra": "mean: 15.082124926055362 msec\nrounds: 69"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_count",
            "value": 655.2201484776447,
            "unit": "iter/sec",
            "range": "stddev: 0.00013905483179085156",
            "extra": "mean: 1.5262045929500578 msec\nrounds: 357"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_refresh_all",
            "value": 730.4179447967323,
            "unit": "iter/sec",
            "range": "stddev: 0.00012147291784445058",
            "extra": "mean: 1.369079178741001 msec\nrounds: 538"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_load_all",
            "value": 262.3268238156683,
            "unit": "iter/sec",
            "range": "stddev: 0.0021089587968966712",
            "extra": "mean: 3.812038683099672 msec\nrounds: 230"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_copy",
            "value": 685.2401943613896,
            "unit": "iter/sec",
            "range": "stddev: 0.00014836257224161412",
            "extra": "mean: 1.4593422981148256 msec\nrounds: 523"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncUtilityOperationsBenchmarks::test_async_is_cached",
            "value": 735.5634755436788,
            "unit": "iter/sec",
            "range": "stddev: 0.00010766506865664548",
            "extra": "mean: 1.3595019780731603 msec\nrounds: 548"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[immediate]",
            "value": 84.37966944447464,
            "unit": "iter/sec",
            "range": "stddev: 0.0032099024517506904",
            "extra": "mean: 11.851195988128893 msec\nrounds: 16"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[count]",
            "value": 101.7204187694344,
            "unit": "iter/sec",
            "range": "stddev: 0.0005796850833463099",
            "extra": "mean: 9.830867903391745 msec\nrounds: 33"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[time]",
            "value": 118.41729544454722,
            "unit": "iter/sec",
            "range": "stddev: 0.000848863142279351",
            "extra": "mean: 8.444712372849983 msec\nrounds: 29"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_write_1000[manual]",
            "value": 115.02164392550196,
            "unit": "iter/sec",
            "range": "stddev: 0.0008898069950030331",
            "extra": "mean: 8.69401589015444 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[immediate]",
            "value": 116.3196932592178,
            "unit": "iter/sec",
            "range": "stddev: 0.0004899679209054973",
            "extra": "mean: 8.596996535844584 msec\nrounds: 108"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[count]",
            "value": 116.63984618983704,
            "unit": "iter/sec",
            "range": "stddev: 0.0005279750115544847",
            "extra": "mean: 8.573399508538884 msec\nrounds: 106"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[time]",
            "value": 117.39635144243489,
            "unit": "iter/sec",
            "range": "stddev: 0.00042512556966272784",
            "extra": "mean: 8.518152291047548 msec\nrounds: 121"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_read_hit[manual]",
            "value": 117.8477500067568,
            "unit": "iter/sec",
            "range": "stddev: 0.0005536789094250559",
            "extra": "mean: 8.485524754971266 msec\nrounds: 125"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_batch_write_1000",
            "value": 249.88566729991882,
            "unit": "iter/sec",
            "range": "stddev: 0.00034328588017532426",
            "extra": "mean: 4.0018301601899235 msec\nrounds: 37"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_upsert",
            "value": 7091.487899588439,
            "unit": "iter/sec",
            "range": "stddev: 0.00001787323646769612",
            "extra": "mean: 141.0141304842438 usec\nrounds: 54"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncV2ArchitectureBenchmarks::test_async_v2_dlq_ops",
            "value": 7354.8685529240975,
            "unit": "iter/sec",
            "range": "stddev: 0.000010527154312550992",
            "extra": "mean: 135.9643605870328 usec\nrounds: 42"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_backup_1000",
            "value": 47.23329318394617,
            "unit": "iter/sec",
            "range": "stddev: 0.0035749521926837042",
            "extra": "mean: 21.17150705765068 msec\nrounds: 56"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncBackupRestoreBenchmarks::test_async_restore_1000",
            "value": 85.70688450751251,
            "unit": "iter/sec",
            "range": "stddev: 0.0020831933437175693",
            "extra": "mean: 11.667674140136858 msec\nrounds: 22"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_pragma_read",
            "value": 668.1676182863898,
            "unit": "iter/sec",
            "range": "stddev: 0.00029463808056611406",
            "extra": "mean: 1.4966304451638066 msec\nrounds: 34"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_get_table_schema",
            "value": 689.1041688387654,
            "unit": "iter/sec",
            "range": "stddev: 0.00016615686057681425",
            "extra": "mean: 1.4511594113341912 msec\nrounds: 27"
          },
          {
            "name": "tests/test_async_benchmark.py::TestAsyncExtendedBenchmarks::test_async_alter_table_add_column",
            "value": 68.75549403569602,
            "unit": "iter/sec",
            "range": "stddev: 0.002112538775130249",
            "extra": "mean: 14.544292263841877 msec\nrounds: 30"
          }
        ]
      }
    ]
  }
}