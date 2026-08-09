# JaFaFaWeb

JaFaFaWeb is a browser-based vehicle telemetry dashboard. The runtime app is intentionally concentrated in `index.html` so it can be deployed as a simple static page, while this repository also keeps lightweight documentation and a validation helper for maintainability.

## What is in this repo

- `index.html` — the full dashboard UI, styles, Google Sign-In bootstrap, telemetry fetching, filtering, and rendering logic.
- `scripts/validate-index.mjs` — a dependency-free validation helper that extracts inline scripts, runs a JavaScript syntax check, and verifies the removed telemetry graphics stay removed.

## Local usage

Open `index.html` directly in a browser, or serve the folder locally:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000/index.html`.

## Validation

Run the repository check with:

```bash
node scripts/validate-index.mjs
```

The script checks that:

1. `index.html` still contains inline JavaScript.
2. The inline JavaScript passes `node --check` syntax validation.
3. Removed telemetry graphics such as the highlights bar, injected metric cards, auto-refresh controls, and loading skeletons are not reintroduced.

## Maintenance notes

- Keep user-facing telemetry units consistent. Current speed filters and table values use `Km/h`; temperature filters and table values use `°C`.
- Keep secrets out of client-side JavaScript. Public browser code should not contain private API keys or database credentials.
- If dashboard code grows further, prefer readable inline functions over minified inline code so the single-page app remains maintainable.
