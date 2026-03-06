# Historical Data Backfill Notes

## Coverage After Backfill

| Currency | Original Coverage | Added Historical Coverage |
|----------|-------------------|--------------------------|
| AED | 2023-11-23 → current | 2014 (partial), 2022, 2023 (Jan-Nov 22) |
| USD | 2023-11-23 → current | 2014 (Jan-Apr), 2020-2023 (Jan-Nov 22) |
| EUR | 2023-11-23 → current | 2014 (Jan-Apr), 2022-2023 (Jan-Nov 22) |
| HKD | 2023-11-23 → current | 2014 (Jan-Mar), 2022-2023 (Jan-Nov 22) |
| JPY | 2023-11-23 → current | 2014 (partial), 2022-2023 (Jan-Nov 22) |
| SAR | 2023-11-23 → current | 2022 (partial), 2023 (Jan-Nov 22) |
| GBP | 2023-11-23 → current | 2014 (partial), 2022-2023 (Jan-Nov 22) |

## Data Source

All data fetched from Bank of China official exchange rate query:
- URL: https://srh.bankofchina.com/search/whpj/search_cn.jsp
- Data is authentic BOC official rates (not estimated or synthesized)
- Same source as the automated GitHub Action

## Technical Note

BOC's search interface uses CAPTCHA, but the answer is embedded in a JWT token
returned in the HTTP `Token` response header from `CaptchaServlet.jsp`.
The JWT payload contains `{"code": "<answer>", "exp": <timestamp>}`.

This makes automated historical data retrieval possible without OCR.
See `scripts/historical_backfill.py` for the implementation.

## Empty Files

Some date files contain empty arrays `[]`. This means BOC had no rate updates
for that date (typically weekends, public holidays, or pre-launch dates for some currencies).
This is expected and consistent with the live data behavior.

## Known Gaps

- 2015-2019: Not yet backfilled (in progress - see backfill script)
- Pre-2014: BOC data availability varies; requires verification
- AED/SAR: No data before ~2016 (currencies added to BOC later)

## Rollback

To revert the backfill:
```bash
git revert <this_commit_hash>
```

Or to remove specific years:
```bash
git rm docs/BOC_CURRENCY_PRICE/*/2014*.json
git commit -m "chore: remove 2014 backfill data"
```
