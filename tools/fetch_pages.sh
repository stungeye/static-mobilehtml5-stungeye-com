#!/bin/bash
# Fetch the PHP-rendered pages of mobilehtml5.stungeye.com straight from the old origin server,
# bypassing Cloudflare so the HTML has no zone injections (challenge script, Email Obfuscation,
# Automatic HTTPS Rewrites). Run once on 2026-10-31, before the cutover; the origin goes away after it.
# Usage: ORIGIN_IP=<old server's IP> tools/fetch_pages.sh <out-dir>     Then: python3 -I tools/snapshot.py <glutton_blog checkout> <out-dir>
set -eu
out=$1; H=mobilehtml5.stungeye.com; IP=$ORIGIN_IP
mkdir -p "$out"
# The routes in glutton_blog's .htaccess / index.php: home, about, apps, archive, atom, one per post, and the 404 page.
for p in / /about /apps /archive /atom \
         /2012/02/10/the-journey-begins /2012/02/15/html5-mobile-web-app-tools \
         /2012/03/05/html5-tumblr-mobile-app-part-one /2012/04/12/parsing-rss-with-javascript-and-phonegap \
         /2012/05/11/html5-tumblr-mobile-app-part-two /2015/06/12/html5-native-app-part-three \
         /no-such-page-c4; do
  f=$(echo "${p#/}" | sed 's#/#__#g'); [ -z "$f" ] && f=_home
  curl -sS --resolve $H:443:$IP -A curl/8.5.0 -o "$out/$f" -w "%{http_code} %{content_type} %{size_download} $p\n" "https://$H$p"
  sleep 0.3
done
