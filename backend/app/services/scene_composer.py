import os
import uuid
import requests
import asyncio
from typing import List, Dict
from app.services.scene_model import Scene
from app.services.sketch_engine import SketchEngine
from app.services.tts_engine import TTSEngine

class SceneComposer:
    def __init__(self):
        self.sketch_engine = SketchEngine()
        self.tts_engine = TTSEngine()

    async def build_scenes(self, storyboard: Dict) -> List[Scene]:
        """
        Convert storyboard JSON into Scene objects.
        Generates sketches in parallel and downloads them.
        Generates audio for each scene.
        """
        
        # 1. Prepare batch items for SketchEngine
        batch_items = []
        for s in storyboard["scenes"]:
            batch_items.append({
                "description": s.get("visual_prompt"),
                "accents": s.get("accents", []),
                "allow_text": True # Default to true for now
            })
            
        # 2. Generate all sketches in parallel
        print(f"Generating {len(batch_items)} sketches...")
        sketches = await self.sketch_engine.generate_batch(batch_items)
        
        scenes = []
        
        # 3. Map back to scenes and generate audio
        for i, s in enumerate(storyboard["scenes"]):
            sketch_data = sketches[i]
            sketch_url = sketch_data["url"]
            
            file_id = str(uuid.uuid4())
            tmp_path = f"/tmp/sketch_{file_id}.png"
            
            raw = requests.get(sketch_url).content
            with open(tmp_path, "wb") as f:
                f.write(raw)
            
            # Generate Audio
            narration = s.get("narration", "")
            audio_path = None
            if narration:
                audio_path = self.tts_engine.generate_audio(narration)

            scene = Scene(
                sketch_path=tmp_path,
                text=s.get("text_overlay", ""),
                duration=s.get("duration_seconds", 4),
                motion="zoom_in", 
                audio_path=audio_path,
                narration=narration
            )
            scenes.append(scene)
            
        return scenes
