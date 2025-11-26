# Local Testing Guide for SketchCourse

Follow these steps to run the application locally and test the video generation pipeline.

## 1. Environment Setup

Ensure your `backend/.env` file contains the following keys:

```bash
REPLICATE_API_TOKEN=r8_...
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
```

> [!IMPORTANT]
> Make sure `SUPABASE_SERVICE_KEY` is the **service_role** key, not the anon key, as the backend needs write access to Storage.

## 2. Start the Backend

Open a terminal and run:

```bash
cd backend
# Activate your virtual environment if you have one
# source venv/bin/activate 

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend should start at `http://127.0.0.1:8000`.

## 3. Start the Frontend

Open a **new** terminal window and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend should start at `http://localhost:3000`.

## 4. Trigger Video Generation

1.  Open `http://localhost:3000` in your browser.
2.  Upload a PDF file.
3.  The frontend will call the backend to start the process.
4.  Monitor the **backend terminal** logs. You should see:
    - `[<id>] extracting...`
    - `[<id>] scripting...`
    - `[<id>] storyboard...`
    - `[<id>] scenes...` (This is where parallel generation happens)
    - `[<id>] rendering...` (This is where parallel rendering happens)
    - `[<id>] DONE! Video URL: ...`

## 5. Verify Performance

Check the timestamps in the backend logs to see how fast the "scenes" and "rendering" steps complete.

- **Scenes**: Should be fast (parallel sketch + audio generation).
- **Rendering**: Should be faster than before (concurrency 8).

## Troubleshooting

- **Missing Dependencies**: Run `pip install -r requirements.txt` in backend and `npm install` in frontend.
- **API Errors**: Check your `.env` keys.
- **FFmpeg Error**: Ensure `ffmpeg` is installed on your system (`brew install ffmpeg` on macOS).
