# 🚀 Scribbl Deployment Guide

Since I cannot access your external accounts directly, here is the exact step-by-step guide to launch **Scribbl** to the world.

---

## Part 1: Backend (The Engine) 🛠️
We will use **Render** (easiest) or **Railway**.
*Prerequisite:* Push your code to a GitHub repository.

1.  **Create a New Web Service** on [Render.com](https://render.com).
2.  **Connect your GitHub repo.**
3.  **Settings:**
    *   **Root Directory:** `backend`
    *   **Runtime:** `Docker` (It will automatically find the Dockerfile I created).
4.  **Environment Variables (CRITICAL):**
    Copy these from your local `.env` file:
    *   `OPENAI_API_KEY`
    *   `REPLICATE_API_TOKEN`
    *   `SUPABASE_URL`
    *   `SUPABASE_SERVICE_KEY`
    *   `SUPABASE_BUCKET` (set to `sketchcourse`)
5.  **Click "Create Web Service".**
    *   Wait for it to build. Once done, it will give you a URL like `https://scribbl-backend.onrender.com`.
    *   **Copy this URL.**

---

## Part 2: Frontend (The Face) 🎨
We will use **Vercel**.

1.  **Go to [Vercel.com](https://vercel.com) and "Add New Project".**
2.  **Import the same GitHub repo.**
3.  **Settings:**
    *   **Root Directory:** `frontend` (Vercel will auto-detect Next.js).
4.  **Environment Variables:**
    *   No secrets needed here unless you added some.
    *   **IMPORTANT:** We need to tell the frontend where the backend is.
    *   Open `frontend/vercel.json` in your code.
    *   Update the destination URL:
        ```json
        "destination": "https://YOUR-RENDER-URL.onrender.com/:path*"
        ```
    *   *Alternative:* You can also set a `NEXT_PUBLIC_API_URL` env var if we refactor the fetch calls, but the `vercel.json` rewrite is easier for now.
5.  **Deploy.**

---

## Part 3: Final Polish ✨
1.  **Domain:** On Vercel, go to Settings > Domains and add `scribbl.study`.
2.  **Test:** Go to your new URL and try to create a sketch!

---

### 🆘 Troubleshooting
*   **Backend fails to build?** Check the logs on Render. It's usually a missing requirement.
*   **Frontend can't connect?** Check the `vercel.json` rewrite rule or the Network tab in your browser.
