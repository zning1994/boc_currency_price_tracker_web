# Partial official-history backfill

This checkpoint fills four previously absent currency/day files in the approved original-40-currency scope for 2026-09-04 through 2026-09-30. It does not fill the entire gap: 4 of 1080 pairs are captured and 1076 remain pending.

| Currency | Date | Pages | Raw rows | Unique timestamps | Archived price runs |
| --- | --- | --- | --- | --- | --- |
| USD | 2026-09-04 | 15 | 290 | 287 | 92 |
| USD | 2026-09-05 | 3 | 55 | 52 | 2 |
| EUR | 2026-09-05 | 3 | 55 | 52 | 32 |
| GBP | 2026-09-05 | 3 | 55 | 52 | 32 |

Source: https://www.boc.cn/sourcedb/whpjSearch/index.html . Captures preserve the visible seven-column official table, each returned page, original quote timestamps, and capture time. No verification credentials are included. Complete returned pages do not establish that the source retains every originally published quote. Weekend queries returned records only through 10:30:00; this is recorded source behavior, not synthetic coverage.

`manifest.json` records source and archive SHA-256 hashes, page counts, timestamp bounds and schema contract. `raw/` retains repeated rows before deduplication. Published daily JSON follows the existing scraper schema and continuous five-price-run deduplication, so unchanged quotes can collapse to one archive row. No interpolation or current-price substitution is used. New currencies remain separate research samples and are excluded from this checkpoint.

Offline validation checked complete sequential pages, 20 rows per non-final page, currency and date consistency, descending timestamps, valid prices, and absence of conflicting prices at one timestamp. Missing-only import refuses to overwrite differing existing files. Three local regression tests passed, including malformed captures and idempotent import that preserves current-day data. Archive bytes were checked against manifest hashes. Only the four listed historical paths and this provenance directory are added; no production configuration is changed.

The data repository has no pull-request CI workflow; its normal fetch and Pages workflows run after main updates. This draft is a review checkpoint, not authorization to merge or publish.
