"""Remove the experiments/ demos that no blog post links to (owner decision F42, 2026-10-31).
Usage: python3 -I tools/drop_unlinked.py [--apply]   (from the repo root; dry run by default)
The posts link only to experiments/tumblr_app/ (a redirect), tumblr_app_part_1a/ and tumblr_app_part_1b/.
Everything else in experiments/ goes, and the rows for it leave the generated /experiments/ listing.
The removed files stay in stungeye/glutton_blog and in this repo's history.
Refuses to apply if a page in site/ still links to a removed path."""
import os, re, shutil, sys

APPLY = '--apply' in sys.argv[1:]
DROP = ['first/', 'phototest/', 'rss_tests/', 'second/', 'third/', 'winnipeg_news_app/', 'MeowReader.apk']
LISTING = 'site/experiments/index.html'
assert '<!-- written by tools/listings.py -->' in open(LISTING, encoding='utf-8').read()

files = []
for d in DROP:
    p = os.path.join('site/experiments', d)
    assert os.path.exists(p), p
    files += [os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs] if d.endswith('/') else [p]

listing = open(LISTING, encoding='utf-8').read()
for d in DROP:
    row = f'<tr><td><a href="{d}">{d}</a></td>'
    assert listing.count(row) == 1, d
    listing = re.sub(r'<tr><td><a href="' + re.escape(d) + r'">.*?</tr>\n', '', listing)

left = []
for r, _, fs in os.walk('site'):
    for f in fs:
        p = os.path.join(r, f)
        if p in files or not f.endswith(('.html', '.xml')) and f != 'atom':
            continue
        t = listing if p == LISTING else open(p, encoding='utf-8', errors='replace').read()
        for d in DROP:
            if re.search(r'experiments/' + re.escape(d), t):
                left.append((p, d))
print(f'{len(files)} files in {len(DROP)} entries', 'LINKED: ' + repr(left) if left else '')
if left:
    sys.exit(1)
if APPLY:
    for d in DROP:
        p = os.path.join('site/experiments', d)
        shutil.rmtree(p) if d.endswith('/') else os.remove(p)
    open(LISTING, 'w', encoding='utf-8').write(listing)
    print('applied')
else:
    print('dry run (use --apply)')
