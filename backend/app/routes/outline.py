from fastapi import APIRouter
from app.services.outline_generator import OutlineGenerator

router = APIRouter()
generator = OutlineGenerator()

@router.post("/generate")
async def generate_outline(payload: dict):
    chunks = payload.get("chunks", [])
    if not chunks:
        return {"error": "No chunks provided"}
    
    if not isinstance(chunks, list):
        return {"error": "chunks must be a list of strings"}


    outline = generator.generate_outline(chunks)
    return {"outline": outline}
