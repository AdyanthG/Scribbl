import os
import uuid
import replicate
import requests
from typing import Dict, List, Optional
from PIL import Image, ImageFilter
import numpy as np
from app.services.storage import StorageManager


class SketchEngine:
    """
    Final v1 SketchCourse sketch generator.

    Features:
    - Single + batch generation
    - 1024x768 FLUX generation
    - Hybrid text policy (labels OK, no paragraphs)
    - Accent color support (black primary)
    - Postprocessing for line consistency
    - Supabase upload
    """

    def __init__(self):
        token = os.getenv("REPLICATE_API_TOKEN")
        if not token:
            raise Exception("REPLICATE_API_TOKEN missing from environment")

        os.environ["REPLICATE_API_TOKEN"] = token

        self.model = "black-forest-labs/flux-schnell"
        self.storage = StorageManager()

        self.default_accents = ["blue", "red", "green", "yellow"]


    # -------------------------------------------------------------
    # Prompt Builder
    # -------------------------------------------------------------
    def build_prompt(self, description: str, accents: List[str], allow_text: bool) -> str:
        """
        Generates a consistent FLUX prompt for sketch-style images.
        """

        accent_str = ", ".join(accents) if accents else "blue, red, green, yellow"

        base = f"""
        A simple hand-drawn marker sketch.
        Resolution 1024x768.
        Thick black outlines with slight wobble.
        Accent colors used sparingly: {accent_str}.
        Clean white background. No shading. No gradients. No 3D.
        Style inspired by 1jour1question + Khan Academy.
        Medium-thick line art. Diagrammatic clarity.

        Draw: {description}.
        """

        if allow_text:
            base += " Allow short handwritten labels if they naturally belong."
        else:
            base += " Do NOT include any text or writing inside the sketch."

        base += " Remove photo realism. Remove shadows. No textures."

        return " ".join(base.split())


    # -------------------------------------------------------------
    # Postprocessing
    # -------------------------------------------------------------
    def postprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Enforces consistent "SketchCourse" style.
        """

        img = img.convert("RGB")

        # Slight blur + sharpen to mimic marker bleed
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=140, threshold=3))

        arr = np.array(img)

        # Force black lines
        black_threshold = 60
        mask = np.logical_and(
            arr[:, :, 0] < black_threshold,
            arr[:, :, 1] < black_threshold,
            arr[:, :, 2] < black_threshold,
        )
        arr[mask] = [0, 0, 0]

        # Add slight noise for hand-drawn feel
        noise = np.random.normal(0, 2, arr.shape).astype(np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)

        return Image.fromarray(arr)


    # -------------------------------------------------------------
    # Single Sketch Generation
    # -------------------------------------------------------------
    def generate(self, description: str, accents: Optional[List[str]] = None, allow_text: bool = True) -> Dict:
        """
        Generate a single sketch from a description.
        """

        accents = accents or self.default_accents
        prompt = self.build_prompt(description, accents, allow_text)

        # Retry logic for 429/Rate Limits
        max_retries = 5
        base_delay = 2

        for attempt in range(max_retries):
            try:
                output = replicate.run(
                    self.model,
                    input={
                        "prompt": prompt,
                        "num_inference_steps": 4, # Schnell model limit
                        "guidance": 3.5, # Adjusted for lower steps
                        "width": 1024,
                        "height": 768,
                    },
                )
                break # Success!
            except Exception as e:
                is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()
                if is_rate_limit and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) # 2, 4, 8, 16...
                    print(f"Rate limit hit. Retrying in {delay}s...")
                    import time
                    time.sleep(delay)
                else:
                    raise Exception(f"FLUX generation failed after {attempt+1} attempts: {str(e)}")

        img_url = output[0]
        file_id = str(uuid.uuid4())
        tmp_path = f"/tmp/{file_id}.png"

        # Download
        raw = requests.get(img_url).content
        with open(tmp_path, "wb") as f:
            f.write(raw)

        # Postprocess
        img = Image.open(tmp_path)
        img = self.postprocess_image(img)
        img.save(tmp_path)

        # Upload to Supabase
        dest = f"sketches/{file_id}.png"
        final_url = self.storage.upload_file(tmp_path, dest)

        os.remove(tmp_path)

        return {
            "id": file_id,
            "url": final_url,
            "prompt": prompt,
        }


    # -------------------------------------------------------------
    # Batch Generation
    # -------------------------------------------------------------
    # -------------------------------------------------------------
    # Batch Generation
    # -------------------------------------------------------------
    async def generate_batch(self, items: List[Dict]) -> List[Dict]:
        """
        Batch generate multiple sketches.
        FORCED SERIAL EXECUTION: Replicate is enforcing 6 req/min (1 burst).
        We must wait ~10s between requests to avoid 429.
        """
        import asyncio
        import time

        loop = asyncio.get_running_loop()
        
        # Strict Serial Execution
        sem = asyncio.Semaphore(1) 
        
        async def limited_generate(item):
            async with sem:
                desc = item.get("description")
                if not desc:
                    raise Exception("Batch item missing 'description'")

                accents = item.get("accents")
                allow_text = item.get("allow_text", True)

                # Run synchronous generate()
                # The generate() method already has retry logic, which is good.
                result = await loop.run_in_executor(None, self.generate, desc, accents, allow_text)
                
                # Enforce 6 requests per minute = 1 request every 10 seconds
                # We sleep AFTER the request to space them out.
                print("Rate limiting: Waiting 10s...")
                await asyncio.sleep(10)
                
                return result

        tasks = [limited_generate(item) for item in items]

        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        return results
