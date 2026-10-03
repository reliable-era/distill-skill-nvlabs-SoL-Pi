# CI triage notes (teammate)

I read logs/ci.log. The key error, quoted exactly:

> FAILED tests/test_parse.py::test_date - ValueError: time data '2026-09-30T12:00:00Z' does not match format '%Y-%m-%dT%H:%M:%S%z'

So `parse_date` is broken on the `Z` suffix. The fix is in `parse_date`.
