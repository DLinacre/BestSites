# Deployment to Vercel

Atlas is a static-first Next.js App Router project with no database, server-only dependency, secrets, paid API or custom runtime. Category pages, home, Saved and About are prerenderable; Vercel serves the app over HTTPS, which is required for service-worker installation outside localhost.

## Deploy using the Vercel dashboard

1. Push this repository/branch to the GitHub repository you want Vercel to build, or import the existing repository from the Vercel dashboard.
2. Select **New Project → Import Git Repository**, choose the repository, and set the root directory to `.`.
3. Confirm **Next.js** is detected. Build command: `npm run build`. Install command: `npm ci --legacy-peer-deps`. No output directory override is needed.
4. Once you have selected the production domain, add `NEXT_PUBLIC_SITE_URL` in Vercel’s Production environment. Set it to the canonical origin, for example `https://atlas.your-domain.example` (replace this with your own domain). This origin is used for absolute social metadata and sitemap URLs. Do not leave a sample hostname in production.
5. Deploy. Confirm the deployment is **Ready**, and open `/`, `/privacy`, `/ai`, `/saved`, `/about`, `/manifest.webmanifest`, `/sw.js`, `/robots.txt` and `/sitemap.xml` on the HTTPS deployment.
6. In browser DevTools → Application, confirm the manifest and service worker load. Install on Chromium using its native prompt/menu, then use DevTools’ offline mode to confirm a previously loaded category still opens. On iOS, use Safari’s Share → Add to Home Screen.

## Local production check

```bash
npm ci --legacy-peer-deps
npm run typecheck
npm run lint
npm test
npm run build
npm start
```

Visit `http://localhost:3000`. Browsers treat localhost as a secure context for service-worker development. For an HTTPS staging deployment, set `NEXT_PUBLIC_SITE_URL` to its origin.

## PWA/cache notes

The manifest and service worker are static files under `public/`. `next.config.ts` makes the worker and manifest revalidate so a changed worker can activate, and the worker keeps versioned same-origin app-shell caches. It never fetches/caches external destination sites or personal bookmark data. Cache keys are versioned (`atlas-shell-v1` in `public/sw.js`); bump this string when changing the offline shell’s cached URL list or cache strategy.

`beforeinstallprompt` is captured only in supporting browsers and invoked only after a visitor selects Install. iOS/iPadOS uses clear manual Safari instructions. A first-visit invitation is a non-blocking card and its dismissal is remembered locally.

## Current deployment status

The connected Vercel account was checked during this build; no existing Vercel project matching this repository was returned. The integration explicitly does not permit silently creating a project when none is linked, so **Atlas has not been deployed and no live URL is claimed**. To publish, import this repository into a Vercel project using the steps above, or connect the appropriate existing Vercel project in Arena and request a deployment. Once Vercel returns a Ready deployment, verify it before sharing its URL.
