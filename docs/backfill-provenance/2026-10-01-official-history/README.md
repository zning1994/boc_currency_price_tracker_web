# Partial official-history backfill

40/1080 approved original-40-currency pairs complete; 1040 pending for 2026-09-04 through 2026-09-30. This is a partial checkpoint.

|Currency|Date|Pages|Raw rows|Unique timestamps|Archived price runs|
|---|---|---|---|---|---|
|AED|2026-09-04|15|289|287|178|
|AED|2026-09-05|3|55|52|19|
|AED|2026-09-06|1|6|3|1|
|AED|2026-09-07|11|218|214|129|
|AED|2026-09-08|13|255|251|155|
|AED|2026-09-09|13|245|242|148|
|AED|2026-09-10|13|244|241|136|
|AED|2026-09-11|13|247|244|133|
|AED|2026-09-12|2|38|35|18|
|AED|2026-09-13|1|9|3|1|
|AED|2026-09-14|11|215|212|135|
|AED|2026-09-15|13|255|252|155|
|AED|2026-09-16|14|262|259|146|
|EUR|2026-09-04|15|290|287|223|
|EUR|2026-09-05|3|55|52|32|
|EUR|2026-09-06|1|6|3|1|
|EUR|2026-09-07|11|218|214|164|
|EUR|2026-09-08|13|255|251|186|
|EUR|2026-09-09|13|245|242|184|
|EUR|2026-09-10|13|244|241|202|
|EUR|2026-09-11|13|245|242|198|
|EUR|2026-09-12|2|37|34|24|
|EUR|2026-09-13|1|9|3|1|
|EUR|2026-09-14|11|216|213|183|
|EUR|2026-09-15|13|255|252|208|
|EUR|2026-09-16|14|262|259|191|
|GBP|2026-09-05|3|55|52|32|
|USD|2026-09-04|15|290|287|92|
|USD|2026-09-05|3|55|52|2|
|USD|2026-09-06|1|6|3|1|
|USD|2026-09-07|11|218|214|83|
|USD|2026-09-08|13|255|251|71|
|USD|2026-09-09|13|245|242|78|
|USD|2026-09-10|13|244|241|117|
|USD|2026-09-11|13|253|250|124|
|USD|2026-09-12|2|38|35|2|
|USD|2026-09-13|1|9|3|1|
|USD|2026-09-14|11|216|213|122|
|USD|2026-09-15|13|255|252|127|
|USD|2026-09-16|14|262|259|93|

Source: https://www.boc.cn/sourcedb/whpjSearch/index.html . Raw captures preserve each returned page, original seven-cell table strings, source timestamps and capture time. No verification credentials are retained. Complete returned pages do not establish that BOC retains every originally published quote. Weekend queries can contain only a few timestamps through 10:30:00.

`manifest.json` records raw and archive SHA-256 hashes, coverage bounds, page counts and storage contract. Published daily files follow existing bare-array schema and continuous five-price-run dedup. No interpolation or current-price substitution is used. Existing files and October 1 data are untouched. New-currency research samples are excluded.

Offline validation checks complete sequential pages, 20 rows on non-final pages, currency/date/price/timestamp consistency, descending chronology, and absence of conflicting quotes at a timestamp. Three regression tests cover valid captures, malformed capture rejection, and idempotent missing-only import that refuses differing existing files and preserves current-day data. All archive hashes match the manifest; git diff --check passes. No production configuration changes. The data repository has no PR functional CI trigger.
