#!/usr/bin/env python3
"""
Scan content/<section> folders, build web thumbnails into a thumbs/ subfolder
inside each content folder, and write content.js (the gallery manifest).

Layout example:
    content/Comics/cover.jpg
    content/Comics/thumbs/cover.jpg              <- generated
    content/Comics/My Comic/01.jpg               <- a multi-page comic (any name)
    content/Comics/My Comic/thumbs/01.jpg        <- generated

- Loose image files in a section folder show as single images.
- A SUBFOLDER inside a section folder is treated as a multi-page set (a "book"):
  its images, sorted by filename, are the pages. The cover (first page) shows in
  the grid; clicking opens reader.html to flip through the pages.
  (Name pages 01.jpg, 02.jpg, ... so they sort in the right order.)

Grids show small thumbnails (fast); clicking opens the full-size original.

Run after adding/removing images, then commit & push:
    python3 generate.py

Thumbnails need Pillow:   pip3 install pillow
The Images/ folder is ignored (it's for backgrounds / site graphics).
"""
import os, json, csv, sys, re

FORCE = "--force" in sys.argv   # rebuild every thumbnail, ignore the up-to-date check

# page section key -> folder-name prefix (case-insensitive, trimmed)
SECTIONS = {
    "comics":      "comics",
    "drawings":    "drawings",
    "characters":  "character",     # matches "Character Designs"
    "storyboards": "storyboard",
}
IMG_EXT      = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}
RASTER_EXT   = {".jpg", ".jpeg", ".png", ".gif", ".webp"}   # Pillow can resize these
ALPHA_EXT    = {".png", ".gif", ".webp"}                    # keep transparency
CONTENT_DIR  = "content"
THUMB_SUBDIR = "thumbs"   # a thumbs/ folder is created inside each content folder
THUMB_MAX    = 800       # longest edge of a thumbnail, in pixels
JPEG_QUALITY = 82

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False


def is_image(fname):
    return os.path.splitext(fname)[1].lower() in IMG_EXT


def find_folder(prefix):
    if not os.path.isdir(CONTENT_DIR):
        return None
    for name in sorted(os.listdir(CONTENT_DIR)):
        full = os.path.join(CONTENT_DIR, name)
        if os.path.isdir(full) and name.strip().lower().startswith(prefix):
            return name
    return None


def make_thumb(src, mirror_dir, fname):
    """Create a thumbnail under thumbs/<mirror_dir>/ and return its web path.
    Falls back to the original image path when a thumbnail can't be made."""
    ext = os.path.splitext(fname)[1].lower()
    full_web = "{}/{}/{}".format(CONTENT_DIR, mirror_dir, fname).replace("\\", "/")

    if ext == ".svg" or ext not in RASTER_EXT or not HAVE_PIL:
        return full_web

    out_dir = os.path.join(CONTENT_DIR, mirror_dir, THUMB_SUBDIR)

    try:
        im = Image.open(src)
        # keep PNG only if the image genuinely has (partial) transparency;
        # otherwise flatten to a much smaller JPEG
        has_alpha = im.mode in ("RGBA", "LA", "PA") or (
            im.mode == "P" and "transparency" in im.info)
        if has_alpha:
            alpha = im.convert("RGBA").getchannel("A")
            if alpha.getextrema()[0] == 255:   # fully opaque despite alpha channel
                has_alpha = False

        out_ext = ".png" if has_alpha else ".jpg"
        out_path = os.path.join(out_dir, os.path.splitext(fname)[0] + out_ext)

        if not FORCE and os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(src):
            return out_path.replace(os.sep, "/")

        os.makedirs(out_dir, exist_ok=True)
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        if has_alpha:
            im.convert("RGBA").save(out_path)
        else:
            im.convert("RGB").save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        return out_path.replace(os.sep, "/")
    except Exception as e:
        print("  ! thumbnail failed for {} ({}) - using full image".format(src, e))
        return full_web


KEPT = set()   # normalized paths of thumbnails we want to keep (for pruning)


def image_item(content_rel_dir, fname):
    """Return {full, thumb} for one image. content_rel_dir is relative to content/."""
    src = os.path.join(CONTENT_DIR, content_rel_dir, fname)
    full = "{}/{}/{}".format(CONTENT_DIR, content_rel_dir, fname).replace("\\", "/")
    thumb = make_thumb(src, content_rel_dir, fname)
    if "/{}/".format(THUMB_SUBDIR) in thumb:
        KEPT.add(os.path.normpath(thumb))
    return {"full": full, "thumb": thumb}


galleries = {}   # section -> [ {full,thumb}, ... ]   loose single images
books = {}        # section -> [ {title,slug,cover,pages:[...]}, ... ]  subfolders
groups = {}       # section -> [ {base, images:[hero, ...]} ]  "a/b/c" projects

GROUP_RE = re.compile(r"^(.*)_([A-Za-z])$")   # e.g. Dragon_a, Dragon_b

def natkey(s):
    # natural sort: page2 < page10, and lowest number (0 or 1) comes first
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

for key, prefix in SECTIONS.items():
    folder = find_folder(prefix)
    loose, sect_books = [], []     # loose = [(fname, item), ...]
    if folder:
        base = os.path.join(CONTENT_DIR, folder)
        for entry in sorted(os.listdir(base), key=natkey):
            if entry.startswith(".") or entry.lower() == THUMB_SUBDIR:
                continue
            path = os.path.join(base, entry)
            if os.path.isdir(path):
                rel = "{}/{}".format(folder, entry)
                pages = [image_item(rel, f) for f in sorted(os.listdir(path), key=natkey)
                         if not f.startswith(".") and f.lower() != THUMB_SUBDIR and is_image(f)]
                if pages:
                    sect_books.append({
                        "title": entry,
                        "slug": entry,
                        "cover": pages[0],
                        "pages": pages,
                    })
            elif is_image(entry):
                loose.append((entry, image_item(folder, entry)))

    # group loose images named "<base>_<letter>"; 2+ members = a project ('a' = hero)
    gmap, singles, sect_groups = {}, [], []
    for fname, item in loose:
        m = GROUP_RE.match(os.path.splitext(fname)[0])
        if m:
            gmap.setdefault(m.group(1), []).append((m.group(2).lower(), item))
        else:
            singles.append(item)
    for gbase, members in gmap.items():
        if len(members) >= 2:
            members.sort(key=lambda x: x[0])              # a, b, c, ...
            sect_groups.append({"base": gbase, "images": [it for _l, it in members]})
        else:
            singles.append(members[0][1])                 # lone "_a" -> normal single

    galleries[key] = singles
    books[key] = sect_books
    groups[key] = sect_groups

# prune orphaned thumbnails (deleted/renamed sources, or PNG->JPEG changes).
# only runs when Pillow is available, so a missing-Pillow run never deletes thumbs.
removed = 0
if HAVE_PIL and os.path.isdir(CONTENT_DIR):
    for root, _dirs, fnames in os.walk(CONTENT_DIR):
        if os.path.basename(root).lower() != THUMB_SUBDIR:
            continue
        for f in fnames:
            if f.startswith("."):
                continue
            p = os.path.normpath(os.path.join(root, f))
            if p not in KEPT:
                try:
                    os.remove(p)
                    removed += 1
                except OSError:
                    pass
        try:
            if not os.listdir(root):
                os.rmdir(root)
        except OSError:
            pass

# ---- captions: auto-maintained captions.csv (file,title,description) ----
# Add a blank row for every new image; keep whatever text you've typed; drop
# rows for images that no longer exist. Edit the CSV any time, then re-run.
CAPTIONS_CSV = "captions.csv"

def cap_key(it):
    pre = CONTENT_DIR + "/"
    f = it["full"]
    return f[len(pre):] if f.startswith(pre) else f

def iter_items():
    for arr in galleries.values():
        for it in arr:
            yield it
    for arr in books.values():
        for b in arr:
            for p in b["pages"]:   # cover is pages[0], same object
                yield p
    for arr in groups.values():
        for g in arr:
            for it in g["images"]:
                yield it

existing = {}
if os.path.exists(CAPTIONS_CSV):
    with open(CAPTIONS_CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            k = (row.get("file") or "").strip()
            if k:
                existing[k] = (row.get("title") or "", row.get("description") or "")

current, n_caps = {}, 0
for it in iter_items():
    k = cap_key(it)
    title, desc = existing.get(k, ("", ""))
    current[k] = (title, desc)
    if title:
        it["title"] = title
    if desc:
        it["desc"] = desc
    if title or desc:
        n_caps += 1

with open(CAPTIONS_CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["file", "title", "description"])
    for k in sorted(current):
        t, d = current[k]
        w.writerow([k, t, d])

with open("content.js", "w") as out:
    out.write("// AUTO-GENERATED by generate.py - do not edit by hand.\n")
    out.write("window.GALLERY = " + json.dumps(galleries, indent=2) + ";\n")
    out.write("window.BOOKS = " + json.dumps(books, indent=2) + ";\n")
    out.write("window.GROUPS = " + json.dumps(groups, indent=2) + ";\n")

n_single = sum(len(v) for v in galleries.values())
n_books  = sum(len(v) for v in books.values())
n_pages  = sum(len(b["pages"]) for v in books.values() for b in v)
if not HAVE_PIL:
    print("WARNING: Pillow not installed - thumbnails skipped (using full images).")
    print("Install with: pip3 install pillow")
print("Wrote content.js")
print("  single images: {}".format(n_single))
print("  multi-page comics/books: {} ({} pages total)".format(n_books, n_pages))
if removed:
    print("  pruned {} orphaned thumbnail(s)".format(removed))
for k in SECTIONS:
    print("  {}: {} singles, {} books".format(k, len(galleries[k]), len(books[k])))
