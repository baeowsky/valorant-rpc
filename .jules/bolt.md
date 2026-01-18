## 2025-10-26 - [Bolt Journal Init]
**Learning:** Initializing the Bolt journal.
**Action:** Proceed with optimizations.

## 2025-10-26 - [Payload Reduction & Parallelization]
**Learning:** `valorant-api.com` returns ~1.5MB for `language=all` but only ~100KB for specific languages. Parallelizing large requests is limited by bandwidth, but parallelizing small requests (after filtering) is efficient.
**Action:** Always check API documentation for response filtering to reduce payload size before parallelizing.
