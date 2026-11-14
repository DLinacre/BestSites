# Atlas data sources and curation notes

## Upstream research

The category map and resource discovery were researched from FMHY’s official public directory on 14 November 2026. Each resource record stores its corresponding source category URL. Source pages are live and can change; these links are attribution and research references, not claims that Atlas endorses every upstream listing.

| Atlas section | FMHY research page |
|---|---|
| Privacy & security | https://fmhy.net/privacy |
| Artificial intelligence | https://fmhy.net/ai |
| Film & television | https://fmhy.net/video |
| Music & audio | https://fmhy.net/audio |
| Gaming & play | https://fmhy.net/gaming |
| Books & reading | https://fmhy.net/reading |
| Software & downloads | https://fmhy.net/downloading |
| Torrenting & open data | https://fmhy.net/torrenting |
| Learning & education | https://fmhy.net/educational |
| Android & iOS | https://fmhy.net/mobile |
| Linux & macOS | https://fmhy.net/linux-macos |
| Around the world | https://fmhy.net/non-english |
| Curiosities & useful things | https://fmhy.net/misc |

FMHY informed discovery and category structure, but Atlas is an independent directory. Entries that appeared in upstream sections were **not** automatically carried over. Atlas excludes pirate streaming, unauthorised copyrighted downloads, cracked software, stolen accounts, suspicious APK aggregators and DRM/paywall circumvention. Its torrenting section is limited to reputable clients and legitimate open-source, public-data and rights-aware distribution. Entertainment and reading favour licensed free services, institutional collections, public-domain works and open-access materials.

## Featured recommendations

One editorial pick is identified for each category in `src/lib/resources.ts`. The selection rationale is stored beside the corresponding resource record and shown on that category’s page.

| Section | Editor’s pick | Why this is the starting point |
|---|---|---|
| Privacy & security | [uBlock Origin](https://github.com/gorhill/uBlock) | Mature open-source browser blocking, broad filter support and active stewardship. |
| Artificial intelligence | [Ollama](https://ollama.com/) | Makes local model experimentation approachable while keeping inference on the user’s device. |
| Film & television | [Kanopy](https://www.kanopy.com/) | Library-backed access to an authorised film and documentary catalogue where an institution participates. |
| Music & audio | [Bandcamp](https://bandcamp.com/) | Artist-first discovery; many releases can be streamed free, with optional purchases supporting creators. |
| Gaming & play | [itch.io — free games](https://itch.io/games/free) | Direct-to-creator discovery with free releases and creator-controlled distribution. |
| Books & reading | [Project Gutenberg](https://www.gutenberg.org/) | Long-running volunteer library with a clear public-domain focus and downloadable ebooks. |
| Software & downloads | [GitHub](https://github.com/) | Explore projects from maintainers and inspect source, history and releases directly. |
| Torrenting & open data | [qBittorrent](https://www.qbittorrent.org/) | Cross-platform, established open-source client without bundled advertising. Use only for lawful torrents. |
| Learning & education | [Khan Academy](https://www.khanacademy.org/) | Respected nonprofit with structured free instruction and practice across core subjects. |
| Android & iOS | [F-Droid](https://f-droid.org/) | Free-software-first Android repository with transparent source and build practices. |
| Linux & macOS | [ArchWiki](https://wiki.archlinux.org/) | Detailed, actively maintained technical documentation that is useful beyond Arch Linux. |
| Around the world | [Wiktionary](https://www.wiktionary.org/) | Broad free multilingual dictionary with cross-language discovery and community editing. |
| Curiosities & useful things | [Awesome lists](https://github.com/sindresorhus/awesome) | Well-established index of topic-specific lists that lead to specialist projects and guides. |

## Entry provenance and status

The dataset is a curated snapshot, not a live API feed. `src/lib/resources.ts` contains original summaries, categorisation, platforms, tags, pricing and open-source flags. `sourceCategoryUrl` ties each listing to its FMHY research section. `src/data/link-status.json` is the result store populated by the reusable audit script. An empty entry is shown as **Not checked** until an audit actually records a result.

Pricing and platform availability can vary by country, product plan and date. Descriptions state known caveats where material: libraries may require a participating membership; free tiers can have limits; item-level rights and licences can differ; and geographic availability applies to some streaming sites. Readers should check a service’s own terms, privacy policy, publisher and licence. An open-source marker refers to the project/service software, not merely to the fact that content is free or openly licensed.

## Link audit

Run `npm run check:links` to produce a human-readable `LINK_AUDIT.md`, or `npm run check:links:update` to also write status/timestamps into `src/data/link-status.json`. The checker records redirects and final destinations, refuses local/private network targets, tries HEAD then a small GET fallback, and treats network blocks, bot denials and temporary server errors as inconclusive rather than broken. Suspected parked pages and cross-host redirects receive a review note.

At the time of this build, no external link has been asserted as verified without a recorded check. See the current [`LINK_AUDIT.md`](LINK_AUDIT.md) for check timestamps and per-link findings. Automated verification is not a malware scan or legal opinion.
