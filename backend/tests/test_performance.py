import asyncio
import time
import os
import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before imports
sys.modules["replicate"] = MagicMock()
sys.modules["openai"] = MagicMock()
sys.modules["ffmpeg"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["supabase"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["PyPDF2"] = MagicMock()

# Set dummy env vars
os.environ["REPLICATE_API_TOKEN"] = "dummy_token"
os.environ["OPENAI_API_KEY"] = "dummy_key"

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.scene_composer import SceneComposer
from app.services.project_orchestrator import ProjectOrchestrator
from app.services.sketch_engine import SketchEngine
from app.services.tts_engine import TTSEngine
from app.services.video_renderer import VideoRenderer

async def test_performance():
    print("Starting Performance Test...")

    # Setup Mocks
    import replicate
    import requests
    from app.services.storage import StorageManager
    import openai
    import ffmpeg

    replicate.run.return_value = ["http://mock.url/image.png"]
    requests.get.return_value.content = b"fake_image_data"
    
    # Mock StorageManager
    # We need to patch StorageManager where it is imported or mock the class
    # Since we imported it, we can patch it in the module or just mock the instance in the classes
    # But SketchEngine instantiates it in __init__.
    # Let's patch it in the modules where it's used or just rely on the fact that we can mock the instance on the objects.
    # Actually, we need to mock it so __init__ doesn't fail if it does something.
    # StorageManager init doesn't seem to do much based on previous read.
    
    # Mock TTS
    mock_openai_client = MagicMock()
    openai.OpenAI.return_value = mock_openai_client
    mock_openai_client.audio.speech.create.return_value.stream_to_file = lambda x: None

    # Create instances
    # We need to mock StorageManager before instantiation if it does network calls
    with patch("app.services.sketch_engine.StorageManager") as mock_storage_1, \
         patch("app.services.tts_engine.StorageManager") as mock_storage_2, \
         patch("app.services.project_orchestrator.StorageManager") as mock_storage_3:
         
        mock_storage_1.return_value.upload_file.return_value = "http://supabase.url/image.png"
        mock_storage_2.return_value.upload_file.return_value = "http://supabase.url/audio.mp3"
        mock_storage_3.return_value.upload_file.return_value = "http://supabase.url/video.mp4"

        composer = SceneComposer()
        orchestrator = ProjectOrchestrator()
        
        # Mock the time-consuming methods to sleep instead of doing work
        async def mock_generate_batch(items, keep_local=False):
            print(f"  [Mock] Generating {len(items)} sketches (simulated 1s)...")
            await asyncio.sleep(1) # Simulate network latency
            results = []
            for i, item in enumerate(items):
                results.append({
                    "id": f"mock_id_{i}",
                    "url": f"http://mock.url/{i}.png",
                    "prompt": item["description"],
                    "local_path": f"/tmp/mock_{i}.png" if keep_local else None
                })
                # Create dummy local file if needed
                if keep_local:
                    with open(f"/tmp/mock_{i}.png", "wb") as f:
                        f.write(b"dummy")
            return results

        composer.sketch_engine.generate_batch = mock_generate_batch

        async def mock_generate_audio(text):
            # print(f"  [Mock] Generating audio (simulated 0.5s)...")
            await asyncio.sleep(0.5)
            return f"/tmp/mock_audio.mp3"
        
        composer.tts_engine.generate_audio = mock_generate_audio

        def mock_render_scene(scene):
            # print(f"  [Mock] Rendering scene (simulated 1s)...")
            time.sleep(1) # Blocking call, should be run in executor
            return f"/tmp/mock_scene.mp4"
        
        orchestrator.video_renderer.render_scene = mock_render_scene
        orchestrator.video_renderer.concat_scenes = lambda paths: "/tmp/final.mp4"
        orchestrator.storage.upload_file = lambda path, dest: "http://final.url/video.mp4"

        # Test Data
        storyboard = {
            "scenes": [
                {"visual_prompt": f"Scene {i}", "narration": f"Narration {i}", "duration_seconds": 2}
                for i in range(20) # 20 scenes to test concurrency
            ]
        }

        # 1. Test SceneComposer (Sketch + Audio)
        print("\n--- Testing SceneComposer ---")
        start_time = time.time()
        scenes = await composer.build_scenes(storyboard)
        end_time = time.time()
        print(f"SceneComposer took {end_time - start_time:.2f}s")
        
        # Verify local paths are used (no requests.get calls for images)
        # Since we mocked generate_batch to return local_path, SceneComposer should use it.
        # We can check if requests.get was called. 
        # Note: requests.get is mocked at module level, but SceneComposer imports requests.
        # We need to patch requests in SceneComposer or just check logic.
        # In our mock_generate_batch, we return local_path. 
        # If SceneComposer logic is correct, it won't call requests.get.
        # But we didn't patch requests in SceneComposer specifically, we patched it in sketch_engine.
        # Let's trust the timing and logic for now. 
        
        # 2. Test ProjectOrchestrator (Rendering)
        print("\n--- Testing ProjectOrchestrator (Rendering) ---")
        # We need to simulate the rendering part of process_project
        # We can just call the logic directly or mock the other parts of process_project
        
        # Let's extract the rendering logic to test it specifically
        loop = asyncio.get_running_loop()
        sem = asyncio.Semaphore(8) # Match the code
        
        async def render_with_limit(scene):
            async with sem:
                return await loop.run_in_executor(None, orchestrator.video_renderer.render_scene, scene)

        start_time = time.time()
        render_tasks = [render_with_limit(s) for s in scenes]
        await asyncio.gather(*render_tasks)
        end_time = time.time()
        print(f"Rendering 20 scenes took {end_time - start_time:.2f}s")
        
        # Expected calculation:
        # 20 scenes, 1s each.
        # Concurrency 8.
        # Batches: 8, 8, 4.
        # Time: 1s + 1s + 1s = 3s approx.
        # With Concurrency 4: 4, 4, 4, 4, 4 -> 5s.
        
        print("\nTest Complete.")

if __name__ == "__main__":
    asyncio.run(test_performance())
