"""History-only price-run dedup retaining every differing same-second quote."""
from collections import defaultdict
from boc_currency_price import PRICE_FIELDS, parse_publish_date


def dedup_history_rows(rows):
    prices_at_time = defaultdict(set)
    distinct = []
    seen = set()
    for row in rows:
        prices = tuple(row[field] for field in PRICE_FIELDS)
        stamp = row['publish_date']
        prices_at_time[stamp].add(prices)
        identity = (stamp, prices)
        if identity not in seen:
            distinct.append(row)
            seen.add(identity)
    ordered = sorted(distinct, key=lambda row: parse_publish_date(row['publish_date'])[0])
    result = []
    last_prices = object()
    for row in ordered:
        prices = tuple(row[field] for field in PRICE_FIELDS)
        if len(prices_at_time[row['publish_date']]) > 1 or prices != last_prices:
            result.append(row)
            last_prices = prices
    return result
