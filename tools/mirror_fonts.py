"""Mirror the Google Fonts dependency (Droid Serif 400, 400 italic) into site/_ext/ (Phase B practice: visual CDN
dependencies are served from the site itself).
Usage: python3 -I tools/mirror_fonts.py [--apply]   (from the repo root; dry run by default)
Fetches the CSS as a current browser does (woff2), saves the font files under site/_ext/fonts.gstatic.com/...,
writes the CSS with root-relative font URLs, and points the pages' <link> at it.
Refuses to apply unless every page that links the CSS is rewritten and no Google Fonts reference is left."""
import os, re, sys, urllib.parse, urllib.request

APPLY = '--apply' in sys.argv[1:]
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
CSS = 'https://fonts.googleapis.com/css?family=Droid+Serif:400,400italic'
LOCAL = '/_ext/fonts.googleapis.com/css/droid-serif-400-400italic.css'
LINK = re.compile(rb"<link href='" + re.escape(CSS.encode()) + rb"' rel='stylesheet' type='text/css'>")
LEFT = re.compile(rb'//fonts\.(?:googleapis|gstatic)\.com')   # external references only, not the /_ext/ copies


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
        assert r.status == 200, (url, r.status)
        return r.read()


css = get(CSS)
fonts = re.findall(rb'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', css)
assert len(fonts) == 2, fonts
out = {}
for u in fonts:
    path = '/_ext/' + urllib.parse.urlsplit(u.decode()).netloc + urllib.parse.urlsplit(u.decode()).path
    out[path] = get(u.decode())
    css = css.replace(u, path.encode())
out[LOCAL] = b'/* Mirrored from ' + CSS.encode() + b' (fetched as a current browser; woff2) by tools/mirror_fonts.py */\n' + css

pages, bad = {}, []
for root, dirs, files in os.walk('site'):
    for f in files:
        p = os.path.join(root, f)
        data = open(p, 'rb').read()
        if not LEFT.search(data):
            continue
        new, n = LINK.subn(b"<link href='" + LOCAL.encode() + b"' rel='stylesheet' type='text/css'>", data)
        if n != 1 or LEFT.search(new):
            bad.append(p)
        pages[p] = new
for path, data in out.items():
    print(f'{path}: {len(data)} bytes')
print(f'{len(pages)} pages relinked', 'BAD: ' + ' '.join(bad) if bad else '')
if bad:
    sys.exit(1)
if APPLY:
    for path, data in out.items():
        dst = 'site' + path
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'wb').write(data)
    for p, data in pages.items():
        open(p, 'wb').write(data)
    print('applied')
else:
    print('dry run (use --apply)')
