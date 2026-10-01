These audit tools apply only to historical import; production scraper and workflows do not import them. Use merged scraper checkout c4c7efeaa19939b0e4d5a25c4b831162887c8792 and its documented Python dependencies.

From this data repo, run `PYTHONPATH=/path/to/scraper python -m unittest discover -s docs/backfill-provenance/2026-10-01-official-history/tools -v`. Tests verify every manifest archive byte-for-byte, official same-second differing quotes in stable source order, identical-repeat removal, and unchanged continuous price-run compression for nonconflicting captures.
