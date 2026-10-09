# nopprut.pages.dev — portfolio site source

Static portfolio site, built by a single Python script (no framework). Deployed to Cloudflare Pages.

## Build

```
pip install pillow requests blake3 python-dotenv
python build.py
```

Generates `dist/` — all pages, `/assets/cat.png`, `og.png`, `robots.txt`, `sitemap.xml`, `llms.txt`, and the security report PDFs (copied in from a sibling project folder if present; see `build.py`'s `SECURITY_SRC`).

Project data (featured work, more projects, tech stack) lives directly in `build.py` as plain Python lists (`FEATURED`, `MORE`, `STACK`) — edit those to add/update portfolio items.

`config.json` holds the deploy-specific bits that shouldn't be hardcoded (base URL, contact links) — see the docstring at the top of `build.py` for its shape.

## Deploy

Direct-upload to Cloudflare Pages (no `wrangler`, no git integration):

```
CLOUDFLARE_ACCOUNT_ID=... CLOUDFLARE_API_TOKEN=... python deploy.py dist nopprut
```

`deploy.py` lives in the sibling `products/shop-tools/fee-reader/` folder of the main project and is shared across this project's Cloudflare Pages deployments — it speaks the same upload protocol `wrangler` uses (upload-token → check-missing → upload → upsert-hashes → create deployment).
