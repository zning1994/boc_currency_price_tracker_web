#!/usr/bin/env python3
"""
BOC Currency Price Historical Data Backfill Script
===================================================

Purpose:
    Backfills historical exchange rate data from Bank of China (BOC)
    for dates not covered by the automated GitHub Action.

Usage:
    # Backfill from 2014-01-01 to 2023-11-22 (default)
    python3 historical_backfill.py

    # Custom date range
    python3 historical_backfill.py --start 2020-01-01 --end 2023-11-22

    # Single currency
    python3 historical_backfill.py --currency USD

    # Adjust parallel workers (default: 4)
    python3 historical_backfill.py --workers 3

Requirements:
    pip install requests

Data Format:
    Output files match the existing docs/BOC_CURRENCY_PRICE/<CURRENCY>/<YYYYMMDD>.json format.
    Each file contains an array of exchange rate records:
    [
        {
            "currency_name": "USD",
            "spot_exchange_buying_price": 695.09,
            "cash_buying_price": 689.44,
            "spot_selling_price": 698.04,
            "cash_selling_price": 698.04,
            "bank_of_china_conversion_price": 696.14,
            "publish_date": "2020.01.02 22:40:12"
        },
        ...
    ]

Technical Notes:
    - BOC website requires CAPTCHA for historical searches.
    - The CAPTCHA answer is embedded in a JWT token returned in the HTTP
      'Token' response header from CaptchaServlet.jsp (no OCR needed).
    - JWT payload: {"code": "<captcha_answer>", "exp": <timestamp>}
    - Token expires in ~60 seconds, so a fresh token is needed per request.
    - Session can be reused; only the captcha token needs refreshing.

Rollback:
    To remove the backfilled data:
    git revert <commit_hash>
    # or
    git rm docs/BOC_CURRENCY_PRICE/*/2014*.json  # etc. by year prefix
"""

import argparse
import requests
import base64
import json
import re
import time
import threading
from datetime import date, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DOCS_DIR = REPO_ROOT / 'docs' / 'BOC_CURRENCY_PRICE'
GAPS_FILE = SCRIPT_DIR / 'backfill_gaps.json'

# Currency mapping
CURRENCIES = {
    'AED': '阿联酋迪拉姆',
    'USD': '美元',
    'EUR': '欧元',
    'HKD': '港币',
    'JPY': '日元',
    'SAR': '沙特里亚尔',
    'GBP': '英镑',
}

DEFAULT_START = date(2014, 1, 1)
DEFAULT_END = date(2023, 11, 22)
DELAY = 0.2
TIMEOUT = 20
MAX_RETRIES = 2

# Thread-safe globals
_lock = threading.Lock()
_stats = {'success': 0, 'empty': 0, 'error': 0, 'skipped': 0}
_gaps = []


def _log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)


def _add_stat(key):
    with _lock:
        _stats[key] = _stats.get(key, 0) + 1


def _add_gap(date_str, currency, reason):
    with _lock:
        _gaps.append({'date': date_str, 'currency': currency, 'reason': reason})


def _init_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    s.get('https://srh.bankofchina.com/search/whpj/search_cn.jsp', timeout=TIMEOUT)
    return s


def _get_captcha(session):
    """
    Fetch CAPTCHA image and extract the answer from JWT token.
    The server embeds the answer in the 'Token' response header as a signed JWT.
    JWT payload: {"code": "<answer>", "exp": <unix_timestamp>}
    """
    r = session.get('https://srh.bankofchina.com/search/whpj/CaptchaServlet.jsp', timeout=TIMEOUT)
    jwt = r.headers.get('Token', '')
    if not jwt:
        raise ValueError('No Token header from CaptchaServlet')
    payload_b64 = jwt.split('.')[1]
    payload_b64 += '=' * (4 - len(payload_b64) % 4 if len(payload_b64) % 4 else 0)
    payload = json.loads(base64.b64decode(payload_b64))
    return payload['code'], jwt


def _query_boc(session, code, jwt, date_str, cn):
    r = session.post(
        'https://srh.bankofchina.com/search/whpj/search_cn.jsp',
        data={'searchDate': date_str, 'pjname': cn, 'token': jwt, 'captcha': code, 'page': '1'},
        headers={'Referer': 'https://srh.bankofchina.com/search/whpj/search_cn.jsp'},
        timeout=TIMEOUT
    )
    return r.text


def _parse_records(html, currency_code):
    if '验证码过期' in html or '验证码错误' in html:
        return None, 'captcha_error'
    records = []
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 6:
            continue
        clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        if not clean[0]:
            continue
        try:
            def f(s):
                return float(s) if s and s.strip() else None
            boc_conv = f(clean[5])
            pub = clean[6].replace('/', '.') if len(clean) > 6 else ''
            if pub and boc_conv is not None:
                records.append({
                    'currency_name': currency_code,
                    'spot_exchange_buying_price': f(clean[1]),
                    'cash_buying_price': f(clean[2]),
                    'spot_selling_price': f(clean[3]),
                    'cash_selling_price': f(clean[4]),
                    'bank_of_china_conversion_price': boc_conv,
                    'publish_date': pub,
                })
        except Exception:
            pass
    return records, 'ok' if records else 'empty'


def _save_records(currency_code, date_obj, records):
    dir_path = DOCS_DIR / currency_code
    dir_path.mkdir(parents=True, exist_ok=True)
    fp = dir_path / f"{date_obj.strftime('%Y%m%d')}.json"
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)


def _file_exists(currency_code, date_obj):
    return (DOCS_DIR / currency_code / f"{date_obj.strftime('%Y%m%d')}.json").exists()


def _process_currency(currency_code, currency_cn, date_list):
    """Process all dates for one currency. Runs in a thread."""
    session = _init_session()
    req_count = 0
    total = len(date_list)

    for i, date_obj in enumerate(date_list):
        date_str = date_obj.strftime('%Y-%m-%d')

        if _file_exists(currency_code, date_obj):
            _add_stat('skipped')
            continue

        for attempt in range(MAX_RETRIES):
            try:
                req_count += 1
                if req_count % 80 == 0:
                    session = _init_session()

                captcha_code, jwt_token = _get_captcha(session)
                html = _query_boc(session, captcha_code, jwt_token, date_str, currency_cn)
                records, status = _parse_records(html, currency_code)

                if status == 'captcha_error':
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(1)
                        session = _init_session()
                        continue
                    _add_stat('error')
                    _add_gap(date_str, currency_code, 'captcha_error')
                    break

                _save_records(currency_code, date_obj, records or [])
                if records:
                    _add_stat('success')
                else:
                    _add_stat('empty')
                    _add_gap(date_str, currency_code, 'no_boc_data')
                break

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                    session = _init_session()
                else:
                    _add_stat('error')
                    _add_gap(date_str, currency_code, str(e)[:100])

        if (i + 1) % 200 == 0 or i == total - 1:
            pct = (i + 1) / total * 100
            _log(f"  {currency_code}: {pct:.0f}% ({i + 1}/{total}) at {date_str}")

        time.sleep(DELAY)


def main():
    parser = argparse.ArgumentParser(description='BOC Historical Data Backfill')
    parser.add_argument('--start', default=str(DEFAULT_START), help='Start date YYYY-MM-DD')
    parser.add_argument('--end', default=str(DEFAULT_END), help='End date YYYY-MM-DD')
    parser.add_argument('--currency', default=None, help='Single currency code (e.g. USD)')
    parser.add_argument('--workers', type=int, default=4, help='Parallel workers')
    args = parser.parse_args()

    start_date = date.fromisoformat(args.start)
    end_date = date.fromisoformat(args.end)
    currencies = {args.currency: CURRENCIES[args.currency]} if args.currency else CURRENCIES

    # Build date list
    date_list = []
    d = start_date
    while d <= end_date:
        date_list.append(d)
        d += timedelta(days=1)

    total_days = len(date_list)
    _log(f"=== BOC Backfill: {start_date} → {end_date} ({total_days} days, {len(currencies)} currencies) ===")
    _log(f"Workers: {args.workers} | Output: {DOCS_DIR}")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_process_currency, code, cn, date_list): code
            for code, cn in currencies.items()
        }
        for future in as_completed(futures):
            code = futures[future]
            try:
                future.result()
                _log(f"✓ {code} complete")
            except Exception as e:
                _log(f"✗ {code} FAILED: {e}")

    # Save gaps report
    GAPS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GAPS_FILE, 'w') as f:
        json.dump({
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'date_range': {'start': str(start_date), 'end': str(end_date)},
            'currencies': list(currencies.keys()),
            'stats': _stats,
            'gaps': _gaps,
        }, f, indent=2)

    _log(f"=== Done: success={_stats['success']} empty={_stats['empty']} "
         f"error={_stats['error']} skip={_stats['skipped']} ===")
    _log(f"Gaps ({len(_gaps)} total) saved to {GAPS_FILE}")


if __name__ == '__main__':
    main()
