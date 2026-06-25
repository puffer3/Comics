# Handoff — PhotoSwipe + readers (for next session)

**Next goal:** mix the PhotoSwipe approach into the **comics viewer** (`reader.html`), reusing reader logic.

**Repo:** `~/Documents/GitHub/Comics` (GitHub Pages, henryjamesglover.com). Vanilla HTML/CSS/JS, no build step. All changes below are **uncommitted in the working tree** — push from laptop via GitHub Desktop. Hard-refresh (Cmd+Shift+R); the `content.js`/CSS cache bites often.

---

## Files changed this session (commit these)

- **`illustrations-photoswipe.html`** — NEW. The PhotoSwipe illustrations page (details below). Intended to **replace `drawings.html`** eventually; keep the old `drawings.html` + `illreader.html` as backups.
- **`generate.py`** — `image_item()` now records full-image `w`/`h` into each item (PhotoSwipe needs dimensions). Backward-compatible (gallery.js/readers ignore extra fields).
- **`content.js`** — regenerated; every image now has `"w"`/`"h"`. Also normal regen.
- **`reader.html`** (comics) — flex-column layout that fills space under the 65px sticky header so the page + counter always fit with no scroll; mobile full-width with aspect-preserving height cap (tall pages get side gutters, not stretched); mobile brand bar hidden (header collapsed, nav kept); small top breathing room.
- **`illreader.html`** (illustrations reader) — flex-column fit; bigger images; group hero in fixed-size box with thumbnail column that doesn't shift; desktop click-zoom + drag-pan (dbl-click/Esc out); mobile fullscreen tap-zoom + pan + swipe-to-navigate (swipe block is fenced as a removable EXPERIMENT); brand bar hidden on mobile; captions render below, image shrinks to fit.
- **`styles.css`** — removed dead `.ill-lb` mobile lightbox CSS.
- **`index.html`, `drawings.html`** — mobile `.page{padding-top:16px}` to lift the section title toward the top bar.
- **`about.html`** — fish-proverb link swapped to the rooster tale; link text "old painter's proverb".

---

## PhotoSwipe illustrations page (`illustrations-photoswipe.html`) — how it works

- **Runtime, not baked.** Loads `content.js`; builds everything in an inline ES-module script. Styled with the site's `styles.css` (snake background, real header/nav, `.sec-head` title). Loads PhotoSwipe v5 + nothing else from unpkg CDN at runtime (needs internet when opened).
- **Flat single gallery.** One swipeable sequence (`dataSource` array). Order: each project's images contiguous `[hero, sub, sub…]`, then the loose singles.
- **Sub-images have no thumbnail.** The grid shows one tile per project **hero** + each single (heroes+singles = the `entries`). Sub-images live only in the swipe sequence (folded in right after their hero). Tile click = `loadAndOpen(thatSlideIndex)`; swiping/arrows continue through everything.
- **Captions = same CSV.** `capOf(it)` reads `it.title`/`it.desc` (from `captions.csv` → `generate.py` → `content.js`). Empty = hidden. None written yet.
- **Right-hand panel** (custom PhotoSwipe UI element, `pswp.ui.registerElement`, updated on `change`): caption text **plus**, for project images, a strip of **member squares** (ported hero/thumb logic from the reader) — click a square = `pswp.goTo(i)`, current one outlined. Arrow keys already walk member images (consecutive slides) and the highlight follows.
  - **Anti-jump:** squares are absolutely anchored to vertical center; caption grows **upward** from just above them, so caption length never moves the squares. Singles (no squares) center the caption. On `≤820px` the panel drops to a bottom strip.
- **Styling choices locked in:** white lightbox (`--pswp-bg:#fff`), grey icons (`--pswp-icon-color:#9aa0a8`), arrows at **bottom corners**, **no** 3/3 counter, **no** zoom button (pinch/dbl-tap still zoom), white grid tiles, grid thumbnails zoomed crop `object-fit:cover; transform:scale(1.5)`.
- **Centered image + caption space:** `paddingFn` reserves **equal** 320px left/right gutters on wide screens so the image stays centered while the caption sits in the right gutter (left gutter empty).

---

## Comics viewer current state (`reader.html`) — what to reuse / mind

- Books are multi-page (`window.BOOKS[section]`). Desktop shows **page 1 alone, then 2-up spreads** (`isSpread` at `min-width:900px`); mobile + illustrations are single-image.
- Navigation: side arrows (fixed), keyboard arrows, and **tap-to-turn** (left third = back, right = forward) with a fading tap-guide overlay. Image **preloading** (next/prev warmed + background warm).
- Layout: `.reader` is a flex column `height:calc(100vh - 65px)`; `.stage{flex:1}`, image `max-height:100%` — auto-fits, no scroll.
- Mobile: full phone width, aspect-preserving height cap `calc(100svh - 130px)` so tall pages (Tour, Mire) get side gutters and the page counter stays visible.
- The page **counter** ("3 / 12") is shown for books only.

## Ideas for mixing PhotoSwipe into comics (next session)

- Comics are a different genre than a photo gallery: **2-up spreads** and **page-turn** don't map cleanly to PhotoSwipe's one-slide swiper. Decide per-mode.
- Likely good fit: use PhotoSwipe's **pinch/zoom + pan** inside a comic page (esp. mobile, to read dense panels), while keeping the existing spread/page-turn flow — i.e. borrow PhotoSwipe's gesture engine, not its whole navigation.
- Alternative: single-page comics could become a PhotoSwipe gallery (each page a slide, swipe to turn), with spreads handled by feeding 2-up composite images or dropping spreads on mobile. Captions/counter would move into a custom UI element like the illustrations side panel.
- Reuse from the illustrations page: the **custom side-panel UI element** pattern, `paddingFn` centering, white/grey theming, the **dimensions-in-content.js** plumbing (already done).

## Ordering (answered)

Order = **filename** (generate.py natural-sorts). Prefix files with numbers (`01-…`, `02-…`) and rerun `generate.py`. Projects always precede loose singles; `_a/_b/_c` sets within-project order; projects ordered by base name. Arbitrary project/single interleaving would need an explicit order list (not built).

## Open items

- Write real captions in `captions.csv` (then rerun `generate.py`).
- Re-export low-res color illustrations at higher res (≈3000–4000px long edge) for crisp zoom; worst: `medusaMom_a` (1000px), `bandanna` (1200px). Same export program; keep filenames; rerun `generate.py`.
- Decide whether `illustrations-photoswipe.html` becomes the live `drawings.html` (keep old grid + `illreader.html` as backup).
- Store page still has Stripe `REPLACE_ME` placeholders; contact form needs one-time FormSubmit activation.
- Optional: one-line cache-buster on `content.js` across pages.
