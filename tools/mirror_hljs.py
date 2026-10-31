"""Replace highlight.js 6.1 from yandex.st (gone) with highlight.js 11.12.0 served from site/_ext/ (owner, 2026-10-31, F43).
Usage: python3 -I tools/mirror_hljs.py <dir with the cdnjs files> [--apply]   (from the repo root; dry run by default)
The dir holds highlight.min.js and styles_base16_solarized-light.min.css, downloaded from
https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.12.0/ ; they must match cdnjs's published SRI hashes.
In 11.x the Solarized Light theme is styles/base16/solarized-light, and initHighlightingOnLoad() is deprecated,
so the pages call hljs.highlightAll() instead.
Refuses to apply unless every page with the old references gets all three replacements and no yandex.st is left."""
import base64, hashlib, os, re, sys

src = sys.argv[1]; APPLY = '--apply' in sys.argv[2:]
V = '11.12.0'
EXT = f'/_ext/cdnjs.cloudflare.com/ajax/libs/highlight.js/{V}'
FILES = {   # local file -> (path under EXT, cdnjs SRI)
    'highlight.min.js': ('/highlight.min.js',
                         'sha512-gzqHAlI1hVdzJ4wiQj/MkppDr6zgEdCoBsrXKRidcaZsSPvNQ3Fy5p7PpMt/8mltxTxMHj1Ur5NWbJdqIfpxgA=='),
    'styles_base16_solarized-light.min.css': ('/styles/base16/solarized-light.min.css',
                                              'sha512-ZW2g6Pn2pMbKSyjcA+r4Lc58kcfvOdcsTuCCTl3qz8NqVJwUtAuiN61pDoW3EEfrjwH2CPtkFWMdkzMY1idilA=='),
}
SUBS = [
    (b'<link rel="stylesheet" href="https://yandex.st/highlightjs/6.1/styles/solarized_light.min.css">',
     f'<link rel="stylesheet" href="{EXT}/styles/base16/solarized-light.min.css">'.encode()),
    (b'<script src="https://yandex.st/highlightjs/6.1/highlight.min.js"></script>',
     f'<script src="{EXT}/highlight.min.js"></script>'.encode()),
    (b'hljs.initHighlightingOnLoad();', b'hljs.highlightAll();'),
]

data = {}
for f, (path, sri) in FILES.items():
    b = open(os.path.join(src, f), 'rb').read()
    got = 'sha512-' + base64.b64encode(hashlib.sha512(b).digest()).decode()
    assert got == sri, (f, got)
    data[path] = b

pages, bad = {}, []
for root, dirs, files in os.walk('site'):
    for f in files:
        p = os.path.join(root, f)
        t = open(p, 'rb').read()
        if b'yandex.st' not in t:
            continue
        for old, new in SUBS:
            t, n = re.subn(re.escape(old), new.replace(b'\\', b'\\\\'), t)
            if n != 1:
                bad.append((p, old[:40], n))
        if b'yandex.st' in t:
            bad.append((p, 'yandex.st left'))
        pages[p] = t
print(f'{len(pages)} pages', 'BAD: ' + repr(bad) if bad else '')
if bad:
    sys.exit(1)
if APPLY:
    for path, b in data.items():
        dst = 'site' + EXT + path
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'wb').write(b)
    for p, t in pages.items():
        open(p, 'wb').write(t)
    print('applied')
else:
    print('dry run (use --apply)')
