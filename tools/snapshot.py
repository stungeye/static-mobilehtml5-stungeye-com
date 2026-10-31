"""Build site/ for mobilehtml5.stungeye.com: a static snapshot of the old PHP flat-file blog.
Usage: python3 -I tools/snapshot.py <glutton_blog checkout> <pages dir from tools/fetch_pages.sh>   (from the repo root)

* Static files: every file tracked in stungeye/glutton_blog at 8342f90 (= the live docroot, all 213 files),
  minus PHP, .htaccess, .git* files and editor swap files. The gitlink experiments/tumblr_app (an empty folder
  on the server) isn't a file; _redirects sends it to its GitHub repo.
* Rendered pages: the PHP output fetched from the origin, saved where Workers static assets'
  auto-trailing-slash serves them at the old URLs (/about -> about.html, /2012/02/10/x -> 2012/02/10/x.html),
  /atom as the extensionless file atom (content type set in _headers), and the site's own 404 page.
Refuses to run if site/ already exists."""
import os, subprocess, sys

src, pages = sys.argv[1], sys.argv[2]
COMMIT = '8342f9039348396c6fb6d80d0d0e98c5c7ced20d'
assert not os.path.exists('site'), 'site/ exists'
head = subprocess.run(['git', '-C', src, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
assert head == COMMIT, head
dirty = subprocess.run(['git', '-C', src, 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout
assert not dirty, dirty

PAGES = {   # fetched file -> site path
    '_home': 'index.html', 'about': 'about.html', 'apps': 'apps.html', 'archive': 'archive.html', 'atom': 'atom',
    'no-such-page-c4': '404.html',
    '2012__02__10__the-journey-begins': '2012/02/10/the-journey-begins.html',
    '2012__02__15__html5-mobile-web-app-tools': '2012/02/15/html5-mobile-web-app-tools.html',
    '2012__03__05__html5-tumblr-mobile-app-part-one': '2012/03/05/html5-tumblr-mobile-app-part-one.html',
    '2012__04__12__parsing-rss-with-javascript-and-phonegap': '2012/04/12/parsing-rss-with-javascript-and-phonegap.html',
    '2012__05__11__html5-tumblr-mobile-app-part-two': '2012/05/11/html5-tumblr-mobile-app-part-two.html',
    '2015__06__12__html5-native-app-part-three': '2015/06/12/html5-native-app-part-three.html',
}


def skip(rel):
    name = os.path.basename(rel)
    return (name.endswith('.php') or name == '.htaccess' or name.startswith('.git')
            or name.endswith('.swp'))


tree = subprocess.run(['git', '-C', src, 'ls-tree', '-r', '-z', COMMIT], capture_output=True, check=True).stdout
kept = skipped = links = 0
for entry in tree.split(b'\0'):
    if not entry:
        continue
    meta, rel = entry.split(b'\t', 1)
    mode, kind, _ = meta.split()
    rel = rel.decode()
    if kind == b'commit':   # gitlink (experiments/tumblr_app)
        links += 1
        continue
    assert kind == b'blob' and mode in (b'100644', b'100755'), (meta, rel)
    if skip(rel):
        skipped += 1
        continue
    data = subprocess.run(['git', '-C', src, 'cat-file', 'blob', f'{COMMIT}:{rel}'], capture_output=True, check=True).stdout
    dst = os.path.join('site', rel)
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    open(dst, 'wb').write(data)
    kept += 1

for f, dst in PAGES.items():
    dst = os.path.join('site', dst)
    assert not os.path.exists(dst), dst
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(open(os.path.join(pages, f), 'rb').read())
print(f'static files {kept}, skipped {skipped}, gitlinks {links}, rendered pages {len(PAGES)}')
