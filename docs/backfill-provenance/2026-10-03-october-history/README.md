# October official historical backfill

45 currencies × October 1–3: 135/135 source queries verified and published in 45 batches. October 1 and 2 are complete historical queries. October 3 consists of observations captured at the individual times in completion/completion-summary.json; it is not a completed day. The last official quote in these observations is 2026-10-03 10:30 Asia/Shanghai.

810 pages, 15,513 raw rows, 15,114 distinct source rows, and 6,987 compressed archive rows. The authoritative algorithm preserves price recurrence intervals and selects the earliest quote of each consecutive identical five-price run. No same-second conflicting prices were found.

85 October 1–2 files were safely corrected. All 45 October 3 quote files retain their original bytes. Each batch retains its source JSON, metadata, TSV, transfer hashes, merge plan, and 135-file backup manifest; every changed file has its original bytes in the corresponding before directory. All 6,075 local batch backup files were rehashed and matched their manifests.

All 135 CDN files were freshly fetched after archive publication, with HTTP 200 and exact full-byte SHA matches. All 45 batch Pages deployments passed. The completion audit records the archive commit it verifies; the final status-only commit changes this provenance directory. The 1,080 completed September archive blobs were freshly rehashed and matched the completed September audit. No September, API, scraper, cron, or workflow changes were made.

The separate realtime Fetch workflow remains failing. The previously observed five new currency API history endpoints remain outside this publication scope. Neither issue is described as resolved by this backfill.

See completion/ for full per-file evidence, observations, supplementary USD/AED/MUR rechecks, batch checks, and verification scripts. Supplementary rechecks do not increase the 135 unique currency/date count.
