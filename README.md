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

Open <http://localhost:3000>. The site works without API keys, paid services, a database, or an account. On first visit, a small install invitation appears; dismissing it is remembered in this browser. The PWA service worker is enabled on HTTPS and localhost.

## Routes

The 13 directory routes are `/privacy`, `/ai`, `/movies`, `/music`, `/gaming`, `/books`, `/downloads`, `/torrenting`, `/education`, `/mobile`, `/linux`, `/international`, and `/misc`. `/saved` contains local bookmarks and visit history; `/about` explains sourcing, link states and privacy.

## Build, lint and test

```bash
npm run typecheck
npm run lint
npm test                 # data integrity, featured picks and search unit tests
npm run build
```

Browser end-to-end tests live in `e2e/` and cover the home page, 13 category routes, search, category filters, saved resources, install invitation, manifest and mobile navigation. Install a browser once, then run them:

```bash
npx playwright install chromium
npm run test:e2e
```

For a Linux machine missing browser system libraries, use `npx playwright install --with-deps chromium` (requires an administrator). The development sandbox used to assemble this repository has no Chromium system libraries, so the browser suite is included but could not be executed there; the production build, lint, type checks and unit tests were run successfully.

## Search and personal features

- Search the full directory by name, description, category, type, platform or tags; one-character typos are tolerated for longer terms.
- Press `Ctrl+K` or `⌘K` to open search. Use arrow keys and Enter to choose a result.
- Search refinements include category, type, platform, pricing, open-source-only and sort.
- Save or unsave a card with its bookmark control. The Saved page supports JSON export/import and clearing recent history.
- Theme button cycles Dark → Light → AMOLED. Theme, bookmarks, recently visited resources and recent categories stay in browser storage only.

## Update resources

Resource records live in [`src/lib/resources.ts`](src/lib/resources.ts). Each record includes its unique ID, HTTPS destination, original description, category/subcategory, resource type, tags, platforms, language, pricing model, open-source designation, featured reason, FMHY research-category URL, link status and last-check timestamp.

When adding a record:

1. Review the project’s official site and the matching FMHY research page.
2. Check that the destination is official or otherwise reputable, relevant, lawful, and not already used. Do not infer safety or licences from a listing alone.
3. Add an original description and a source category URL. Only set `openSource` when that applies to the resource itself, and choose a pricing model you can substantiate.
4. Keep the default link status `not-checked` until an audit records a result.
5. Run `npm test`, `npm run typecheck`, `npm run lint`, and `npm run check:links`.

The link checker writes `LINK_AUDIT.md`. To update the UI’s status data as well, run:

```bash
npm run check:links:update
```

Review the generated final destinations and `src/data/link-status.json` before committing. The checker distinguishes working responses, redirects, bot-blocked/inconclusive checks, and broken responses. A 403/429, timeout, or sandbox network restriction is **not** labelled broken. A successful HTTP check does not guarantee that a site is safe, lawful in your jurisdiction, or suitable for a particular use. The scheduled GitHub Action publishes each audit and status JSON as a workflow artifact; it does not silently commit status changes.

## PWA notes

The app manifest, maskable/standard icons, service worker and offline fallback are in `public/`. Only same-origin application pages and static application assets are cached; external destinations and personal data are never cached. Cache names are versioned and old Atlas caches are deleted on activation. Chromium browsers use `beforeinstallprompt` only after a user action. Safari on iPhone/iPad receives Add to Home Screen instructions.

## Privacy and attribution

No sign-in, analytics, third-party search API, advertising script, or remote font is needed. Saved items, recents and theme stay in local browser storage. FMHY is attributed as a research source in the resource details, About page and [`DATA_SOURCES.md`](DATA_SOURCES.md); resource summaries are original. See [`LINK_AUDIT.md`](LINK_AUDIT.md) for current link results and [`DEPLOYMENT.md`](DEPLOYMENT.md) for Vercel setup.
