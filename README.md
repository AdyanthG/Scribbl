# Scribbl ✏️

**Turn boring PDFs into engaging, hand-drawn sketch videos instantly.**

Scribbl is an AI-powered study tool that transforms static course materials (PDFs, textbooks, notes) into dynamic, visual explanations. It uses a pipeline of LLMs and image generation models to script, storyboard, and animate educational content.

![Scribbl Demo](https://github.com/user-attachments/assets/placeholder-image.png)

## 🚀 Features

*   **PDF to Video:** Upload any PDF and get a narrated sketch video in minutes.
*   **AI Storytelling:** GPT-4o breaks down complex topics into simple, visual narratives.
*   **Hand-Drawn Aesthetic:** Custom FLUX model generates consistent, sketchy-style illustrations.
*   **Ken Burns Effect:** Dynamic camera movements bring static sketches to life.
*   **Study Gallery:** Save and manage your generated sketches.

## 🛠️ Tech Stack

### Frontend
*   **Framework:** Next.js 14 (App Router)
*   **Styling:** Tailwind CSS + Framer Motion
*   **Deployment:** Vercel

### Backend
*   **Framework:** FastAPI (Python)
*   **AI Orchestration:** OpenAI (Script/TTS) + Replicate (FLUX Image Gen)
*   **Video Processing:** FFmpeg
*   **Storage:** Supabase
*   **Deployment:** Render / DigitalOcean (Docker)

## 📦 Installation

### Prerequisites
*   Node.js 18+
*   Python 3.11+
*   FFmpeg installed locally

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/scribbl.git
cd scribbl
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `/backend`:
```env
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SUPABASE_BUCKET=sketchcourse
```

Run the server:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to start scribbling!

## 🚢 Deployment

### Frontend (Vercel)
1.  Push to GitHub.
2.  Import `frontend` directory to Vercel.
3.  Add environment variables if needed.

### Backend (Render/DigitalOcean)
1.  Push to GitHub.
2.  Deploy `backend` directory using the included `Dockerfile`.
3.  Set environment variables in your dashboard.

## 📄 License

MIT License. Built with ❤️ by the Scribbl Team at Vanderbilt.
