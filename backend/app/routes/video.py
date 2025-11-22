from fastapi import APIRouter
from app.services.video_renderer import VideoRenderer

router = APIRouter()
renderer = VideoRenderer()

@router.get("/test")
def video_test():
    out = renderer.render_scene(
        image_path="backend/tests/assets/test.png",
        audio_path=None,
        text="Hello SketchCourse",
        duration=5,
        motion="zoom_in"
    )
    return {"video_path": out}
