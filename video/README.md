# GTA VI decomp thread → video

Two cuts of a narrated recap of the r/Piracy thread about GTA VI being decompiled
to PC five days after the console launch.

| File | Format | Length |
| --- | --- | --- |
| `public/video/gtavi_piracy_recap_16x9.mp4` | 1920×1080, 30 fps | ~3:25 |
| `public/video/gtavi_piracy_recap_9x16.mp4` | 1080×1920, 30 fps | ~3:25 |

Both are H.264 + AAC, mono 44.1 kHz.

## What's in it

- Narration: 8 beats, generated voice (not a human recording)
- Reddit-style comment cards quoting the thread (usernames shown, text lightly trimmed)
- Cutaway beats: `$4,000,000,000` counter with revenue vs. dev-cost bars, a mocked
  decompiler window, and a LEGO → Play-Doh diagram for the "console speaks ABC" comment
- Captions punched up for the short-form cut, glitch transitions, film grain
- Generated lo-fi bed (76 BPM, Am7–Fmaj7–Cmaj7–G6) side-chain ducked under the voice

All figures quoted ($4B revenue, ~$1.5B dev + marketing) come from the thread itself
and are unverified; the video says so on the end card.

## Re-rendering

```bash
cd video
python3 -m venv .venv && . .venv/bin/activate
pip install pillow numpy imageio-ffmpeg fonttools brotli   # ffmpeg comes from imageio-ffmpeg
python render.py 16x9
python render.py 9x16
```

Frames are pushed as raw RGB into ffmpeg (libx264, CRF 19), then muxed with the
mixed audio. On a 2-core sandbox this takes roughly 10 minutes per cut.

Preview a single scene without rendering everything:

```bash
python render.py 16x9 --preview 1:1 build/preview.png   # BEAT:SCENE
```

## Layout

- `content.py` — all copy: comment cards, scene list per narration beat, captions
- `render.py` — scene builders, compositor, audio synthesis and mix
- `audio/beatN.mp3` — narration clips, one per beat (durations drive scene timing)
- `assets/fonts/` — Inter, Anton and Space Mono, converted from the `@fontsource`
  npm packages (woff2 → ttf) so the renderer has exact metrics
- `build/` — scratch output, safe to delete

Narration text is not stored in the repo; regenerate or re-record clips into
`audio/beat1.mp3` … `audio/beat8.mp3` and the timeline follows their durations.

Renders are written straight to `public/video/` so the site at `/video` serves them.
They are committed (≈43 MB) because the deployed page streams them as static assets;
keep that in mind before re-running a render, since Git keeps every historical copy.
