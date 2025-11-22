from fastapi import APIRouter
from app.services.sketch_engine import SketchEngine

router = APIRouter()
engine = SketchEngine()

@router.post("/generate")
async def generate_single(payload: dict):
    description = payload.get("description")
    accents = payload.get("accents")
    allow_text = payload.get("allow_text", True)

    if not description:
        return {"error": "Missing 'description'"}

    result = engine.generate(description, accents, allow_text)
    return {"sketch": result}


@router.post("/generate_batch")
async def generate_batch(payload: dict):
    items = payload.get("items")
    if not items:
        return {"error": "Missing 'items' array"}

    out = await engine.generate_batch(items)
    return {"sketches": out}
