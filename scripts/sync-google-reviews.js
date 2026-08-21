'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const OAUTH_TOKEN_URL = 'https://oauth2.googleapis.com/token';
const ACCOUNTS_API = 'https://mybusinessaccountmanagement.googleapis.com/v1/accounts';
const LOCATIONS_API_ROOT = 'https://mybusinessbusinessinformation.googleapis.com/v1';
const REVIEWS_API_ROOT = 'https://mybusiness.googleapis.com/v4';
const ROOT = path.resolve(__dirname, '..');
const OUTPUT_PATH = path.join(ROOT, 'data', 'google-reviews.json');
const ENTITY_PATH = path.join(ROOT, 'seo', 'knight-group-business-entity.json');
const HOME_REVIEWS_PATH = path.join(ROOT, 'seo', 'knight-group-reviews-home.json');
const DEFAULT_LOCATION_TITLE = 'Knight Group';
const DEFAULT_BUSINESS_NAME = 'Knight Group Handyman Services';
const KNIGHT_LOGICS_LOCATION = 'locations/1248159491432428151';
const WEEKDAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
const CANONICAL_REGULAR_HOURS = {
    periods: WEEKDAYS.map((day) => ({
        openDay: day,
        openTime: { hours: 8 },
        closeDay: day,
        closeTime: { hours: 17 }
    }))
};

const STAR_MAP = {
    ONE: 1,
    TWO: 2,
    THREE: 3,
    FOUR: 4,
    FIVE: 5
};

const AVATAR_COLORS = ['#1d4ed8', '#156f43', '#b42318', '#8a5a00', '#17623b', '#274690', '#7c3aed', '#0f766e'];

function loadEnvFile(filePath) {
    if (!fs.existsSync(filePath)) {
        return;
    }

    const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) {
            continue;
        }

        const idx = trimmed.indexOf('=');
        if (idx === -1) {
            continue;
        }

        const key = trimmed.slice(0, idx).trim();
        let value = trimmed.slice(idx + 1).trim();

        if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
            value = value.slice(1, -1);
        }

        if (!(key in process.env)) {
            process.env[key] = value;
        }
    }
}

function isUsableId(value) {
    if (!value) return false;
    const text = String(value).trim();
    if (!text) return false;
    if (/x{4,}/i.test(text) || text.toUpperCase().includes('XXXXXXXX')) return false;
    return true;
}

function loadDefaultEnvs() {
    const root = path.resolve(__dirname, '..');
    loadEnvFile(path.join(root, '.env.local'));

    const secretPath = process.env.KL_ACCOUNTS_ENV_PATH || 'C:/Users/nknig/.copilot-secrets/accounts.env';
    loadEnvFile(secretPath);

    if (isUsableId(process.env.KNIGHTGROUP_GBP_ACCOUNT_NAME) && !isUsableId(process.env.GBP_ACCOUNT_NAME)) {
        process.env.GBP_ACCOUNT_NAME = process.env.KNIGHTGROUP_GBP_ACCOUNT_NAME;
    }
    if (isUsableId(process.env.KNIGHTGROUP_GBP_LOCATION_NAME) && !isUsableId(process.env.GBP_LOCATION_NAME)) {
        process.env.GBP_LOCATION_NAME = process.env.KNIGHTGROUP_GBP_LOCATION_NAME;
    }
    if (process.env.KNIGHTGROUP_GBP_LOCATION_TITLE && !process.env.GBP_LOCATION_TITLE) {
        process.env.GBP_LOCATION_TITLE = process.env.KNIGHTGROUP_GBP_LOCATION_TITLE;
    }
}

function requireEnv(name) {
    const value = process.env[name];
    if (!value) {
        throw new Error(`Missing required environment variable: ${name}`);
    }
    return value;
}

function normalizeAccountName(input) {
    if (!input) return null;
    return input.startsWith('accounts/') ? input : `accounts/${input}`;
}

function normalizeLocationName(input) {
    if (!input) return null;
    return input.startsWith('locations/') ? input : `locations/${input}`;
}

async function apiGet(url, accessToken) {
    const response = await fetch(url, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
            Accept: 'application/json'
        }
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(`API request failed (${response.status}) ${url} :: ${JSON.stringify(payload)}`);
    }

    return payload;
}

async function getAccessToken() {
    const clientId = requireEnv('GBP_OAUTH_CLIENT_ID');
    const clientSecret = requireEnv('GBP_OAUTH_CLIENT_SECRET');
    const refreshToken = requireEnv('GBP_REFRESH_TOKEN');

    const body = new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        grant_type: 'refresh_token'
    });

    const response = await fetch(OAUTH_TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok || !payload.access_token) {
        throw new Error(`OAuth token refresh failed (${response.status}): ${JSON.stringify(payload)}`);
    }

    return payload.access_token;
}

async function listAllLocations(accessToken, accountName) {
    const locations = [];
    let pageToken = '';

    do {
        const query = new URLSearchParams({
            readMask: 'name,title,metadata'
        });

        if (pageToken) {
            query.set('pageToken', pageToken);
        }

        const payload = await apiGet(`${LOCATIONS_API_ROOT}/${accountName}/locations?${query.toString()}`, accessToken);
        locations.push(...(payload.locations || []));
        pageToken = payload.nextPageToken || '';
    } while (pageToken);

    return locations;
}

function selectAccount(accounts) {
    const preferred = normalizeAccountName(process.env.GBP_ACCOUNT_NAME || process.env.GBP_ACCOUNT_ID);
    if (preferred) {
        const exact = accounts.find((a) => a.name === preferred);
        if (exact) return exact;
    }

    if (accounts.length === 1) {
        return accounts[0];
    }

    const hint = (process.env.GBP_ACCOUNT_HINT || 'knight group').toLowerCase().trim();
    if (hint) {
        const found = accounts.find((a) => {
            const name = (a.accountName || '').toLowerCase();
            return name.includes(hint);
        });
        if (found) return found;
    }

    throw new Error(
        'Unable to auto-select GBP account. Set KNIGHTGROUP_GBP_ACCOUNT_NAME or GBP_ACCOUNT_NAME. ' +
        `Available accounts: ${accounts.map((a) => `${a.name} (${a.accountName || 'no-label'})`).join(', ')}`
    );
}

function knightGroupLocationNameFromEnv() {
    const candidates = [
        process.env.KNIGHTGROUP_GBP_LOCATION_NAME,
        process.env.KG_GBP_LOCATION_ID
    ];
    for (const value of candidates) {
        if (isUsableId(value)) {
            return normalizeLocationName(value);
        }
    }
    return null;
}

function isOtherBrandLocation(location) {
    const title = String((location && location.title) || '').toLowerCase();
    const name = normalizeLocationName(location && location.name);
    if (name === KNIGHT_LOGICS_LOCATION) return true;
    return /logics|screen team|faith works|roof monsters|resin tables/.test(title);
}

function assertKnightGroupLocation(location) {
    if (!location || !location.name) {
        throw new Error('No GBP location selected for Knight Group.');
    }
    if (isOtherBrandLocation(location)) {
        throw new Error(
            `Refusing to sync ${location.title || location.name} onto the Knight Group site. ` +
            'Use KNIGHTGROUP_GBP_LOCATION_NAME or KG_GBP_LOCATION_ID.'
        );
    }
}

function selectLocation(locations) {
    const preferred = knightGroupLocationNameFromEnv();
    if (preferred) {
        const exact = locations.find((l) => l.name === preferred);
        if (exact) return exact;
    }

    const exactTitle = locations.find((l) => String(l.title || '').trim().toLowerCase() === 'knight group');
    if (exactTitle) return exactTitle;

    const titleHint = (process.env.GBP_LOCATION_TITLE || DEFAULT_LOCATION_TITLE).toLowerCase().trim();
    const byTitle = locations.find((l) => {
        const title = (l.title || '').toLowerCase();
        return title.includes(titleHint) && !isOtherBrandLocation(l);
    });
    if (byTitle) {
        return byTitle;
    }

    throw new Error(
        'Unable to auto-select the Knight Group GBP location. Set KNIGHTGROUP_GBP_LOCATION_NAME or KG_GBP_LOCATION_ID. ' +
        `Available locations: ${locations.map((l) => `${l.name} (${l.title || 'no-title'})`).join(', ')}`
    );
}

async function listAllReviews(accessToken, accountName, locationName) {
    const reviews = [];
    let pageToken = '';
    let totalReviewCount = null;
    let averageRating = null;

    do {
        const query = new URLSearchParams({ pageSize: '50' });
        if (pageToken) {
            query.set('pageToken', pageToken);
        }

        const endpoint = `${REVIEWS_API_ROOT}/${accountName}/${locationName}/reviews?${query.toString()}`;
        const payload = await apiGet(endpoint, accessToken);
        reviews.push(...(payload.reviews || []));
        if (payload.totalReviewCount != null) {
            totalReviewCount = Number(payload.totalReviewCount);
        }
        if (payload.averageRating != null) {
            averageRating = Number(payload.averageRating);
        }
        pageToken = payload.nextPageToken || '';
    } while (pageToken);

    return { reviews, totalReviewCount, averageRating };
}

function hashColor(value) {
    const digest = crypto.createHash('sha1').update(String(value || '')).digest();
    return AVATAR_COLORS[digest[0] % AVATAR_COLORS.length];
}

function mapStars(starValue) {
    if (typeof starValue === 'number') {
        return Math.max(1, Math.min(5, Math.round(starValue)));
    }

    if (!starValue) {
        return 5;
    }

    const normalized = String(starValue).toUpperCase().trim();
    return STAR_MAP[normalized] || 5;
}

function formatDate(isoDate) {
    if (!isoDate) return '';
    const date = new Date(isoDate);
    if (Number.isNaN(date.getTime())) return '';
    return date.toISOString().slice(0, 10);
}

function toFeedReview(review) {
    const reviewerName = (review.reviewer && review.reviewer.displayName) || 'Google User';
    const starCount = mapStars(review.starRating);
    const comment = review.comment || '';
    const reply = review.reviewReply;
    const businessName = process.env.GBP_BUSINESS_DISPLAY_NAME || DEFAULT_BUSINESS_NAME;

    return {
        name: reviewerName,
        meta: 'Google review',
        date: formatDate(review.createTime || review.updateTime),
        text: comment,
        stars: starCount,
        avatarColor: hashColor(reviewerName),
        replied: Boolean(reply && reply.comment),
        ownerReply: reply && reply.comment
            ? {
                name: businessName,
                date: formatDate(reply.updateTime),
                text: reply.comment
            }
            : undefined
    };
}

function buildPayload(sourceReviews, location, totals = {}) {
    const reviews = sourceReviews
        .map(toFeedReview)
        .filter((r) => r.text || r.stars)
        .sort((a, b) => String(b.date).localeCompare(String(a.date)));

    const ratingTotal = reviews.reduce((sum, r) => sum + (Number(r.stars) || 0), 0);
    const computedRating = reviews.length ? Number((ratingTotal / reviews.length).toFixed(1)) : 0;
    const reviewCount = Number(totals.totalReviewCount || reviews.length || 0);
    const ratingValue = totals.averageRating != null
        ? Number(Number(totals.averageRating).toFixed(1))
        : computedRating;

    return {
        ratingValue,
        reviewCount,
        fetchedAt: new Date().toISOString(),
        source: {
            account: process.env.GBP_ACCOUNT_NAME || null,
            location: location.name,
            locationTitle: location.title || null
        },
        reviews
    };
}

function toErrorMessage(error) {
    if (!error) return '';
    if (typeof error === 'string') return error;
    return String(error.message || error);
}

function looksLikeQuotaBlocked(error, apiUrlFragment) {
    const msg = toErrorMessage(error);
    return msg.includes('API request failed (429)') && (!apiUrlFragment || msg.includes(apiUrlFragment));
}

function extractActivationUrl(error) {
    const msg = toErrorMessage(error);
    const match = msg.match(/https?:\/\/[^\s"']*console\.developers\.google\.com[^\s"']*/i);
    return match ? match[0] : null;
}

function looksLikeServiceDisabled(error) {
    const msg = toErrorMessage(error);
    return msg.includes('SERVICE_DISABLED') || msg.includes('API has not been used') || msg.includes('it is disabled');
}

async function apiPatch(url, accessToken, body, updateMask) {
    const target = new URL(url);
    target.searchParams.set('updateMask', updateMask);
    const response = await fetch(target, {
        method: 'PATCH',
        headers: {
            Authorization: `Bearer ${accessToken}`,
            Accept: 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(`API patch failed (${response.status}) ${url} :: ${JSON.stringify(payload)}`);
    }
    return payload;
}

function hoursKey(hours) {
    const periods = ((hours && hours.periods) || []).map((period) => ({
        openDay: period.openDay,
        openHours: (period.openTime && period.openTime.hours) || 0,
        openMinutes: (period.openTime && period.openTime.minutes) || 0,
        closeDay: period.closeDay,
        closeHours: (period.closeTime && period.closeTime.hours) || 0,
        closeMinutes: (period.closeTime && period.closeTime.minutes) || 0
    }));
    periods.sort((a, b) => String(a.openDay).localeCompare(String(b.openDay)));
    return JSON.stringify(periods);
}

async function syncRegularHours(accessToken, location, dryRun) {
    const url = `${LOCATIONS_API_ROOT}/${location.name}`;
    const current = await apiGet(`${url}?readMask=${encodeURIComponent('name,title,regularHours')}`, accessToken);
    const same = hoursKey(current.regularHours) === hoursKey(CANONICAL_REGULAR_HOURS);
    if (same) {
        console.log('GBP hours already match the site: Monday–Friday 8 AM–5 PM.');
        return current.regularHours;
    }

    console.log('GBP hours were:', JSON.stringify(current.regularHours || null));
    if (dryRun) {
        console.log('[dry-run] Would PATCH regularHours to Monday–Friday 8 AM–5 PM.');
        return CANONICAL_REGULAR_HOURS;
    }

    const updated = await apiPatch(url, accessToken, { regularHours: CANONICAL_REGULAR_HOURS }, 'regularHours');
    console.log('Updated GBP hours to Monday–Friday 8 AM–5 PM.');
    return updated.regularHours || CANONICAL_REGULAR_HOURS;
}

function writeEntityRating(payload, dryRun) {
    if (!fs.existsSync(ENTITY_PATH)) return;
    const entity = JSON.parse(fs.readFileSync(ENTITY_PATH, 'utf8'));
    entity.aggregateRating = entity.aggregateRating || { '@type': 'AggregateRating' };
    entity.aggregateRating.ratingValue = Number(payload.ratingValue).toFixed(1);
    entity.aggregateRating.reviewCount = String(payload.reviewCount);
    entity.aggregateRating.bestRating = entity.aggregateRating.bestRating || '5';
    entity.aggregateRating.worstRating = entity.aggregateRating.worstRating || '1';
    if (dryRun) {
        console.log('[dry-run] Would set entity aggregateRating to', entity.aggregateRating.ratingValue, entity.aggregateRating.reviewCount);
        return;
    }
    fs.writeFileSync(ENTITY_PATH, `${JSON.stringify(entity, null, 2)}\n`, 'utf8');
}

function writeHomeReviews(payload, dryRun) {
    const picked = (payload.reviews || [])
        .filter((review) => review.text)
        .slice(0, 3)
        .map((review) => ({
            '@type': 'Review',
            author: { '@type': 'Person', name: review.name },
            datePublished: review.date,
            reviewBody: review.text,
            reviewRating: {
                '@type': 'Rating',
                ratingValue: String(review.stars || 5),
                bestRating: '5'
            }
        }));
    if (!picked.length) return;
    if (dryRun) {
        console.log('[dry-run] Would write', picked.length, 'schema reviews');
        return;
    }
    fs.writeFileSync(HOME_REVIEWS_PATH, `${JSON.stringify(picked, null, 2)}\n`, 'utf8');
}

function applyReviewCountToHtml(rootDir, payload, dryRun) {
    const count = String(payload.reviewCount);
    const rating = Number(payload.ratingValue).toFixed(1);
    const files = [];

    function walk(dir) {
        for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
            if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === '__pycache__') continue;
            const full = path.join(dir, entry.name);
            if (entry.isDirectory()) walk(full);
            else if (entry.name.endsWith('.html')) files.push(full);
        }
    }

    walk(rootDir);
    let changed = 0;
    for (const file of files) {
        const original = fs.readFileSync(file, 'utf8');
        let next = original.replace(/"reviewCount":\s*"\d+"/g, `"reviewCount": "${count}"`);
        next = next.replace(/\d+(?:\.\d+)? &middot; \d+ reviews/g, `${rating} &middot; ${count} reviews`);
        next = next.replace(/\d+(?:\.\d+)? · \d+ reviews/g, `${rating} · ${count} reviews`);
        next = next.replace(/\d+(?:\.\d+)? &middot; \d+ Google reviews/g, `${rating} &middot; ${count} Google reviews`);
        next = next.replace(/\d+ out of 5 stars, \d+ Google reviews/g, `${rating.replace(/\.0$/, '')} out of 5 stars, ${count} Google reviews`);
        next = next.replace(/5(?:\.0)? Google rating\s+\d+ reviews/g, `${rating} Google rating  ${count} reviews`);
        next = next.replace(/Google rating\s+\d+ reviews/g, `Google rating  ${count} reviews`);
        if (next !== original) {
            changed += 1;
            if (!dryRun) fs.writeFileSync(file, next, 'utf8');
        }
    }
    console.log(`${dryRun ? '[dry-run] Would update' : 'Updated'} ${changed} HTML files with ${rating} / ${count} reviews.`);
}

function writeOutput(payload, dryRun) {
    const json = `${JSON.stringify(payload, null, 2)}\n`;
    if (dryRun) {
        console.log('[dry-run] Would write', OUTPUT_PATH);
        console.log('[dry-run] reviewCount =', payload.reviewCount, 'ratingValue =', payload.ratingValue);
        return;
    }

    fs.writeFileSync(OUTPUT_PATH, json, 'utf8');
    console.log('Wrote review feed:', OUTPUT_PATH);
    console.log('reviewCount =', payload.reviewCount, 'ratingValue =', payload.ratingValue);
}

async function run() {
    loadDefaultEnvs();

    const dryRun = process.argv.includes('--dry-run');
    const skipHours = process.argv.includes('--skip-hours');
    const applyOnly = process.argv.includes('--apply-only');
    const applyRootArg = process.argv.find((arg) => arg.startsWith('--root='));
    const applyRoot = applyRootArg ? applyRootArg.slice('--root='.length) : ROOT;

    if (applyOnly) {
        const feedPath = path.join(applyRoot, 'data', 'google-reviews.json');
        const payload = JSON.parse(fs.readFileSync(feedPath, 'utf8'));
        applyReviewCountToHtml(applyRoot, payload, dryRun);
        return;
    }

    const accessToken = await getAccessToken();

    const explicitAccountName = isUsableId(process.env.KNIGHTGROUP_GBP_ACCOUNT_NAME || process.env.GBP_ACCOUNT_NAME)
        ? normalizeAccountName(process.env.KNIGHTGROUP_GBP_ACCOUNT_NAME || process.env.GBP_ACCOUNT_NAME)
        : null;
    const explicitLocationName = knightGroupLocationNameFromEnv();

    let accountName = explicitAccountName;
    let location = explicitLocationName
        ? {
            name: explicitLocationName,
            title: process.env.KNIGHTGROUP_GBP_LOCATION_TITLE || DEFAULT_LOCATION_TITLE
        }
        : null;

    if (!accountName) {
        let accountsPayload;
        try {
            accountsPayload = await apiGet(ACCOUNTS_API, accessToken);
        } catch (error) {
            if (looksLikeQuotaBlocked(error, ACCOUNTS_API)) {
                throw new Error(
                    'Account discovery is quota-blocked. Set KNIGHTGROUP_GBP_ACCOUNT_NAME and KNIGHTGROUP_GBP_LOCATION_NAME in accounts.env.'
                );
            }
            throw error;
        }

        const accounts = accountsPayload.accounts || [];
        if (!accounts.length) {
            throw new Error('No Google Business accounts found for the authorized user.');
        }

        const account = selectAccount(accounts);
        accountName = account.name;
        process.env.GBP_ACCOUNT_NAME = accountName;
    }

    if (!location || !location.title || location.title === DEFAULT_LOCATION_TITLE) {
        const locations = await listAllLocations(accessToken, accountName);
        if (!locations.length) {
            throw new Error(`No locations found under account ${accountName}.`);
        }
        location = selectLocation(locations);
    }

    assertKnightGroupLocation(location);
    console.log('Using GBP location:', location.title, location.name);

    const listed = await listAllReviews(accessToken, accountName, location.name);
    const payload = buildPayload(listed.reviews, location, listed);

    writeOutput(payload, dryRun);
    writeEntityRating(payload, dryRun);
    writeHomeReviews(payload, dryRun);
    applyReviewCountToHtml(applyRoot, payload, dryRun);

    if (!skipHours) {
        await syncRegularHours(accessToken, location, dryRun);
    }
}

run().catch((error) => {
    if (looksLikeServiceDisabled(error)) {
        const activationUrl = extractActivationUrl(error) ||
            'https://console.cloud.google.com/apis/library/mybusiness.googleapis.com';
        console.error(
            'GBP review sync failed: enable Business Profile APIs in GCP. ' +
            `See: ${activationUrl}`
        );
    } else {
        console.error('GBP review sync failed:', error.message || error);
    }
    process.exitCode = 1;
});
