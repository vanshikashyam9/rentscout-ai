# Deploying RentScout

Backend + Postgres on **Render**, frontend on **Vercel**. Both free tiers are
fine for this app. Total time: roughly 20–30 minutes.

The order matters: backend first, because the frontend needs the backend's URL
at **build time**.

---

## Part 1 — Backend on Render

The repo has a `render.yaml` Blueprint that creates the API and its database
together.

1. Go to [render.com](https://render.com) → sign in with your GitHub account.
2. **New → Blueprint** → pick `rentscout-ai`, branch `main`.
3. Render reads `render.yaml` and shows two resources: `rentscout-api` (Docker
   web service) and `rentscout-db` (Postgres). `DATABASE_URL` and `SECRET_KEY`
   are filled in automatically. It asks for two values:

   | Variable | Value |
   |---|---|
   | `ALLOWED_ORIGINS` | `http://localhost:3000` for now — updated in Part 3 |
   | `OPENAI_API_KEY` | optional; only `/chat` uses it. Leave blank to start. |

4. **Apply.** The first Docker build takes a few minutes.
5. Your API URL is shown at the top of the `rentscout-api` page, something like
   `https://rentscout-api.onrender.com`. **You need it in Part 2.**
6. Check `https://<your-api-url>/` returns `{"message": "RentScout API Running"}`.

The API creates its tables and seeds demo data on first boot when the database
is empty — no manual seed step.

**Free-tier caveats:** the free web service sleeps after ~15 minutes idle, so
the first request after a quiet spell takes 30–60 seconds. The free Postgres
database expires 30 days after creation — upgrade it or recreate it before
then.

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

The frontend calls the API from the browser, so the API must allow the Vercel
origin:

1. Back in Render → `rentscout-api` → **Environment** → set

   ```
   ALLOWED_ORIGINS=https://<your-vercel-url>,http://localhost:3000
   ```

   (comma-separated, no spaces — keep localhost so local dev still works
   against the deployed API if you want).
2. **Save Changes.** Render redeploys the API.

---

## Part 4 — Verify

Open the Vercel URL and check:

- [ ] Landing page shows CMHC vacancy numbers (not the "unavailable" fallback —
      if you see that, `ALLOWED_ORIGINS` or `NEXT_PUBLIC_API_URL` is wrong)
- [ ] `/market` renders the vacancy chart for Vancouver CMA
- [ ] `/analyze` scores the "Try a suspicious listing" example HIGH
- [ ] `/budget` verdict updates as sliders move

Common failures:

| Symptom | Cause |
|---|---|
| "Market data is unavailable" on landing | Browser can't reach the API: check `NEXT_PUBLIC_API_URL` (Vercel) and `ALLOWED_ORIGINS` (Render) |
| CORS errors in browser console | Vercel URL missing from `ALLOWED_ORIGINS` |
| First load hangs ~1 minute | Free Render service waking from sleep — expected |
| API 500s on every DB route | `DATABASE_URL` missing, or the free database expired |
| Changed `NEXT_PUBLIC_API_URL` but nothing changed | It's baked at build time — redeploy the frontend after changing it |

---

## Custom domain (optional)

To serve the site at your own domain (e.g. `rentscout.ai`): Vercel → project →
**Settings → Domains** → add it and follow the DNS records it shows at your
registrar. Then add `https://<your-domain>` to `ALLOWED_ORIGINS` on Render.

---

## Redeploys

Both platforms redeploy automatically on push to `main`.
`NEXT_PUBLIC_API_URL` only takes effect on a frontend **rebuild**.
