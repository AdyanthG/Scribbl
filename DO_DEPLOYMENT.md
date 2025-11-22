# 🌊 DigitalOcean Deployment (GitHub Student Pack)

This is the **"Pro"** way to deploy. It's free with your student credits ($200) and much faster than Render's free tier.

---

## Phase 1: Get the Credits 💰
1.  Go to [education.github.com/pack](https://education.github.com/pack).
2.  Sign up/Login with GitHub.
3.  Search for **DigitalOcean** and click the link to claim your $200 credit.
4.  Create a DigitalOcean account.

---

## Phase 2: Create the "App Platform" 🚀
DigitalOcean has a service called "App Platform" which is exactly like Render/Heroku (easy, no server management).

1.  **Go to DigitalOcean Dashboard** -> **Apps** (on the left) -> **Create App**.
2.  **Service Provider:** Select **GitHub**.
3.  **Repository:** Select your `scribbl` repo.
4.  **Source Directory:** Select `/backend`.
    *   *Note:* It should auto-detect the Dockerfile.
5.  **Resources:**
    *   Since you have $200, pick the **Basic** plan ($5/mo).
    *   This gives you 512MB RAM and 1 vCPU. Always on. No cold starts.
6.  **Environment Variables:**
    *   Click "Edit" next to Environment Variables.
    *   Add all your secrets (`OPENAI_API_KEY`, `SUPABASE_URL`, etc.).
7.  **Next** -> **Create Resources**.

---

## Phase 3: Frontend Connection 🔗
1.  Once the DigitalOcean app is live, it will give you a URL (e.g., `https://scribbl-backend-xyz.ondigitalocean.app`).
2.  Go to your **Vercel** project (Frontend).
3.  Update the `destination` in `vercel.json` (or your environment variable) to point to this new DigitalOcean URL.
4.  Redeploy Vercel.

---

### Why this wins:
*   **Cost:** $0 (covered by credits for ~1-2 years).
*   **Speed:** No sleeping. Instant API responses.
*   **Scale:** If you go viral, you can just click "Upgrade" to a bigger server using your credits.
