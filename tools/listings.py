"""Write a plain listing index.html in each folder that Apache auto-indexed on the old server (owner decision F41).
Usage: python3 -I tools/listings.py [--apply]   (from the repo root; dry run by default)
Covers the folders of the old docroot (stungeye/glutton_blog) that are in site/ and have no index.html, except
experiments/first/boiler/ and below (its .htaccess had Options -Indexes, so Apache answered 403 there).
Folders this repo added (_ext/, the post date folders) get none: they weren't folders on the old server.
experiments/tumblr_app/ is listed in /experiments/ but answers with a redirect (_redirects)."""
import html, os, sys

APPLY = '--apply' in sys.argv[1:]
MARK = '<!-- written by tools/listings.py -->'
SKIP_TOP = {'_ext', '2012', '2015'}
NO_INDEXES = 'experiments/first/boiler'
EXTRA = {'experiments': [('tumblr_app/', '-')]}   # gitlink on the old server; now a redirect to its GitHub repo


def size(n):
    for unit in ('', 'K', 'M'):
        if n < 1024 or unit == 'M':
            return f'{n:.0f}{unit}' if unit == '' or n >= 10 else f'{n:.1f}{unit}'
        n /= 1024


def page(rel, rows):
    title = f'Index of /{rel}/'
    lines = [f'<tr><td><a href="{html.escape(href, quote=True)}">{html.escape(href)}</a></td><td>{s}</td></tr>' for href, s in rows]
    return f'''<!DOCTYPE html>
{MARK}
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><h1>{html.escape(title)}</h1>
<table><tr><th>Name</th><th>Size</th></tr>
<tr><td><a href="../">Parent Directory</a></td><td>-</td></tr>
{chr(10).join(lines)}
</table>
<p><a href="/">Mobile HTML5 Development</a></p>
</body></html>
'''


todo = {}
for root, dirs, files in os.walk('site'):
    dirs.sort()
    rel = os.path.relpath(root, 'site').replace(os.sep, '/')
    if rel == '.':
        dirs[:] = [d for d in dirs if d not in SKIP_TOP]
        continue
    if rel == NO_INDEXES or rel.startswith(NO_INDEXES + '/'):
        continue
    if 'index.html' in files:
        continue
    rows = [(d + '/', '-') for d in dirs] + EXTRA.get(rel, [])
    rows = sorted(rows) + [(f, size(os.path.getsize(os.path.join(root, f)))) for f in sorted(files)]
    todo[os.path.join(root, 'index.html')] = page(rel, rows)
for p in todo:
    print(p)
print(f'{len(todo)} listings')
if APPLY:
    for p, text in todo.items():
        assert not os.path.exists(p), p
        open(p, 'w', encoding='utf-8').write(text)
    print('applied')
else:
    print('dry run (use --apply)')
