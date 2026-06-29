# LawHelpCA Geocoding Results

Live validation on 2026-06-29 against the current `geocode_address` implementation.

## Summary

- LawHelpCA directory count observed live: `413 Organization(s) Found`
- The sequential live geocoding run hit Nominatim rate limiting (`429 Too Many Requests`), so many resources returned `None` even with valid-looking addresses.
- A second real failure mode was bad source data. Example: `3137 Castro Valey Blvd #210, Castro Valley CA 94546` contains `Valey` instead of `Valley`, and all fallback queries returned no results.
- Failed geocoding attempts are now logged to `failed_geocoding_attempts.log`.

## First 15 Live Results

```text
Access, Inc. | 2612 Daniel Ave, San Diego CA 92111 | None
Affordable Housing Advocates | 427 C Street Suite 304, San Diego CA 92101 | None
AIDS Legal Referral Panel - San Francisco Office | 1663 Mission Street Suite 720, San Francisco CA 94103 | None
Alameda County Lawyer Referral Service | Oakland CA 94607 | None
Alameda County Public Defender: Clean Slate Clinic | 545 4th Street Suite 400, Oakland CA 94612 | None
Alameda County Self-Help | 2233 Shore Line Drive, Alameda CA 94501 | None
Alameda Small Claims Court | 1225 Fallon Street, Oakland CA 94601 | None
All for the Family Legal Clinic, Inc. | 3137 Castro Valey Blvd #210, Castro Valley CA 94546 | None
Alliance for Children's Rights | 4525 Wilshire Blvd Ste. 150, Los Angeles CA 90010 | None
Al Otro Lado, Inc. | 511 E. San Ysidro Blvd. #333, San Ysidro CA 92173 | None
Alpine County Self Help Center | 14777 State Route 89, Markleeville CA 96120 | None
Alpine Small Claims Court | 14777 State Route 89, Markleeville CA 96120 | None
Amador County Office of the Family Law Facilitator and Self-Help Center | 500 Argonaut Lane, Jackson CA 95642 | None
Amador County Self-Help Legal Services | 500 Argonaut Lane, Jackson CA 95642 | None
Arab Resource and Organizing Center | 522 Valencia St, San Francisco CA 94110 | None
```

## Isolated Successful Lookups Before Throttling

```text
Alliance for Children's Rights | 4525 Wilshire Blvd Ste. 150, Los Angeles CA 90010 | (34.0618378, -118.3280802)
Al Otro Lado, Inc. | 511 E. San Ysidro Blvd. #333, San Ysidro CA 92173 | (32.5499049, -117.0360386)
```

## Why `geocode_address` Returns `None`

1. Nominatim responds with HTTP `429 Too Many Requests` during bulk sequential lookups.
2. Some LawHelpCA source addresses are partial or malformed, so all fallback queries return an empty JSON list.
3. The current function intentionally logs failures and returns `None` instead of raising.

## Failed Geocoding Log Samples

```json
{"timestamp": "2026-06-29T21:05:14Z", "address": "2612 Daniel Ave, San Diego CA 92111", "attempted_queries": ["2612 Daniel Ave, San Diego CA 92111", "2612 Daniel Ave, San Diego, CA 92111", "2612 Daniel Ave, San Diego, CA 92111, USA", "2612 Daniel Ave, San Diego, California 92111", "2612 Daniel Ave, San Diego, California, USA"], "error": "429 Client Error: Too many requests for url: https://nominatim.openstreetmap.org/search?q=2612+Daniel+Ave%2C+San+Diego%2C+California%2C+USA&format=json&limit=1"}
{"timestamp": "2026-06-29T21:06:10Z", "address": "3137 Castro Valey Blvd #210, Castro Valley CA 94546", "attempted_queries": ["3137 Castro Valey Blvd #210, Castro Valley CA 94546", "3137 Castro Valey Blvd #210, Castro Valley, CA 94546", "3137 Castro Valey Blvd #210, Castro Valley, CA 94546, USA", "3137 Castro Valey Blvd #210, Castro Valley, California 94546", "3137 Castro Valey Blvd #210, Castro Valley, California, USA"], "error": ""}
{"timestamp": "2026-06-29T21:08:35Z", "address": "4525 Wilshire Blvd Ste. 150, Los Angeles CA 90010", "attempted_queries": ["4525 Wilshire Blvd Ste. 150, Los Angeles CA 90010", "4525 Wilshire Blvd, Los Angeles CA 90010", "4525 Wilshire Blvd Ste. 150, Los Angeles, CA 90010", "4525 Wilshire Blvd Ste. 150, Los Angeles, CA 90010, USA", "4525 Wilshire Blvd Ste. 150, Los Angeles, California 90010", "4525 Wilshire Blvd Ste. 150, Los Angeles, California, USA"], "error": "429 Client Error: Too many requests for url: https://nominatim.openstreetmap.org/search?q=4525+Wilshire+Blvd+Ste.+150%2C+Los+Angeles%2C+California%2C+USA&format=json&limit=1"}
```
