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

1. Open [Google Business Profile](https://business.google.com/) for Knight Group.
2. Or run account discovery once when quota resets (script prints `accounts/...` and `locations/...`).
3. Paste the two `KNIGHTGROUP_*` lines into `accounts.env`.
4. Run: `npm run reviews:sync-google`
5. Commit `data/google-reviews.json` when the feed updates (or let the weekly growth script refresh it).

The homepage carousel (`JS/kg-google-reviews.js`) loads `data/google-reviews.json` when reviews exist; otherwise it keeps the static HTML cards.
