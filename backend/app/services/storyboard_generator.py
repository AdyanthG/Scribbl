import os
import json
from typing import Dict, List, Union
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class StoryboardGenerator:

    def generate_storyboard(self, input_data: Union[Dict, str]) -> Dict:
        """
        Generates a scene-by-scene storyboard from either an outline (dict) or raw text (str).
        """
        
        SYSTEM_MSG = """
        You are an expert educational content creator for TikTok/YouTube Shorts.
        Your goal is to turn the input content into a fast-paced, visually engaging video script.

        STYLE GUIDE:
        - **Fast Paced:** No long monologues. Change visuals every 3-5 seconds.
        - **Visual First:** The narration should support the visual, not the other way around.
        - **Simple Language:** Explain like I'm 12. Use analogies.
        - **Sketch Style:** The visuals will be hand-drawn sketches. Keep prompts simple and iconic.
        - **Colors:** Use black (primary), blue, red, green, yellow (accents).

        OUTPUT FORMAT (JSON):
        {
            "title": "Catchy Title",
            "scenes": [
                {
                    "id": 1,
                    "narration": "Spoken text here...",
                    "visual_prompt": "Description of the sketch to draw...",
                    "text_overlay": "Short text on screen (optional)",
                    "accents": ["blue", "red"],
                    "duration_seconds": 4
                }
            ]
        }
        """

        content_str = json.dumps(input_data) if isinstance(input_data, dict) else input_data[:15000]

        USER_MSG = f"""
        Create a short video storyboard from this content:
        
        {content_str}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_MSG},
                    {"role": "user", "content": USER_MSG},
                ],
                temperature=0.7
            )

            raw = response.choices[0].message.content
            return json.loads(raw)
        except Exception as e:
            print(f"Error generating storyboard: {e}")
            # Fallback for JSON parsing errors
            if 'raw' in locals():
                try:
                    json_str = raw[raw.index("{"): raw.rindex("}")+1]
                    return json.loads(json_str)
                except:
                    pass
            raise e
