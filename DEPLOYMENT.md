# Deploying RentScout

Backend + Postgres on **Railway**, frontend on **Vercel**. Both free tiers are
fine for this app. Total time: roughly 30–45 minutes.

The order matters: backend first, because the frontend needs the backend's URL
at **build time**.

---

## Part 1 — Backend on Railway

1. Go to [railway.app](https://railway.app) → sign in with your GitHub account.
2. **New Project → Deploy from GitHub repo** → pick `rentscout-ai`.
   - When asked which branch, choose the branch you deploy from
     (`feature/rentscout-v3` until it merges to `main`, then switch).
   - Railway detects the root `Dockerfile` automatically.
3. In the same project: **+ New → Database → PostgreSQL.**
4. Open the app service → **Variables** and add:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (reference the DB service) |
   | `SECRET_KEY` | generate: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |
   | `ALLOWED_ORIGINS` | `http://localhost:3000` for now — updated in Part 3 |
   | `OPENAI_API_KEY` | optional; only `/chat` uses it. Leave unset to start. |

5. Open the service → **Settings → Networking → Generate Domain.**
   You get something like `rentscout-api-production.up.railway.app`.
   **This is your API URL — you need it in Part 2.**
6. Wait for the deploy to go green, then check:
   `https://<your-api-url>/` should return `{"message": "RentScout API Running"}`.

### Seed the production database

In the Railway service → three-dot menu → **Command line** (or install the
Railway CLI locally and use `railway run`):

```
python -m backend.seed_data --reset
```

You should see `Seeded 123 demo listings across 19 areas`.

---

## Part 2 — Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → sign in with GitHub.
2. **Add New → Project** → import `rentscout-ai`.
3. **Root Directory: `frontend`** ← the one setting people miss.
   Framework preset: Next.js (auto-detected). Leave build settings alone —
   Vercel does not use the Dockerfile, and that's fine.
4. Under **Environment Variables**, add:

   | Variable | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://<your-api-url-from-part-1>` — https, no trailing slash |

5. **Deploy.** You get `https://rentscout-<something>.vercel.app`.

---

## Part 3 — Connect them

The frontend now calls the API from the browser, so the API must allow the
Vercel origin:

1. Back in Railway → app service → **Variables** → set

   ```
   ALLOWED_ORIGINS=https://<your-vercel-url>,http://localhost:3000
   ```

   (comma-separated, no spaces, no trailing slashes — keep localhost so local
   dev still works against the deployed API if you want).
2. Railway redeploys automatically on the variable change.

---

## Part 4 — Verify

Open the Vercel URL and check:

- [ ] Landing page shows CMHC vacancy numbers (not the "unavailable" fallback —
      if you see that, `ALLOWED_ORIGINS` or `NEXT_PUBLIC_API_URL` is wrong)
- [ ] `/search` returns ranked sample listings for a $2,500 budget
- [ ] `/market` renders the vacancy chart for Vancouver CMA
- [ ] `/analyze` scores the "Try a suspicious listing" example HIGH
- [ ] `/budget` verdict updates as sliders move

Common failures:

| Symptom | Cause |
|---|---|
| "Market data is unavailable" on landing | Browser can't reach the API: check `NEXT_PUBLIC_API_URL` (Vercel) and CORS `ALLOWED_ORIGINS` (Railway) |
| CORS errors in browser console | Vercel URL missing from `ALLOWED_ORIGINS`, or has a trailing slash |
| API 500s on every DB route | `DATABASE_URL` not referencing the Postgres service |
| Search returns 0 results | Seed step skipped — run it (Part 1) |
| Changed `NEXT_PUBLIC_API_URL` but nothing changed | It's baked at build time — redeploy the frontend after changing it |

---

## Redeploys

Both platforms redeploy automatically on push to the connected branch.
`NEXT_PUBLIC_API_URL` only takes effect on a frontend **rebuild**.
