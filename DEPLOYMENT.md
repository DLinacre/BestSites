# Vercel deployment readiness

Atlas is a Next.js App Router application with a static-first build. It needs no database, secret key, paid API or custom runtime. The repository is configured for Vercel’s Next.js preset and includes a separate GitHub Actions CI workflow.

## Build configuration

- Framework preset: **Next.js** (automatic detection)
- Root directory: `.`
- Install command: `npm ci --legacy-peer-deps`
- Build command: `npm run build`
- Output directory: leave unset (Vercel manages Next.js output)
- Required environment variable for a stable custom canonical origin: `NEXT_PUBLIC_SITE_URL=https://<your-chosen-domain>` for Preview and Production as appropriate. Set this to an origin only (scheme + host; no path, query or fragment).
- No other environment variables or secrets are required. Vercel’s `VERCEL_URL` is used as an HTTPS fallback for its generated deployment hostname; local builds default to `http://localhost:3000`.

The site-origin helper validates the configured origin, derives metadata’s `metadataBase`, sitemap URLs and the robots sitemap reference from the same value, and rejects non-HTTPS configured production origins. Supply the domain you own; this repository does not invent one. Category canonical URLs are `/{id}`. Legacy duplicate paths `/category/{id}` return permanent redirects; the sitemap lists exactly one category URL each. `/saved` is excluded from the sitemap and robots index directives.

## Deploy from the Vercel dashboard

1. Import `DLinacre/BestSites` into a Vercel project or select an existing Atlas project.
2. Choose the Next.js framework preset and confirm the commands above.
3. Set `NEXT_PUBLIC_SITE_URL` to the actual canonical HTTPS origin you control.
4. Deploy and wait for Vercel to report **Ready**.
5. Verify the actual deployment: `/`, all 13 category routes, `/category/privacy` (308 to `/privacy`), `/category/not-a-real-category` (404), `/about`, `/saved`, `/robots.txt`, `/sitemap.xml`, `/manifest.webmanifest`, `/sw.js`, and PWA icon URLs.
6. In Chromium DevTools → Application, check the manifest, service worker scope and active controller. Install via the native browser prompt after a user action. Load a category, switch offline and revisit it; also check the static `/offline.html` fallback. On iOS Safari, use Share → Add to Home Screen and reopen in standalone mode.

## Local production verification

```bash
npm ci --legacy-peer-deps
npm run typecheck
npm run lint
npm test
npm run build
npm start
```

`window.isSecureContext` gates service-worker registration. HTTPS is required in production; browsers treat localhost/loopback as secure for local development. `public/manifest.webmanifest`, icons and `public/sw.js` are same-origin public assets.

## PWA caching and updates

The service worker uses a versioned same-origin app-shell cache (`atlas-shell-v2` at this revision), precaches the homepage, offline page and 13 category pages, caches subsequently visited same-origin navigations/static assets, and falls back to the route cache then `/offline.html`. It never caches third-party destinations, API responses or local browser storage. When activated, it removes older `atlas-shell-*` caches. Its script and manifest have revalidation headers so the browser can pick up worker and icon changes. Increment the shell version when changing the cache strategy or offline assets.

The Chromium/Android `beforeinstallprompt` event is prevented and stored; the native prompt is called only inside the visitor’s button click. Dismissal is remembered, and `appinstalled`, display-mode standalone and iOS `navigator.standalone` state suppress future invitations. iPhone/iPad Safari gets manual Add to Home Screen instructions. CI includes Playwright installation, worker, install-flow, offline and axe accessibility tests.

## CI and scheduled link checks

`.github/workflows/ci.yml` runs on pushes and PRs to `main`, plus manual dispatch. It uses Node 22, the committed lockfile, and installs Playwright Chromium with Linux system dependencies before running typecheck, lint, unit tests, production build, E2E and accessibility suites. The pre-existing `.github/workflows/link-audit.yml` stays separate and scheduled; it runs the 104 destination checks from GitHub-hosted runners and saves the report/status JSON as a workflow artifact. Audit failure or blocked individual destinations are disclosed, not silently treated as working.

## Current deployment status

Vercel project listings were checked for both `BestSites` and `Atlas`; no matching project was returned. **No Atlas deployment is configured or verified, and no live URL is claimed.** Create/import the Vercel project and set its actual canonical domain as above before launch. After deployment, confirm its state and test the returned production URL before sharing it.
