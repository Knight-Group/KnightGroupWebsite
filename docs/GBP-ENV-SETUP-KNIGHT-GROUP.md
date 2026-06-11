# Knight Group GBP API setup

The review sync script (`npm run reviews:sync-google`) can pull reviews **automatically** once these variables exist in `C:\Users\nknig\.copilot-secrets\accounts.env`:

```env
KNIGHTGROUP_GBP_ACCOUNT_NAME=accounts/XXXXXXXX
KNIGHTGROUP_GBP_LOCATION_NAME=locations/XXXXXXXX
```

Shared OAuth (already present):

- `GBP_OAUTH_CLIENT_ID`
- `GBP_OAUTH_CLIENT_SECRET`
- `GBP_REFRESH_TOKEN`

## Why discovery is blocked

Google returns **429 quota-blocked** on the account-list API when called too often. The script cannot auto-discover account/location IDs in that state.

## How to get the IDs (one time)

### Location ID (confirmed 2026-06-11)

Knight Group → GBP **Advanced settings** → **Business Profile ID** (for Support):

```
15551195498878135337
```

Map to:

```env
KNIGHTGROUP_GBP_LOCATION_NAME=locations/15551195498878135337
```

### Account ID

Still required for review sync. Options:

1. Run `npm run reviews:sync-google:dry-run` when Google lifts API quota (prints `accounts/...`).
2. Ask Google Support for the **Account ID** when contacting them (give them the Business Profile ID above).
3. After enabling `mybusiness.googleapis.com` in GCP, try `KNIGHTGROUP_GBP_ACCOUNT_NAME=accounts/-` (wildcard) — the reviews endpoint accepted that path shape in testing.

Paste both `KNIGHTGROUP_*` lines into `C:\Users\nknig\.copilot-secrets\accounts.env`.
4. Run: `npm run reviews:sync-google`
5. Commit `data/google-reviews.json` when the feed updates (or let the weekly growth script refresh it).

The homepage carousel (`JS/kg-google-reviews.js`) loads `data/google-reviews.json` when reviews exist; otherwise it keeps the static HTML cards.
