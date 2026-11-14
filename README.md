# Atlas — free to explore

Atlas is an independently branded, installable directory of useful free websites, software and resources. It has 13 dedicated category pages and 104 curated destinations, a keyboard-accessible global search, bookmarks and history stored on-device, three themes, link-status disclosures, and an offline-capable PWA shell.

Atlas was inspired by the breadth and category organisation of [FMHY](https://fmhy.net/), but is a separate project with its own identity, descriptions, recommendations and lawful-content standards. It is not affiliated with or endorsed by FMHY.

## Requirements

- Node.js 22.17 or later (Node 22 LTS recommended)
- npm 10+
- For browser tests: Chromium installed with Playwright

## Install and run locally

```bash
npm ci --legacy-peer-deps
npm run dev
```

Open <http://localhost:3000>. The site works without API keys, paid services, a database, or an account. On first visit, a small install invitation appears; dismissal and installed-app state are respected on this device. The service worker registers only when `window.isSecureContext` is true, including HTTPS and localhost/loopback development.

## Routes

The 13 directory routes are `/privacy`, `/ai`, `/movies`, `/music`, `/gaming`, `/books`, `/downloads`, `/torrenting`, `/education`, `/mobile`, `/linux`, `/international`, and `/misc`. `/saved` contains local bookmarks and visit history; `/about` explains sourcing, link states and privacy.

## Build, lint and test

```bash
npm run typecheck
npm run lint
npm test                 # data integrity, featured picks and search unit tests
npm run build
npm run test:e2e        # requires Playwright Chromium
npm run test:a11y       # WCAG 2.1 A/AA axe checks
```

Browser tests in `e2e/` cover all category routes, canonical redirects and 404s, search, filters, bookmarks, mobile navigation, install-prompt timing, iOS instructions, secure-context service-worker registration, cached offline pages, fallback behavior and cache cleanup. The accessibility spec runs axe against key pages/themes.

```bash
npx playwright install --with-deps chromium
npm run test:e2e
npm run test:a11y
```

The dedicated GitHub Actions CI workflow installs Chromium and its Linux dependencies before running both suites. Local browser tests require the same Playwright browser libraries.

## Search and personal features

- Search the full directory by name, description, category, type, platform or tags; one-character typos are tolerated for longer terms.
- Press `Ctrl+K` or `⌘K` to open search. Use arrow keys and Enter to choose a result.
- Search refinements include category, type, platform, pricing, open-source-only and sort.
- Save or unsave a card with its bookmark control. The Saved page supports JSON export/import and clearing recent history.
- Theme button cycles Dark → Light → AMOLED. Theme, bookmarks, recently visited resources and recent categories stay in browser storage only.

## Update resources

Resource records live in [`src/lib/resources.ts`](src/lib/resources.ts). Each record includes its unique ID, HTTPS destination, original description, category/subcategory, resource type, tags, platforms, language, pricing model, open-source designation, featured reason, FMHY research-category URL, explicit regional-availability value, any known access requirements, and the current link-audit record. Regional availability is `unknown` until verified; it must never be inferred from a site's language or apparent reach. Access notes currently identify participating-library eligibility, phone-number registration and AI Studio account/regional limits where the source descriptions support them.

When adding a record:

1. Review the project’s official site and the matching FMHY research page.
2. Check that the destination is official or otherwise reputable, relevant, lawful, and not already used. Do not infer safety or licences from a listing alone.
3. Add an original description and a source category URL. Only set `openSource` when that applies to the resource itself, and choose a pricing model you can substantiate.
4. Keep the default link status `not-checked` until an audit records a result.
5. Run `npm test`, `npm run typecheck`, `npm run lint`, and `npm run check:links`.

The link checker writes `LINK_AUDIT.md`. To atomically update the UI’s structured audit data and report, run:

```bash
npm run check:links:update
```

A complete run is required before anything is written. Every current record stores resource ID, status, timestamp, method, HTTP status (or null), final URL, note, and explicit redirect/cross-host flags. New checks append the previous result to bounded history. A failed/incomplete run leaves the existing file untouched; an inconclusive per-link result becomes the latest honest status while keeping prior results in history. The report and UI read the same schema. The checker distinguishes responding destinations, redirects, bot-blocked/inconclusive checks and clear 404/410 failures. A 403/429, timeout, or sandbox network restriction is **not** labelled broken. The scheduled GitHub Action runs with GitHub-hosted outbound access and publishes each audit and status JSON as a workflow artifact; it does not silently commit status changes. Cross-host redirects and suspected parking pages need human review.

## PWA notes

The app manifest, maskable/standard icons, service worker and offline fallback are in `public/`. Only same-origin application pages and static application assets are cached; external destinations and personal data are never cached. Cache names are versioned and old Atlas caches are deleted on activation. Chromium browsers use `beforeinstallprompt` only after a user action. Safari on iPhone/iPad receives Add to Home Screen instructions.

## Privacy and attribution

No sign-in, analytics, third-party search API, advertising script, or remote font is needed. Saved items, recents and theme stay in local browser storage. FMHY is attributed as a research source in the resource details, About page and [`DATA_SOURCES.md`](DATA_SOURCES.md); resource summaries are original. See [`LINK_AUDIT.md`](LINK_AUDIT.md) for current link results and [`DEPLOYMENT.md`](DEPLOYMENT.md) for Vercel setup.
