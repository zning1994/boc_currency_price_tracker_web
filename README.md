# BOC currency price archive

This repo is a **pure data CDN** for Bank of China exchange-rate
snapshots. It has no source code — only the JSON archive committed by a
scheduled workflow that runs every 30 minutes.

For everything else you probably want, go to one of these:

- **Public site / API docs / charts** → <https://bocurrencyprice.techina.science>
- **JSON API** → <https://api-bocurrencyprice.techina.science>
- **Scraper code (private)** → <https://github.com/zning1994/boc_currency_price_tracker_new>
- **Worker code (private)** → <https://github.com/zning1994/boc_currency_price_tracker_api>
- **Portal code (private)** → <https://github.com/zning1994/boc_currency_price_tracker_portal>

## What lives in this repo

```
docs/
├── BOC_CURRENCY_PRICE/<CCY>/<YYYYMMDD>.json   # 40 currencies × ~880 days
└── CNAME                                       # data-bocurrencyprice.techina.science
.github/workflows/main.yml                      # cron */30 — fetch + commit
```

The git history is the immutable archive — every 30-minute cron tick
that finds a price change becomes a `chore: update currency price …`
commit. Don't `git rebase` or `git push --force` here; consumers point
at specific dates.

## Direct CDN URLs

```
https://data-bocurrencyprice.techina.science/BOC_CURRENCY_PRICE/USD/20260425.json
```

The legacy URL on `bocurrencyprice.techina.science/BOC_CURRENCY_PRICE/...`
is preserved transparently via a Pages Function reverse proxy in the
portal repo, so existing consumers still work without any change.

## Schema

See the [scraper README](https://github.com/zning1994/boc_currency_price_tracker_new/blob/main/README.md).
