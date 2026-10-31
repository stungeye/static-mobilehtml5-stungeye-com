"""Remove the Google AdSense slots from site/ (owner decision F41, extending F11's GA strip).
Usage: python3 -I tools/strip_adsense.py [--apply]   (from the repo root; dry run by default)
Each slot is a container (<section id="google_sidebar"> or <div id="google_above_comments">) holding one inline
script of google_ad_* settings and the show_ads.js loader. The container goes, with its leading indent and line end.
Refuses to apply if an inline block holds anything else, or if any AdSense reference is left."""
import os, re, sys

APPLY = '--apply' in sys.argv[1:]
WS = rb'[ \t\r\n]*'
SETTINGS = rb'<script type="text/javascript"><!--' + rb'((?:(?!</script>).)*)' + rb'</script>'
LOADER = rb'<script type="text/javascript"' + WS + rb'src="https://pagead2\.googlesyndication\.com/pagead/show_ads\.js">' + WS + rb'</script>'
SLOT = re.compile(rb'[ \t]*<(section|div) id="google_(?:sidebar|above_comments)">' + WS + SETTINGS + WS + LOADER + WS +
                  rb'</\1>[ \t]*\r?\n?', re.S)
OK = re.compile(rb'\A(?:' + WS + rb'(?:google_ad_client = "ca-pub-8119657288856342";|google_ad_slot = "\d+";|'
                rb'google_ad_(?:width|height) = \d+;|/\* [\w ]+ \*/|//-->))*' + WS + rb'\Z')
LEFT = re.compile(rb'googlesyndication|google_ad_|ca-pub-|adsbygoogle')

total, bad = 0, []
for root, dirs, files in os.walk('site'):
    for f in files:
        p = os.path.join(root, f)
        data = open(p, 'rb').read()
        if not LEFT.search(data):
            continue
        n = 0
        def drop(m):
            global n
            if not OK.match(m.group(2)):
                bad.append((p, m.group(2)[:200]))
            n += 1
            return b''
        new = SLOT.sub(drop, data)
        if LEFT.search(new):
            bad.append((p, 'AdSense reference left'))
        print(f'{p}: {n} slot(s)')
        total += n
        if APPLY and not bad:
            open(p, 'wb').write(new)
print(f'{total} slots', 'BAD:' if bad else '', *bad, sep='\n' if bad else ' ')
if bad:
    sys.exit(1)
print('applied' if APPLY else 'dry run (use --apply)')
