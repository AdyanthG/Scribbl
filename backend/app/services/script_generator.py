import os
import json
from typing import Dict
from openai import OpenAI

class ScriptGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"

    def generate_script(self, text: str, target_duration_minutes: int = 3) -> Dict:
        """
        Generates a scene-by-scene video script from the provided text.
        """
        
        SYSTEM_PROMPT = """
        You are an expert educational content creator for TikTok/YouTube Shorts.
        Your goal is to turn dense academic text into a fast-paced, visually engaging video script.
        
        STYLE GUIDE:
        - **Fast Paced:** No long monologues. Change visuals every 3-5 seconds.
        - **Visual First:** The narration should support the visual, not the other way around.
        - **Simple Language:** Explain like I'm 12. Use analogies.
        - **Sketch Style:** The visuals will be hand-drawn sketches. Keep prompts simple and iconic.
        
        OUTPUT FORMAT (JSON):
        {
            "title": "Catchy Title",
            "scenes": [
                {
                    "id": 1,
                    "narration": "Spoken text here...",
                    "visual_prompt": "Description of the sketch to draw...",
                    "text_overlay": "Short text on screen (optional)",
                    "estimated_duration": 4
                }
            ]
        }
        """

        USER_PROMPT = f"""
        Source Text:
        {text[:20000]}  # Limit context window if needed

        Target Duration: {target_duration_minutes} minutes.
        Create a script that explains the core concepts efficiently.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"Error generating script: {e}")
            raise e
