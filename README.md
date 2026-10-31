# static-mobilehtml5-stungeye-com

A static snapshot of **[mobilehtml5.stungeye.com](https://mobilehtml5.stungeye.com)**, "Mobile HTML5 Development": Kyle Geske's 2012–2015 blog about building mobile apps with HTML5, CSS3, JavaScript and PhoneGap, plus the demo apps in `experiments/`.

The site used to run on a small PHP flat-file blog engine, [stungeye/glutton_blog](https://github.com/stungeye/glutton_blog), on a VPS. That repo keeps the PHP source; this one holds what is served, as plain files.

## What's in `site/`

* **Static files:** every file of `glutton_blog` at `8342f90` (the old server's docroot), minus PHP, `.htaccess`, `.git*` and editor swap files.
* **The pages the PHP rendered**, fetched from the old server on 2026-10-31 and saved so they keep their URLs: `/` (`index.html`), `/about`, `/apps`, `/archive`, the six posts (`/YYYY/MM/DD/slug` → `YYYY/MM/DD/slug.html`), the Atom feed at `/atom` (an extensionless file; `_headers` gives it `text/xml`), and the site's own 404 page.
* **Changes from the old site**, each made by a script in `tools/`:
  * `tools/strip_adsense.py`: the Google AdSense slots are removed. (Google Analytics and Disqus were already off.)
  * `tools/mirror_fonts.py`: the Droid Serif web font is served from `site/_ext/` instead of Google Fonts.
  * `tools/listings.py`: folders that the old server listed automatically get a plain `index.html` listing (not under `experiments/first/boiler/`, which the old server didn't list).
  * `tools/drop_unlinked.py`: the demos in `experiments/` that no post links to are removed (`first/`, `second/`, `third/`, `phototest/`, `rss_tests/`, `winnipeg_news_app/`, `MeowReader.apk`). Only `tumblr_app_part_1a/` and `tumblr_app_part_1b/` stay. The removed files are still in `glutton_blog` and in this repo's history.
  * `site/_redirects`: `/experiments/tumblr_app/` was a git submodule (an empty folder on the old server), so it now redirects to [stungeye/HTML5-Tumblr-Mobile-App](https://github.com/stungeye/HTML5-Tumblr-Mobile-App).
* **Not carried over:** the PHP, including the two `rss.php` feed proxies (their demos are removed too).

Rebuild from scratch (needs the old origin, so this was a one-time run): `tools/fetch_pages.sh <dir>`, then `python3 -I tools/snapshot.py <glutton_blog checkout> <dir>`, then each tool with `--apply` in the order above.

## Hosting

Served from **Cloudflare Workers static assets** (Free plan; the largest file is well under the 25 MiB limit).

* **Worker:** `static-mobilehtml5-stungeye-com`, account `Stungeye@gmail.com's Account`.
* **Deploy:** Workers Builds: every push to `main` deploys. No build command; deploy command `npx wrangler deploy`. Only `site/` is uploaded; `_redirects` and `_headers` are read by Cloudflare and not served.
* **Serving:** `html_handling: auto-trailing-slash` (`/about` serves `about.html`; `/about/` 307s to `/about`; `/experiments` 307s to `/experiments/`), `not_found_handling: 404-page` (`site/404.html`).
* **workers.dev:** on until the cutover is checked. Per-version preview URLs are off.
* **Route:** none yet. The cutover adds `mobilehtml5.stungeye.com/*` on zone `stungeye.com`; rollback is deleting the route.
