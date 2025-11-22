from fastapi import APIRouter
from app.services.storyboard_generator import StoryboardGenerator

router = APIRouter()
generator = StoryboardGenerator()

@router.post("/generate")
async def generate_storyboard_route(payload: dict):
    outline = payload.get("outline")

    if not outline:
        return {"error": "No outline provided"}

    storyboard = generator.generate_storyboard(outline)
    return {"storyboard": storyboard}
