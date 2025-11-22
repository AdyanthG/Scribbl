from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import pdf, outline, storyboard, sketches, video, projects


app = FastAPI(title="SketchCourse Backend")

# Allow local dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
app.include_router(outline.router, prefix="/outline", tags=["outline"])
app.include_router(storyboard.router, prefix="/storyboard", tags=["storyboard"])
app.include_router(sketches.router, prefix="/sketches", tags=["sketches"])
app.include_router(video.router, prefix="/video", tags=["video"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])

@app.get("/")
def root():
    return {"status": "SketchCourse backend running"}
